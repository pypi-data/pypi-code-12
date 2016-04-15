# | Copyright 2012-2016 Karlsruhe Institute of Technology
# |
# | Licensed under the Apache License, Version 2.0 (the "License");
# | you may not use this file except in compliance with the License.
# | You may obtain a copy of the License at
# |
# |     http://www.apache.org/licenses/LICENSE-2.0
# |
# | Unless required by applicable law or agreed to in writing, software
# | distributed under the License is distributed on an "AS IS" BASIS,
# | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# | See the License for the specific language governing permissions and
# | limitations under the License.

# -*- coding: utf-8 -*-

import os, re, glob, time, tempfile

try:
	from commands import getoutput
except Exception:
	from subprocess import getoutput
from grid_control import utils
from grid_control.backends.broker import Broker
from grid_control.backends.condor_wms.processhandler import ProcessHandler
from grid_control.backends.wms import BackendError, BasicWMS, WMS
from grid_control.job_db import Job
from python_compat import ifilter, irange, izip, lmap, lzip, md5, set, sorted

# if the ssh stuff proves too hack'y: http://www.lag.net/paramiko/

# enum pseudo classes
class PoolType:
	enumTypes = ('LOCAL','SPOOL','SSH','GSISSH')
	for idx, eType in enumerate(enumTypes):
		locals()[eType] = idx

class Condor(BasicWMS):
	configSections = BasicWMS.configSections + ['condor']
	# dictionary mapping vanilla condor job status to GC job status
	# condor: U = unexpanded (never been run), H = on hold, R = running, I = idle (waiting for a machine to execute on), C = completed, and X = removed
	# 0 Unexpanded 	U -- 1	Idle 	I -- 2	Running 	R -- 3	Removed 	X -- 4	Completed 	C -- 5	Held 	H -- 6	Submission_err 	E
	# GC: 'INIT', 'SUBMITTED', 'DISABLED', 'READY', 'WAITING', 'QUEUED', 'ABORTED', 'RUNNING', 'CANCELLED', 'DONE', 'FAILED', 'SUCCESS'
	_statusMap = { # dictionary mapping vanilla condor job status to GC job status
		'0' : Job.WAITING,   # unexpanded (never been run)
		'1' : Job.SUBMITTED, # idle (waiting for a machine to execute on)
		'2' : Job.RUNNING,   # running
		'3' : Job.ABORTED,   # removed
		'4' : Job.DONE,      # completed
		'5' : Job.WAITING,   # DISABLED; on hold
		'6' : Job.FAILED,    # submit error
		'7' : Job.WAITING,   # suspended
		}
	_humanMap = { # dictionary mapping vanilla condor job status to human readable condor status
		'0' : 'Unexpanded',
		'1' : 'Idle',
		'2' : 'Running',
		'3' : 'Removed',
		'4' : 'Completed',
		'5' : 'Held',
		'6' : 'Submission_err',
		'7' : 'Suspended',
		}

# __init__: start Condor based job management
#>>config: Config class extended dictionary
	def __init__(self, config, wmsName):
		utils.vprint('Using batch system: Condor/GlideInWMS', -1)
		BasicWMS.__init__(self, config, wmsName)
		# special debug out/messages/annotations - may have noticeable effect on storage and performance!
		if config.get('debugLog', ''):
			self.debug=open(config.get('debugLog', ''),'a')
		else:
			self.debug=False
		######
		self.taskID = config.get('task id', md5(str(time.time())).hexdigest(), persistent = True) # FIXME!
		self.debugOut("""

		#############################
		Initialized Condor/GlideInWMS
		#############################
		Config: %s
		taskID: %s
		Name:   %s
		#############################

		"""%(config.getConfigName(),self.taskID,wmsName))
		# finalize config state by reading values or setting to defaults
		self.settings={
			'jdl': {
				'Universe' : config.get('Universe', 'vanilla'),
				'NotifyEmail' : config.get('NotifyEmail', ''),
				'ClassAdData' : config.getList('ClassAdData',[]),
				'JDLData' : config.getList('JDLData',[])
				},
			'pool' : {
				'hosts' : config.getList('PoolHostList',[])
				}
			}
		# prepare interfaces for local/remote/ssh pool access
		self._initPoolInterfaces(config)
		# load keys for condor pool ClassAds
		self.poolReqs  = config.getDict('poolArgs req', {})[0]
		self.poolQuery = config.getDict('poolArgs query', {})[0]
		self._formatStatusReturnQuery(config)
		# Sandbox base path where individual job data is stored, staged and returned to
		self.sandPath = config.getPath('sandbox path', config.getWorkPath('sandbox'), mustExist = False)
		# history query is faster with split files - check if and how this is used
		# default condor_history command works WITHOUT explicitly specified file
		self.historyFile = None
		if self.remoteType == PoolType.LOCAL and getoutput( self.configValExec + ' ENABLE_HISTORY_ROTATION').lower() == 'true':
			self.historyFile = getoutput( self.configValExec + ' HISTORY')
			if not os.path.isfile(self.historyFile):
				self.historyFile = None
		# broker for selecting Sites
		self.brokerSite = config.getPlugin('site broker', 'UserBroker', cls = Broker,
			tags = [self], pargs = ('sites', 'sites', self.getSites))
		self.debugFlush()

	def explainError(self, proc, code):
		if 'Keyboard interrupt raised by user' in proc.getError():
			return True
		return False

	def getSites(self):
		return self.settings['pool']['hosts']

	def debugOut(self,message,timestamp=True,newline=True):
		if self.debug:
			if newline and timestamp:
				self.debug.write('[%s] >> %s\n' % (time.asctime(),message))
			elif newline:
				self.debug.write('%s\n' % message)
			elif timestamp:
				self.debug.write('%s' % message)
			else:
				self.debug.write(message)
	def debugPool(self,timestamp=True,newline=True):
		if self.debug:
			self.debugOut(self.Pool.LoggedExecute('echo ', "'pool check'" ).cmd, timestamp, newline)
	def debugFlush(self):
		if self.debug:
			self.debug.flush()
			os.fsync(self.debug.fileno())

