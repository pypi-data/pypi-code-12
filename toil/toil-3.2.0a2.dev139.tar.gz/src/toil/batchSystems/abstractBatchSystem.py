# Copyright (C) 2015 UCSC Computational Genomics Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import absolute_import
from collections import namedtuple
from toil.common import Toil
import os
import shutil

# A class containing the information required for worker cleanup on shutdown of the batch system.
WorkerCleanupInfo = namedtuple('WorkerCleanupInfo', (
    # A path to the value of config.workDir (where the cache would go)
    'workDir',
    # The value of config.workflowID (used to identify files specific to this workflow)
    'workflowID',
    # The value of the cleanWorkDir flag
    'cleanWorkDir'))


class AbstractBatchSystem:
    """
    An abstract (as far as python currently allows) base class
    to represent the interface the batch system must provide to the toil.
    """

    @staticmethod
    def supportsHotDeployment():
        """
        Whether this batch system supports hot deployment of the user script and toil itself. If it does,
        the __init__ method will have to accept two optional parameters in addition to the declared ones: userScript
        and toilDistribution. Both will be instances of toil.common.HotDeployedResource that represent the user
        script and a source tarball (sdist) of toil respectively.

        :return: boolean indicating whether hot deployment is supported by the batch system
        :rtype: bool
        """
        return False

    def __init__(self, config, maxCores, maxMemory, maxDisk):
        """
        Initializes initial state of the object

        :param toil.common.Config config: object is setup by the toilSetup script and
          has configuration parameters for the jobtree. You can add code
          to that script to get parameters for your batch system.

        :param float maxCores: the maximum number of cores the batch system can
          request for any one job

        :param int maxMemory: the maximum amount of memory the batch system can
          request for any one job, in bytes

        :param int maxDisk: the maximum amount of disk space the batch system can
          request for any one job, in bytes
        """
        self.config = config
        self.maxCores = maxCores
        self.maxMemory = maxMemory
        self.maxDisk = maxDisk
        self.environment = {}
        """
        :type: dict[str,str]
        """
        self.workerCleanupInfo = WorkerCleanupInfo(workDir=self.config.workDir,
                                                   workflowID=self.config.workflowID,
                                                   cleanWorkDir=self.config.cleanWorkDir)

    def checkResourceRequest(self, memory, cores, disk):
        """
        Check resource request is not greater than that available or allowed.

        :param int memory: amount of memory being requested, in bytes

        :param float cores: number of cores being requested

        :param int disk: amount of disk space being requested, in bytes

        :raise InsufficientSystemResources: raised when a resource is requested in an amount
          greater than allowed
        """
        assert memory is not None
        assert disk is not None
        assert cores is not None
        if cores > self.maxCores:
            raise InsufficientSystemResources('cores', cores, self.maxCores)
        if memory > self.maxMemory:
            raise InsufficientSystemResources('memory', memory, self.maxMemory)
        if disk > self.maxDisk:
            raise InsufficientSystemResources('disk', disk, self.maxDisk)

    def issueBatchJob(self, command, memory, cores, disk):
        """
        Issues a job with the specified command to the batch system and returns a unique jobID.

        :param str command: the string to run as a command,

        :param int memory: int giving the number of bytes of memory the job needs to run

        :param float cores: the number of cores needed for the job

        :param int disk: int giving the number of bytes of disk space the job needs to run

        :return: a unique jobID that can be used to reference the newly issued job
        :rtype: str
        """
        raise NotImplementedError('Abstract method: issueBatchJob')

    def killBatchJobs(self, jobIDs):
        """
        Kills the given job IDs.

        :param list[str] jobIDs: list of jobIDs to kill
        """
        raise NotImplementedError('Abstract method: killBatchJobs')

    # FIXME: Return value should be a set (then also fix the tests)

    def getIssuedBatchJobIDs(self):
        """
        Gets all currently issued jobs

        :return: A list of jobs (as jobIDs) currently issued (may be running, or may be
          waiting to be run). Despite the result being a list, the ordering should not
          be depended upon.
        :rtype: list[str]
        """
        raise NotImplementedError('Abstract method: getIssuedBatchJobIDs')

    def getRunningBatchJobIDs(self):
        """
        Gets a map of jobs as jobIDs that are currently running (not just waiting)
        and how long they have been running, in seconds.

        :return: dictionary with currently running jobID keys and how many seconds they have
          been running as the value
        :rtype: dict[str,float]
        """
        raise NotImplementedError('Abstract method: getRunningBatchJobIDs')

    def getUpdatedBatchJob(self, maxWait):
        """
        Gets a job that has updated its status, according to the batch system.

        :param int maxWait: gives the number of seconds to block
          waiting to find an updated job.

        :return: If a result is available returns tuple of form (jobID, exitValue)
          else it returns None. Does not return jobs that were killed.
        :rtype: (str, int)|None
        """
        raise NotImplementedError('Abstract method: getUpdatedBatchJob')

    def shutdown(self):
        """
        Called at the completion of a toil invocation.
        Should cleanly terminate all worker threads.
        """
        raise NotImplementedError('Abstract Method: shutdown')

    def setEnv(self, name, value=None):
        """
        Set an environment variable for the worker process before it is launched. The worker
        process will typically inherit the environment of the machine it is running on but this
        method makes it possible to override specific variables in that inherited environment
        before the worker is launched. Note that this mechanism is different to the one used by
        the worker internally to set up the environment of a job. A call to this method affects
        all jobs issued after this method returns. Note to implementors: This means that you
        would typically need to copy the variables before enqueuing a job.

        If no value is provided it will be looked up from the current environment.

        NB: Only the Mesos and single-machine batch systems support passing environment
        variables. On other batch systems, this method has no effect. See
        https://github.com/BD2KGenomics/toil/issues/547.

        :param str name: the environment variable to be set on the worker.

        :param str value: if given, the environment variable given by name will be set to this value.
          if None, the variable's current value will be used as the value on the worker

        :raise RuntimeError: if value is None and the name cannot be found in the environment
        """
        if value is None:
            try:
                value = os.environ[name]
            except KeyError:
                raise RuntimeError("%s does not exist in current environment", name)
        self.environment[name] = value

    @classmethod
    def getRescueBatchJobFrequency(cls):
        """
        Gets the period of time to wait (floating point, in seconds) between checking for
        missing/overlong jobs.

        :return: time in seconds to wait in between checking for lost jobs
        :rtype: int
        """
        raise NotImplementedError('Abstract method: getRescueBatchJobFrequency')

    def _getResultsFileName(self, toilPath):
        """
        Get a path for the batch systems to store results. GridEngine
        and LSF currently use this.
        """
        return os.path.join(toilPath, "results.txt")

    @staticmethod
    def supportsWorkerCleanup():
        """
        Indicates whether this batch system invokes :meth:`workerCleanup` after the last job for
        a particular workflow invocation finishes. Note that the term *worker* refers to an
        entire node, not just a worker process. A worker process may run more than one job
        sequentially, and more than one concurrent worker process may exist on a worker node,
        for the same workflow. The batch system is said to *shut down* after the last worker
        process terminates.

        :return: boolean indication whether the batch system supports worker cleanup
        :rtype: bool
        """
        return False

    @staticmethod
    def workerCleanup(info):
        """
        Cleans up the worker node on batch system shutdown. Also see :meth:`supportsWorkerCleanup`.

        :param WorkerCleanupInfo info: A named tuple consisting of all the relevant information
               for cleaning up the worker.
        """
        assert isinstance(info, WorkerCleanupInfo)
        workflowDir = Toil.getWorkflowDir(info.workflowID, info.workDir)
        if (info.cleanWorkDir == 'always'
            or info.cleanWorkDir in ('onSuccess', 'onError') and os.listdir(workflowDir) == []):
            shutil.rmtree(workflowDir)


class InsufficientSystemResources(Exception):
    """
    To be raised when a job requests more of a particular resource than is either currently allowed
    or avaliable
    """
    def __init__(self, resource, requested, available):
        """
        Creates an instance of this exception that indicates which resource is insufficient for current
        demands, as well as the amount requested and amount actually available.

        :param str resource: string representing the resource type

        :param int requested: the amount of the particular resource requested that resulted in this exception

        :param int available: amount of the particular resource actually available
        """
        self.requested = requested
        self.available = available
        self.resource = resource

    def __str__(self):
        return 'Requesting more {} than available. Requested: {}, Available: {}' \
               ''.format(self.resource, self.requested, self.available)