# overwrite for check/submit/fetch intervals
	def getTimings(self):
		if self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH:
			return utils.Result(waitOnIdle = 30, waitBetweenSteps = 5)
		elif self.remoteType == PoolType.SPOOL:
			return utils.Result(waitOnIdle = 60, waitBetweenSteps = 10)
		else:
			return utils.Result(waitOnIdle = 20, waitBetweenSteps = 5)

# getSandbox: return path to sandbox for a specific job or basepath
	def getSandboxPath(self, jobNum=''):
		sandpath = os.path.join(self.sandPath, str(jobNum), '' )
		if not os.path.exists(sandpath):
			try:
				os.makedirs(sandpath)
			except Exception:
				raise BackendError('Error accessing or creating sandbox directory:\n	%s' % sandpath)
		return sandpath

# getWorkdirPath: return path to condor output dir for a specific job or basepath
	def getWorkdirPath(self, jobNum=''):
		# local and spool make condor access the local sandbox directly
		if self.remoteType == PoolType.LOCAL or self.remoteType == PoolType.SPOOL:
			return self.getSandboxPath(jobNum)
		# ssh and gsissh require a remote working directory
		else:
			remotePath = os.path.join( self.poolWorkDir, 'GCRemote.work.TaskID.' + self.taskID, str(jobNum), '' )
			mkdirProcess = self.Pool.LoggedExecute('mkdir -p', remotePath )
			self.debugOut('Getting Workdir Nmr: %s Dir: %s - retcode %s' % (jobNum,remotePath,mkdirProcess.wait()))
			if mkdirProcess.wait()==0:
				return remotePath
			else:
				if self.explainError(mkdirProcess, mkdirProcess.wait()):
					pass
				else:
					mkdirProcess.logError(self.errorLog)
					raise BackendError("Error accessing or creating remote working directory!\n%s" % remotePath)


# getJobsOutput: retrieve task output files from sandbox directory
#>>wmsJobIdList: list of (wmsID, JobNum) tuples
	def _getJobsOutput(self, wmsJobIdList):
		if not len(wmsJobIdList):
			raise StopIteration
		self.debugOut("Started retrieving: %s" % set(lzip(*wmsJobIdList)[0]))

		activity = utils.ActivityLog('retrieving job outputs')
		for wmsId, jobNum in wmsJobIdList:
			sandpath = self.getSandboxPath(jobNum)
			if sandpath is None:
				yield (jobNum, None)
				continue
			# when working with a remote spool schedd, tell condor to return files
			if self.remoteType == PoolType.SPOOL:
				transferProcess = self.Pool.LoggedExecute(self.transferExec, '%(jobID)s' % {"jobID" : self._splitId(wmsId) })
				if transferProcess.wait() != 0:
					if self.explainError(transferProcess, transferProcess.wait()):
						pass
					else:
						transferProcess.logError(self.errorLog)
			# when working with a remote [gsi]ssh schedd, manually return files
			elif self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH:
				transferProcess = self.Pool.LoggedCopyFromRemote( self.getWorkdirPath(jobNum), self.getSandboxPath())
				if transferProcess.wait() != 0:
					if self.explainError(transferProcess, transferProcess.wait()):
						pass
					else:
						transferProcess.logError(self.errorLog)
				# clean up remote working directory
				cleanupProcess = self.Pool.LoggedExecute('rm -rf %s' % self.getWorkdirPath(jobNum) )
				self.debugOut("Cleaning up remote workdir: JobID %s\n	%s"%(jobNum,cleanupProcess.cmd))
				if cleanupProcess.wait() != 0:
					if self.explainError(cleanupProcess, cleanupProcess.wait()):
						pass
					else:
						cleanupProcess.logError(self.errorLog)
			yield (jobNum, sandpath)
		# clean up if necessary
		self._tidyUpWorkingDirectory()
		self.debugFlush()


# cancelJobs: remove jobs from queue and yield (wmsID, jobNum) of cancelled jobs
#>>wmsJobIdList: list of (wmsID, JobNum) tuples
	def cancelJobs(self, wmsJobIdList):
		if len(wmsJobIdList) == 0:
			raise StopIteration
		self.debugOut("Started canceling: %s" % set(lzip(*wmsJobIdList)[0]))
		self.debugPool()

		wmsIdList=list(self._getRawIDs(wmsJobIdList))
		wmsIdArgument = " ".join(wmsIdList)
		wmsToJobMap = dict(wmsJobIdList)

		activity = utils.ActivityLog('cancelling jobs')
		cancelProcess = self.Pool.LoggedExecute(self.cancelExec, '%(jobIDs)s' % {"jobIDs" : wmsIdArgument })

		# check if canceling actually worked
		for cancelReturnLine in cancelProcess.iter():
			if ( cancelReturnLine!= '\n' ) and ( 'marked for removal' in cancelReturnLine ):
				try:
					wmsID=cancelReturnLine.split()[1]
					wmsIdList.remove(wmsID)
					wmsID=self._createId(wmsID)
					jobNum=wmsToJobMap[wmsID]
					yield ( jobNum, wmsID)
				except KeyError:	# mismatch in GC<->Condor mapping
					self._log.error('Error with canceled condor job %s', wmsID)
					self._log.error('\tCondor IDs: %s', wmsIdList)
					self._log.error('\tProcess message: %s', cancelProcess.getMessage())
					raise BackendError('Error while cancelling job %s' % wmsID)
			# clean up remote work dir
			if self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH:
				cleanupProcess = self.Pool.LoggedExecute('rm -rf %s' % self.getWorkdirPath(jobNum) )
				self.debugOut("Cleaning up remote workdir:\n	" + cleanupProcess.cmd)
				if cleanupProcess.wait() != 0:
					if self.explainError(cleanupProcess, cleanupProcess.wait()):
						pass
					else:
						cleanupProcess.logError(self.errorLog)

		retCode = cancelProcess.wait()
		if retCode != 0:
			if self.explainError(cancelProcess, retCode):
				pass
			else:
				cancelProcess.logError(self.errorLog)
		# clean up if necessary
		self._tidyUpWorkingDirectory()
		self.debugFlush()


# _reviseWorkingDirectory: check remote working directories and clean up when needed
	def _tidyUpWorkingDirectory(self,forceCleanup=False):
		# active remote submission should clean up when no jobs remain
		if self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH:
			self.debugOut("Revising remote working directory for cleanup. Forced CleanUp: %s" % forceCleanup)
			activity = utils.ActivityLog('revising remote work directory')
			# check whether there are any remote working directories remaining
			checkProcess = self.Pool.LoggedExecute('find %s -maxdepth 1 -type d | wc -l' % self.getWorkdirPath() )
			try:
				if forceCleanup or ( int(checkProcess.getOutput()) <= 1 ):
					cleanupProcess = self.Pool.LoggedExecute('rm -rf %s' % self.getWorkdirPath() )
					if cleanupProcess.wait()!=0:
						if self.explainError(cleanupProcess, cleanupProcess.wait()):
							return
						cleanupProcess.logError(self.errorLog)
						raise BackendError('Cleanup process %s returned: %s' % (cleanupProcess.cmd, cleanupProcess.getMessage()))
			except Exception:
				self._log.warning('There might be some junk data left in: %s @ %s', self.getWorkdirPath(), self.Pool.getDomain())
				raise BackendError('Unable to clean up remote working directory')

# checkJobs: Check status of jobs and yield (jobNum, wmsID, status, other data)
#>>wmsJobIdList: list of (wmsID, JobNum) tuples
	def checkJobs(self, wmsJobIdList):
		if len(wmsJobIdList) == 0:
			raise StopIteration
		self.debugOut('Started checking: %s' % set(lzip(*wmsJobIdList)[0]))
		self.debugPool()

		wmsIdList=list(self._getRawIDs(wmsJobIdList))
		wmsIdArgument = ' '.join(wmsIdList)
		wmsToJobMap = dict(wmsJobIdList)

		activity = utils.ActivityLog('fetching job status')
		statusProcess = self.Pool.LoggedExecute(self.statusExec, '%(format)s %(jobIDs)s' % {"jobIDs" : wmsIdArgument, "format" : self.statusReturnFormat })
		activity.finish()

		activity = utils.ActivityLog('checking job status')
		# process all lines of the status executable output
		utils.vprint('querrying condor_q', 2)
		for statusReturnLine in statusProcess.iter():
			try:
				# test if wmsID job was requested, then extact data and remove from check list
				if statusReturnLine.split()[0] in wmsIdList:
					( jobID, wmsID, status, jobinfo ) = self._statusReturnLineRead(statusReturnLine)
					wmsIdList.remove(wmsID)
					yield ( jobID, self._createId(wmsID), status, jobinfo )
			except Exception:
				raise BackendError('Error reading job status info:\n%s' % statusReturnLine)

		# cleanup after final yield
		retCode = statusProcess.wait()
		if retCode != 0:
			if self.explainError(statusProcess, retCode):
				pass
			else:
				statusProcess.logError(self.errorLog, brief=True)
		activity.finish()

		self.debugOut("Remaining after condor_q: %s" % wmsIdList)
		# jobs not in queue have either succeeded or failed - both is considered 'Done' for GC
		# if no additional information is required, consider everything we couldn't find as done
		if retCode == 0:
			for wmsID in list(wmsIdList):
				wmsIdList.remove(wmsID)
				wmsID=self._createId(wmsID)
				yield ( wmsToJobMap[wmsID], wmsID, Job.DONE, {} )
		# TODO: querry log on properly configured pool
		# querying the history can be SLOW! only do when necessary and possible
		if False and len(wmsIdList) > 0 and self.remoteType != PoolType.SPOOL:
			utils.vprint('querrying condor_history', 2)
			# querying the history can be VERY slow! Only do so bit by bit if possible
			if self.historyFile:
				historyList = sorted([ "-f "+ file for file in ifilter(os.path.isfile, glob.glob(self.historyFile+"*")) ])
			else:
				historyList=[""]
			# query the history file by file until no more jobs need updating
			for historyFile in historyList:
				if len(wmsIdList) > 0:
					statusArgs = '%(fileQuery)s %(format)s %(jobIDs)s' % {"fileQuery": historyFile, "jobIDs" : " ", "format" : self.statusReturnFormat}
					statusProcess = self.Pool.LoggedExecute(self.historyExec, statusArgs)
					for statusReturnLine in statusProcess.iter():
						# test if line starts with a number and was requested
						try:
							# test if wmsID job was requested, then extact data and remove from check list
							if statusReturnLine.split()[0] in wmsIdList:
								( jobID, wmsID, status, jobinfo ) = self._statusReturnLineRead(statusReturnLine)
								wmsIdList.remove(wmsID)
								yield ( jobID, self._createId(wmsID), status, jobinfo )
						except Exception:
							raise BackendError('Error reading job status info:\n%s' % statusReturnLine)

					# cleanup after final yield
					retCode = statusProcess.wait()
					if retCode != 0:
						if self.explainError(statusProcess, retCode):
							pass
						else:
							statusProcess.logError(self.errorLog, brief=True)
		self.debugFlush()


	# helper: process output line from call to condor_q or condor_history
	#>>line: output from condor_q or condor_history
	def _statusReturnLineRead(self,line):
		try:
			statusReturnValues = line.split()
			# transform output string to dictionary
			jobinfo = dict(izip(self.statusReturnKeys, statusReturnValues))
			# extract GC and WMS ID, check for consistency
			jobID,wmsID=jobinfo['GCID@WMSID'].split('@')
			if (wmsID != jobinfo['wmsid']):
				raise BackendError("Critical! Unable to match jobs in queue! \n CondorID: %s	Expected: %s \n%s" % ( jobinfo['wmsid'], wmsID, line ))
			jobinfo['jobid']=int(jobID)
			del jobinfo['GCID@WMSID']
			# extract Host and Queue data
			if "@" in jobinfo["RemoteHost"]:
				jobinfo['dest'] = jobinfo["RemoteHost"].split("@")[1] + ': /' + jobinfo.get("Queue","")
			else:
				jobinfo['dest'] = jobinfo["RemoteHost"]
			del jobinfo["RemoteHost"]
			if "Queue" in jobinfo:
				del jobinfo["Queue"]
			# convert status to appropriate format
			status = self._statusMap[jobinfo['status']]
			jobinfo['status'] = self._humanMap[jobinfo['status']]
			return ( jobinfo['jobid'], jobinfo['wmsid'], status, jobinfo )
		except Exception:
			raise BackendError('Error reading job info:\n%s' % line)


# submitJobs: Submit a number of jobs and yield (jobNum, WMS ID, other data) sequentially
#	GC handles most job data by sending a batch file setting up the environment and executing/monitoring the actual job
#>>jobNum: internal ID of the Job
#	JobNum is linked to the actual *task* here
	def submitJobs(self, jobNumListFull, module):
		submitBatch=25
		for index in irange(0, len(jobNumListFull), submitBatch):
			jobNumList=jobNumListFull[index:index+submitBatch]
			self.debugOut("\nStarted submitting: %s" % jobNumList)
			self.debugPool()
			# get the full job config path and basename
			def _getJobCFG(jobNum):
				return os.path.join(self.getSandboxPath(jobNum), 'job_%d.var' % jobNum), 'job_%d.var' % jobNum
			activity = utils.ActivityLog('preparing jobs')
			# construct a temporary JDL for this batch of jobs
			jdlDescriptor, jdlFilePath = tempfile.mkstemp(suffix='.jdl')
			jdlSubmitPath = jdlFilePath
			self.debugOut("Writing temporary jdl to: "+jdlSubmitPath)
			try:
				data = self.makeJDLdata(jobNumList, module)
				utils.safeWrite(os.fdopen(jdlDescriptor, 'w'), data)
			except Exception:
				utils.removeFiles([jdlFilePath])
				raise BackendError('Could not write jdl data to %s.' % jdlFilePath)

			# create the _jobconfig.sh file containing the actual data
			for jobNum in jobNumList:
				try:
					self._writeJobConfig(_getJobCFG(jobNum)[0], jobNum, module, {})
				except Exception:
					raise BackendError('Could not write _jobconfig data for %s.' % jobNum)

			self.debugOut("Copying to remote")
			# copy infiles to ssh/gsissh remote pool if required
			if self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH:
				activity = utils.ActivityLog('preparing remote scheduler')
				self.debugOut("Copying to sandbox")
				workdirBase = self.getWorkdirPath()
				# TODO: check whether shared remote files already exist and copy otherwise
				for fileDescr, fileSource, fileTarget in self._getSandboxFilesIn(module):
					copyProcess = self.Pool.LoggedCopyToRemote(fileSource, os.path.join(workdirBase, fileTarget))
					if copyProcess.wait() != 0:
						if self.explainError(copyProcess, copyProcess.wait()):
							pass
						else:
							copyProcess.logError(self.errorLog, brief=True)
					self.debugFlush()
				# copy job config files
				self.debugOut("Copying job configs")
				for jobNum in jobNumList:
					fileSource, fileTarget = _getJobCFG(jobNum)
					copyProcess = self.Pool.LoggedCopyToRemote(fileSource, os.path.join(self.getWorkdirPath(jobNum), fileTarget))
					if copyProcess.wait() != 0:
						if self.explainError(copyProcess, copyProcess.wait()):
							pass
						else:
							copyProcess.logError(self.errorLog, brief=True)
					self.debugFlush()
				# copy jdl
				self.debugOut("Copying jdl")
				jdlSubmitPath = os.path.join(workdirBase, os.path.basename(jdlFilePath))
				copyProcess = self.Pool.LoggedCopyToRemote(jdlFilePath, jdlSubmitPath )
				if copyProcess.wait() != 0:
					if self.explainError(copyProcess, copyProcess.wait()):
						pass
					else:
						copyProcess.logError(self.errorLog, brief=True)
				self.debugFlush()
				# copy proxy
				for authFile in self._token.getAuthFiles():
					self.debugOut("Copying proxy")
					copyProcess = self.Pool.LoggedCopyToRemote(authFile, os.path.join(self.getWorkdirPath(), os.path.basename(authFile)))
					if copyProcess.wait() != 0:
						if self.explainError(copyProcess, copyProcess.wait()):
							pass
						else:
							copyProcess.logError(self.errorLog, brief=True)
					self.debugFlush()


			self.debugOut("Starting jobs")
			try:
				# submit all jobs simultaneously and temporarily store verbose (ClassAdd) output
				activity = utils.ActivityLog('queuing jobs at scheduler')
				proc = self.Pool.LoggedExecute(self.submitExec, ' -verbose %(JDL)s' % { "JDL": jdlSubmitPath })

				self.debugOut("AAAAA")
				# extract the Condor ID (WMS ID) of the jobs from output ClassAds
				wmsJobIdList = []
				for line in proc.iter():
					if "GridControl_GCIDtoWMSID" in line:
						GCWMSID=line.split('=')[1].strip(' "\n').split('@')
						GCID,WMSID=int(GCWMSID[0]),GCWMSID[1].strip()
						# Condor creates a default job then overwrites settings on any subsequent job - i.e. skip every second, but better be sure
						if ( not wmsJobIdList ) or ( GCID not in lzip(*wmsJobIdList)[0] ):
							wmsJobIdList.append((self._createId(WMSID),GCID))
					if "GridControl_GCtoWMSID" in line:
						self.debugOut("o : %s" % line)
						self.debugOut("o : %s" % wmsJobIdList)

				retCode = proc.wait()
				activity.finish()
				if (retCode != 0) or ( len(wmsJobIdList) < len(jobNumList) ):
					if self.explainError(proc, retCode):
						pass
					else:
						utils.eprint("Submitted %4d jobs of %4d expected" % (len(wmsJobIdList),len(jobNumList)))
						proc.logError(self.errorLog, jdl = jdlFilePath)
			finally:
				utils.removeFiles([jdlFilePath])
			self.debugOut("Done Submitting")

			# yield the (jobNum, WMS ID, other data) of each job successively
			for index in irange(len(wmsJobIdList)):
				yield (wmsJobIdList[index][1], wmsJobIdList[index][0], {} )
			self.debugOut("Yielded submitted job")
			self.debugFlush()

# makeJDL: create a JDL file's *content* specifying job data for several Jobs
#	GridControl handles job data (executable, environment etc) via batch files which are pre-placed in the sandbox refered to by the JDL
#>>jobNumList: List of jobNums for which to define tasks in this JDL
	def makeJDLdata(self, jobNumList, module):
		self.debugOut("VVVVV")
		self.debugOut("Started preparing: %s " % jobNumList)
		# resolve file paths for different pool types
		# handle gc executable separately
		gcExec, transferFiles = "",[]
		if self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH:
			for description, source, target in self._getSandboxFilesIn(module):
				if 'gc-run.sh' in target:
					gcExec=os.path.join(self.getWorkdirPath(), target)
				else:
					transferFiles.append(os.path.join(self.getWorkdirPath(), target))
		else:
			for description, source, target in self._getSandboxFilesIn(module):
				if 'gc-run.sh' in source:
					gcExec = source
				else:
					transferFiles.append(source)

		self.debugOut("o Creating Header")
		# header for all jobs
		remove_cond = '( JobStatus == 5 && HoldReasonCode != 16 )' # cancel held jobs - ignore spooling ones
		jdlData = [
			'Universe   = ' + self.settings["jdl"]["Universe"],
			'Executable = ' + gcExec,
			'notify_user = ' + self.settings["jdl"]["NotifyEmail"],
			'Log = ' + os.path.join(self.getWorkdirPath(), "GC_Condor.%s.log") % self.taskID,
			'should_transfer_files = YES',
			'when_to_transfer_output = ON_EXIT',
			'periodic_remove = ( %s )' % remove_cond,
		]
		# properly inject any information retrieval keys into ClassAds - regular attributes do not need injecting
		for key in self.poolQuery.values():
			# is this a match string? '+JOB_GLIDEIN_Entry_Name = "$$(GLIDEIN_Entry_Name:Unknown)"'
			# -> MATCH_GLIDEIN_Entry_Name = "CMS_T2_DE_RWTH_grid-ce2" && MATCH_EXP_JOB_GLIDEIN_Entry_Name = "CMS_T2_DE_RWTH_grid-ce2"
			matchKey=re.match("(?:MATCH_EXP_JOB_|MATCH_|JOB_)(.*)",key).groups()[0]
			if matchKey:
				inject='+JOB_%s = "$$(%s:Unknown)"' % (matchKey,matchKey)
				jdlData.append(inject)
				self.debugOut("  o Injected: %s " % inject)

		if self.remoteType == PoolType.SPOOL:
			# remote submissal requires job data to stay active until retrieved
			jdlData.extend("leave_in_queue = (JobStatus == 4) && ((StageOutFinish =?= UNDEFINED) || (StageOutFinish == 0))",
			# Condor should not attempt to assign to local user
			'+Owner=UNDEFINED')
		for authFile in self._token.getAuthFiles():
			if not (self.remoteType == PoolType.SSH or self.remoteType == PoolType.GSISSH):
				jdlData.append("x509userproxy = %s" % authFile)
			else:
				jdlData.append("x509userproxy = %s" % os.path.join(self.getWorkdirPath(), os.path.basename(authFile)))
			self.debugOut("  o Added Proxy")
		for line in self.settings["jdl"]["ClassAdData"]:
			jdlData.append( '+' + line )
		for line in self.settings["jdl"]["JDLData"]:
			jdlData.append( line )

		self.debugOut("o Creating Job Data")
		# job specific data
		for jobNum in jobNumList:
			self.debugOut("  o Adding Job %s" % jobNum)
			workdir = self.getWorkdirPath(jobNum)
			output_files = ",".join([target for (desc, src, target) in self._getSandboxFilesOut(module) if ((src != 'gc.stdout') and (src != 'gc.stderr'))])
			jdlData.extend([
				# store matching Grid-Control and Condor ID
				'+GridControl_GCtoWMSID = "%s@$(Cluster).$(Process)"' % module.getDescription(jobNum).jobName,
				'+GridControl_GCIDtoWMSID = "%s@$(Cluster).$(Process)"' % jobNum,
				# publish the WMS id for Dashboard
				'environment = CONDOR_WMS_DASHID=https://%s:/$(Cluster).$(Process)' % self.wmsName,
				# condor doesn"t execute the job directly. actual job data, files and arguments are accessed by the GC scripts (but need to be copied to the worker)
				'transfer_input_files = ' + ",".join(transferFiles + [os.path.join(workdir, 'job_%d.var' % jobNum)]),
				# only copy important files +++ stdout and stderr get remapped but transferred automatically, so don't request them as they would not be found
				'transfer_output_files = ' + output_files,
				'initialdir = ' + workdir,
				'Output = ' + os.path.join(workdir, "gc.stdout"),
				'Error = '  + os.path.join(workdir, "gc.stderr"),
				'arguments = %s '  % jobNum
				])
			jdlData.extend( self._getFormattedRequirements(jobNum, module) )
			jdlData.append('Queue\n')

		# combine JDL and add line breaks
		jdlData = [ line + '\n' for line in jdlData]
		self.debugOut("o Finished JDL")
		self.debugOut("AAAAA")
		self.debugFlush()
		return jdlData

	# helper for converting GC requirements to Condor requirements
	def _getFormattedRequirements(self, jobNum, task):
		jdlReq=[]
		# get requirements from task and broker WMS sites
		reqs = self.brokerSite.brokerAdd(task.getRequirements(jobNum), WMS.SITES)
		for reqType, reqValue in reqs:

			if reqType == WMS.SITES:
				(refuseSites, desireSites) = utils.splitBlackWhiteList(reqValue[1])
				#(blacklist, whitelist) = utils.splitBlackWhiteList(reqValue[1])
				## sites matching regular expression requirements
				#refuseRegx=[ site for site in self._siteMap.keys()
				# if True in [ re.search(bexpr.lower(),siteDescript.lower()) is not None for siteDescript in _siteMap[site] for bexpr in blacklist ] ]
				#desireRegx=[ site for site in self._siteMap.keys()
				# if True in [ re.search(bexpr.lower(),siteDescript.lower()) is not None for siteDescript in _siteMap[site] for bexpr in whitelist ] ]
				## sites specifically matched
				#refuseSite=[ site for site in self._siteMap.keys() if site.lower() in ap(lambda req: req.lower(), blacklist) ]
				#desireSite=[ site for site in self._siteMap.keys() if site.lower() in ap(lambda req: req.lower(), whitelist) ]
				## sites to actually match; refusing takes precedence over desiring, specific takes precedence over expression
				#refuseSites=set(refuseSite).union(set(refuseRegx))
				#desireSites=set(desireSite).union(set(desireRegx)-set(refuseRegx))-set(refuseSite)

				if "blacklistSite" in self.poolReqs:
					jdlReq.append( self.poolReqs["blacklistSite"] + ' = ' + '"' + ','.join(refuseSites)  + '"' )
				if "whitelistSite" in self.poolReqs:
					jdlReq.append( self.poolReqs["whitelistSite"] + ' = ' + '"' + ','.join(desireSites)  + '"' )

			elif reqType == WMS.WALLTIME:
				if ("walltimeMin" in self.poolReqs) and reqValue > 0:
					jdlReq.append('%s = %d' % (self.poolReqs["walltimeMin"], reqValue))

			elif reqType == WMS.STORAGE:
				if ("requestSEs" in self.poolReqs):
					jdlReq.append( self.poolReqs["requestSEs"] + ' = ' + '"' + ','.join(reqValue) + '"' )
				#append unused requirements to JDL for debugging

			elif self.debug:
				self.debugOut("reqType: %s  reqValue: %s"%(reqType,reqValue))
				self.debugFlush()
				jdlReq.append('# Unused Requirement:')
				jdlReq.append('# Type: %s' % reqType )
				jdlReq.append('# Type: %s' % reqValue )

			#TODO::: GLIDEIN_REQUIRE_GLEXEC_USE, WMS.SOFTWARE, WMS.MEMORY, WMS.CPUS
		# (HPDA) file location service
		if "dataFiles" in self.poolReqs:
			# as per ``formatFileList``
			# UserMod filelists are space separated                              'File1 File2 File3'
			# CMSSW filelists are individually quoted and comma+space separated  '"File1", "File2", "File3"'
			file_list = task.getJobConfig(jobNum).get('FILE_NAMES','').strip()
			if '", "' in file_list: # CMSSW style
				file_list = file_list.strip('"').split('", "')
			else: # UserMod style
				file_list = file_list.split(' ')
			if file_list:
				arg_key = self.poolReqs["dataFiles"]
				data_file = os.path.join(self.getSandboxPath(jobNum), 'job_%d_files.txt' % jobNum)
				data_file_list = open(data_file,"w")
				try:
					data_file_list.writelines(lmap(lambda line: line + "\n", file_list))
				finally:
					data_file_list.close()
				jdlReq.append('%s = "%s"'%(arg_key, data_file))
		return jdlReq

		##
		##	Pool access functions
		##	mainly implements remote pool wrappers/interfaces

# _createStatusReturnFormat: set query strings for condor_q and condor_history based on backend state
	def _formatStatusReturnQuery(self, config):
		self.debugOut("Formatting Status Return String")
		# return a safe request with default fallback
		def getSafeQueryKey(ClassAdKey, default='"NA"'):
			return r"IfThenElse(isUndefined(%(key)s)==False,%(key)s,%(def)s)" % { "key" : ClassAdKey, "def" : default}
		# Dummy for producing empty format specifier
		statusReturnBlank=r"""'IfThenElse(isUndefined(ClusterId),"","")'"""
		# default query string and matching dictionary keys
		statusReturnFormat= r"-format '%d.' ClusterId -format '%d ' ProcId" + \
							r" -format '%s ' GridControl_GCIDtoWMSID" + \
							r" -format '%d ' JobStatus" + \
							r" -format '%%v:' '%s'" % getSafeQueryKey("HoldReasonCode") + \
							r" -format '%%v ' '%s'" % getSafeQueryKey("HoldReasonSubCode") + \
							r""" -format '%s ' 'formatTime(QDate,"%m/%d-%H:%M")'""" + \
							r""" -format '%s ' 'formatTime(CompletionDate,"%m/%d-%H:%M")'""" + \
							r""" -format '%s ' 'IfThenElse(isUndefined(RemoteHost)==False,RemoteHost,IfThenElse(isUndefined(LastRemoteHost)==False,LastRemoteHost,"NA"))'"""
		statusReturnKeys = ["wmsid", "GCID@WMSID", "status", "holdreason", "submit_time", "completion_time", "RemoteHost"]
		# add pool specific query arguments
		for queryKey, queryArg in self.poolQuery.items():
			statusReturnFormat+=r" -format '%%v' '%s'" % getSafeQueryKey(queryArg)
			statusReturnKeys.append(queryKey)
		# end query string line
		statusReturnFormat+=r" -format '%%s\n' %s" % statusReturnBlank
		self.statusReturnFormat=statusReturnFormat
		self.statusReturnKeys=statusReturnKeys
		self.debugOut("statusReturnKeys: %s" % ",".join(self.statusReturnKeys))
		self.debugOut("statusReturnFormat %s" % self.statusReturnFormat)


	# remote submissal requires different access to Condor tools
	# local	: remote == ""			=> condor_q job.jdl
	# remote: remote == <pool>		=> condor_q -remote <pool> job.jdl
	# ssh	: remote == <user@pool>	=> ssh <user@pool> "condor_q job.jdl"
# _initPoolInterfaces: prepare commands and interfaces according to selected submit type
	def _initPoolInterfaces(self, config):
		# check submissal type
		self.remoteType = config.get("remote Type", "").lower()
		if self.remoteType in ["ssh"]:
			self.remoteType = PoolType.SSH
		elif self.remoteType in ["gsissh","gssh"]:
			self.remoteType = PoolType.GSISSH
		elif self.remoteType in ["spool","condor","remote"]:
			self.remoteType = PoolType.SPOOL
		else:
			self.remoteType = PoolType.LOCAL
		self.debugOut("Selected pool type: %s" % PoolType.enumTypes[self.remoteType])

		# get remote destination features
		user,sched,collector = self._getDestination(config)
		nice_user = user or "<local default>"
		nice_sched = sched or "<local default>"
		nice_collector = collector or "<local default>"
		self.debugOut("Destination:\n")
		self.debugOut("\tuser:%s @ sched:%s via collector:%s" % (nice_user, nice_sched, nice_collector))
		# prepare commands appropriate for pool type
		if self.remoteType == PoolType.LOCAL or self.remoteType == PoolType.SPOOL:
			self.user=user
			self.Pool=self.Pool=ProcessHandler.createInstance("LocalProcessHandler")
			# local and remote use condor tools installed locally - get them
			self.submitExec = utils.resolveInstallPath('condor_submit')
			self.statusExec = utils.resolveInstallPath('condor_q')
			self.historyExec = utils.resolveInstallPath('condor_history')	# completed/failed jobs are stored outside the queue
			self.cancelExec = utils.resolveInstallPath('condor_rm')
			self.transferExec = utils.resolveInstallPath('condor_transfer_data')	# submission might spool to another schedd and need to fetch output
			self.configValExec = utils.resolveInstallPath('condor_config_val')	# service is better when being able to adjust to pool settings
			if self.remoteType == PoolType.SPOOL:
				# remote requires adding instructions for accessing remote pool
				self.submitExec+= " %s %s" % (utils.QM(sched,"-remote %s"%sched,""),utils.QM(collector, "-pool %s"%collector, ""))
				self.statusExec+= " %s %s" % (utils.QM(sched,"-name %s"%sched,""),utils.QM(collector, "-pool %s"%collector, ""))
				self.historyExec = "false"	# disabled for this type
				self.cancelExec+= " %s %s" % (utils.QM(sched,"-name %s"%sched,""),utils.QM(collector, "-pool %s"%collector, ""))
				self.transferExec+= " %s %s" % (utils.QM(sched,"-name %s"%sched,""),utils.QM(collector, "-pool %s"%collector, ""))
		else:
			# ssh type instructions are passed to the remote host via regular ssh/gsissh
			host="%s%s"%(utils.QM(user,"%s@" % user,""), sched)
			if self.remoteType == PoolType.SSH:
				self.Pool=ProcessHandler.createInstance("SSHProcessHandler",remoteHost=host , sshLink=config.getWorkPath(".ssh", self.wmsName+host ) )
			else:
				self.Pool=ProcessHandler.createInstance("GSISSHProcessHandler",remoteHost=host , sshLink=config.getWorkPath(".gsissh", self.wmsName+host ) )
			# ssh type instructions rely on commands being available on remote pool
			self.submitExec = 'condor_submit'
			self.statusExec = 'condor_q'
			self.historyExec = 'condor_history'
			self.cancelExec = 'condor_rm'
			self.transferExec = "false"	# disabled for this type
			self.configValExec = 'condor_config_val'
			# test availability of commands
			testProcess=self.Pool.LoggedExecute("condor_version")
			self.debugOut("*** Testing remote connectivity:\n%s"%testProcess.cmd)
			if testProcess.wait()!=0:
				testProcess.logError(self.errorLog)
				raise BackendError("Failed to access remote Condor tools! The pool you are submitting to is very likely not configured properly.")
			# get initial workdir on remote pool
			if config.get("remote workdir", ''):
				uName=self.Pool.LoggedExecute("whoami").getOutput().strip()
				self.poolWorkDir=os.path.join(config.get("remote workdir", ''), uName)
				pwdProcess=self.Pool.LoggedExecute("mkdir -p %s" % self.poolWorkDir )
			else:
				pwdProcess=self.Pool.LoggedExecute("pwd")
				self.poolWorkDir=pwdProcess.getOutput().strip()
			if pwdProcess.wait()!=0:
				self._log.critical("Code: %d\nOutput Message: %s\nError Message: %s", pwdProcess.wait(), pwdProcess.getOutput(), pwdProcess.getError())
				raise BackendError("Failed to determine, create or verify base work directory on remote host")

#_getDestination: read user/sched/collector from config
	def _getDestination(self,config):
		splitDest = [ item.strip() for item in config.get('remote Dest', '@').split('@') ]
		user = config.get('remote User', '').strip()
		if len(splitDest)==1:
			return utils.QM(user,user,None),splitDest[0],None
		elif len(splitDest)==2:
			return utils.QM(user,user,None),splitDest[0],splitDest[1]
		else:
			self._log.warning('Could not parse Configuration setting "remote Dest"!')
			self._log.warning('Expected: [<sched>|<sched>@|<sched>@<collector>]')
			self._log.warning('Found: %s', config.get('remote Dest', '@'))
			raise BackendError('Could not parse submit destination')
