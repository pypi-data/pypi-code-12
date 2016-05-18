#!/usr/bin/env python2.7
"""
UCSC Computational Genomics Lab ADAM Variants Pipeline
Author: Audrey Musselman-Brown
Affiliation: UC Santa Cruz Genomics Institute

Please see the README.md in the same directory

Toil pipeline for converting variants in VCF format to ADAM 

                        Tree structure of ADAM pipeline
                                       0 
                                       |++(1)
                                       2 --> 4 --> 5 --> 6
                                        ++(3)

0 = Start Master
1 = Master Service
2 = Start Workers
3 = Worker Service
4 = Download Data
5 = ADAM Convert
6 = Upload Data

================================================================================
:Dependencies
docker          - apt-get install docker (or 'docker.io' for linux)
toil            - pip install --pre toil
"""

import argparse
import logging
import multiprocessing
import os
import subprocess
import sys
import time
from toil.job import Job

SPARK_MASTER_PORT = "7077"
HDFS_MASTER_PORT = "8020"

log = logging.getLogger(__name__)

# JOB FUNCTIONS

# copied from bwa_alignment.docker_call
def docker_call(work_dir,
                tool_parameters,
                tool,
                java_opts=None,
                outfile=None,
                sudo=False,
                docker_parameters=None,
                check_output=False,
                no_rm=False):
    """
    Makes subprocess call of a command to a docker container.

    tool_parameters: list   An array of the parameters to be passed to the tool
    tool: str               Name of the Docker image to be used (e.g. quay.io/ucsc_cgl/samtools)
    java_opts: str          Optional commands to pass to a java jar execution. (e.g. '-Xmx15G')
    outfile: file           Filehandle that stderr will be passed to
    sudo: bool              If the user wants the docker command executed as sudo
    """
    rm = '--rm'
    if no_rm:
        rm = ''

    base_docker_call = ('docker run %s --log-driver=none -v %s:/data' % (rm, work_dir)).split()

    log.warn("Calling docker with %s." % " ".join(base_docker_call))

    if sudo:
        base_docker_call = ['sudo'] + base_docker_call
    if java_opts:
        base_docker_call = base_docker_call + ['-e', 'JAVA_OPTS={}'.format(java_opts)]
    if docker_parameters:
        base_docker_call = base_docker_call + docker_parameters

    log.warn("Calling docker with %s." % " ".join(base_docker_call))
    sys.stderr.write( "Calling docker with %s\n" % " ".join(base_docker_call))

    try:
        if outfile:
            subprocess.check_call(base_docker_call + [tool] + tool_parameters, stdout=outfile)
        else:
            if check_output:
                return subprocess.check_output(base_docker_call + [tool] + tool_parameters)
            else:
                subprocess.check_call(base_docker_call + [tool] + tool_parameters)

    except subprocess.CalledProcessError:
        raise RuntimeError('docker command returned a non-zero exit status. Check error logs.')
    except OSError:
        raise RuntimeError('docker not found on system. Install on all nodes.')


# remainder of this file copied with modification from adam_pipeline/spark_toil_script.py
def start_master(job, inputs):
    """
    Start the master service.
    """
    log.warn("master job\n")
    masterIP = job.addService(MasterService(inputs['sudo'], "%s G" % inputs['executorMemory']))
    job.addChildJobFn(start_workers, masterIP, inputs)


def start_workers(job, masterIP, inputs):
    """
    Start the worker services.
    """
    log.warn("workers job\n")
    for i in range(inputs['numWorkers']):
        job.addService(WorkerService(masterIP, inputs['sudo'], "%s G" % inputs['executorMemory']))
    job.addFollowOnJobFn(download_data, masterIP, inputs, memory = "%s G" % inputs['driverMemory'])


def call_conductor(masterIP, inputs, src, dst):
    """
    Invoke the conductor container.
    """
    docker_call(no_rm = True,
                work_dir = os.getcwd(),
                tool = "quay.io/ucsc_cgl/conductor",
                docker_parameters = ["--net=host"],
                tool_parameters = ["--master", "spark://"+masterIP+":"+SPARK_MASTER_PORT,
                 "--conf", "spark.driver.memory=%sg" % inputs["driverMemory"],
                 "--conf", "spark.executor.memory=%sg" % inputs["executorMemory"],
                 "--", "-C", src, dst],
                sudo = inputs['sudo'])


def call_adam(masterIP, inputs, arguments):
    """
    Call adam-submit via docker.
    """
    params = []
    default_params = ["--master", ("spark://%s:%s" % (masterIP, SPARK_MASTER_PORT)), 
                      "--conf", ("spark.driver.memory=%sg" % inputs["driverMemory"]),
                      "--conf", ("spark.executor.memory=%sg" % inputs["executorMemory"]),
                      "--conf", ("spark.hadoop.fs.default.name=hdfs://%s:%s" % (masterIP, HDFS_MASTER_PORT)),
                      "--"]
    try:
        params = default_params + arguments
    except:
        log.error("parms: %s" % str(default_params))
        log.error("args: %s" % str(arguments))
        raise

    docker_call(no_rm = True,
                work_dir = os.getcwd(),
                tool = "quay.io/ucsc_cgl/adam:cd6ef41", 
                docker_parameters = ["--net=host"],
                tool_parameters = params,
                sudo = inputs['sudo'])


def remove_file(masterIP, filename):
    """
    Remove the given file from hdfs with master at the given IP address
    """
    containerID = subprocess.check_output(["ssh", "-o", "StrictHostKeyChecking=no", masterIP, "docker", "ps", \
                                           "|", "grep", "apache-hadoop-master", "|", "awk", "'{print $1}'"])[:-1]
    subprocess.check_call(["ssh", "-o", "StrictHostKeyChecking=no", masterIP, "docker", "exec", containerID, \
                           "/opt/apache-hadoop/bin/hdfs", "dfs", "-rm", "-r", "/"+filename])


def download_data(job, masterIP, inputs):
    """
    Download input data files from s3.
    """
    log.warn("download data\n")

    vcfFileSystem, vcfPath = inputs['vcfName'].split('://')
    vcfName = vcfPath.split('/')[-1]
    hdfsVcf = "hdfs://"+masterIP+":"+HDFS_MASTER_PORT+"/"+vcfName

    call_conductor(masterIP, inputs, inputs['vcfName'], hdfsVcf)

    job.addFollowOnJobFn(adam_convert, masterIP, hdfsVcf, inputs, memory = "%s G" % inputs['driverMemory'])


def adam_convert(job, masterIP, inFile, snpFile, inputs):
    """
    Convert input VCF file into ADAM format.
    """
    log.warn("adam convert\n")

    adamFile = ".".join(os.path.splitext(inFile)[:-1])+".adam"
    
    call_adam(masterIP,
              inputs,
              ["vcf2adam", 
               inFile, adamFile])
              
    inFileName = inFile.split("/")[-1]
    remove_file(masterIP, inFileName)
 
    job.addFollowOnJobFn(upload_data, masterIP, adamFile, inputs, memory = "%s G" % inputs['driverMemory'])


def upload_data(job, masterIP, hdfsName, inputs):
    """
    Upload file hdfsName from hdfs to s3.
    """
    log.warn("write data\n")

    fileSystem, path = hdfsName.split('://')
    nameOnly = path.split('/')[-1]
    
    uploadName = "%s/%s" % (inputs['outDir'], nameOnly)
    if inputs['suffix']:
        uploadName = uploadName.replace('.adam', '%s.adam' % inputs['suffix'])

    call_conductor(masterIP, inputs, hdfsName, uploadName, memory = "%s G" % inputs['driverMemory'])
    
# SERVICE CLASSES

class MasterService(Job.Service):

    def __init__(self, sudo, memory):

        self.sudo = sudo
        self.memory = memory
        self.cores = multiprocessing.cpu_count()
        Job.Service.__init__(self, memory = self.memory, cores = self.cores)

    def start(self):
        """
        Start spark and hdfs master containers
        """
        log.warn("start masters\n")
        
        if (os.uname()[0] == "Darwin"):
            machine = subprocess.check_output(["docker-machine", "ls"]).split("\n")[1].split()[0]
            self.IP = subprocess.check_output(["docker-machine", "ip", machine]).strip().rstrip()
        else:
            self.IP = subprocess.check_output(["hostname", "-f",])[:-1]

        self.sparkContainerID = docker_call(no_rm = True,
                                            work_dir = os.getcwd(),
                                            tool = "quay.io/ucsc_cgl/apache-spark-master:1.5.2",
                                            docker_parameters = ["--net=host",
                                                                 "-d",
                                                                 "-v", "/mnt/ephemeral/:/ephemeral/:rw",
                                                                 "-e", "SPARK_MASTER_IP="+self.IP,
                                                                 "-e", "SPARK_LOCAL_DIRS=/ephemeral/spark/local",
                                                                 "-e", "SPARK_WORKER_DIR=/ephemeral/spark/work"],
                                            tool_parameters = [],
                                            sudo = self.sudo,
                                            check_output = True)[:-1]
        self.hdfsContainerID = docker_call(no_rm = True,
                                           work_dir = os.getcwd(),
                                           tool = "quay.io/ucsc_cgl/apache-hadoop-master:2.6.2",
                                           docker_parameters = ["--net=host",
                                                                "-d"],
                                           tool_parameters = [self.IP],
                                           sudo = self.sudo,
                                           check_output = True)[:-1]
        return self.IP

    def stop(self):
        """
        Stop and remove spark and hdfs master containers
        """
        log.warn("stop masters\n")
        
        sudo = []
        if self.sudo:
            sudo = ["sudo"]

        subprocess.call(sudo + ["docker", "exec", self.sparkContainerID, "rm", "-r", "/ephemeral/spark"])
        subprocess.call(sudo + ["docker", "stop", self.sparkContainerID])
        subprocess.call(sudo + ["docker", "rm", self.sparkContainerID])
        subprocess.call(sudo + ["docker", "stop", self.hdfsContainerID])
        subprocess.call(sudo + ["docker", "rm", self.hdfsContainerID])

        return

                
class WorkerService(Job.Service):
    
    def __init__(self, masterIP, sudo, memory):
        self.masterIP = masterIP
        self.sudo = sudo
        self.memory = memory
        self.cores = multiprocessing.cpu_count()
        Job.Service.__init__(self, memory = self.memory, cores = self.cores)

    def start(self):
        """
        Start spark and hdfs worker containers
        """
        log.warn("start workers\n")

        self.sparkContainerID = docker_call(no_rm = True,
                                            work_dir = os.getcwd(),
                                            tool = "quay.io/ucsc_cgl/apache-spark-worker:1.5.2",
                                            docker_parameters = ["--net=host", 
                                                                 "-d",
                                                                 "-v", "/mnt/ephemeral/:/ephemeral/:rw",
                                                                 "-e", "\"SPARK_MASTER_IP="+self.masterIP+":"+SPARK_MASTER_PORT+"\"",
                                                                 "-e", "SPARK_LOCAL_DIRS=/ephemeral/spark/local",
                                                                 "-e", "SPARK_WORKER_DIR=/ephemeral/spark/work"],
                                            tool_parameters = [self.masterIP+":"+SPARK_MASTER_PORT],
                                            sudo = self.sudo,
                                            check_output = True)[:-1]
        
        self.hdfsContainerID = docker_call(no_rm = True,
                                           work_dir = os.getcwd(),
                                           tool = "quay.io/ucsc_cgl/apache-hadoop-worker:2.6.2",
                                           docker_parameters = ["--net=host",
                                                                "-d",
                                                                "-v", "/mnt/ephemeral/:/ephemeral/:rw"],
                                           tool_parameters = [self.masterIP],
                                           sudo = self.sudo,
                                           check_output = True)[:-1]
        
        # fake do/while to check if HDFS is up
        hdfs_down = True
        retries = 0
        while hdfs_down and (retries < 5):

            sys.stderr.write("Sleeping 30 seconds before checking HDFS startup.")
            time.sleep(30)
            clusterID = ""
            try:
                clusterID = subprocess.check_output(["docker",
                                                     "exec",
                                                     self.hdfsContainerID,
                                                     "grep",
                                                     "clusterID",
                                                     "-R",
                                                     "/opt/apache-hadoop/logs"])
            except:
                # grep returns a non-zero exit code if the pattern is not found
                # we expect to not find the pattern, so a non-zero code is OK
                pass

            if "Incompatible" in clusterID:
                sys.stderr.write("Hadoop Datanode failed to start with: %s" % clusterID)
                sys.stderr.write("Retrying container startup, retry #%d." % retries)
                retries += 1

                sys.stderr.write("Removing ephemeral hdfs directory.")
                subprocess.check_call(["docker",
                                       "exec",
                                       self.hdfsContainerID,
                                       "rm",
                                       "-rf",
                                       "/ephemeral/hdfs"])

                sys.stderr.write("Killing container %s." % self.hdfsContainerID)
                subprocess.check_call(["docker",
                                       "kill",
                                       self.hdfsContainerID])

                # todo: this is copied code. clean up!
                sys.stderr.write("Restarting datanode.")
                self.hdfsContainerID = docker_call(no_rm = True,
                                                   work_dir = os.getcwd(),
                                                   tool = "quay.io/ucsc_cgl/apache-hadoop-worker:2.6.2",
                                                   docker_parameters = ["--net=host",
                                                                        "-d",
                                                                        "-v", "/mnt/ephemeral/:/ephemeral/:rw"],
                                                   tool_parameters = [self.masterIP],
                                                   sudo = self.sudo,
                                                   check_output = True)[:-1]

            else:
                sys.stderr.write("HDFS datanode started up OK!")
                hdfs_down = False

        if retries >= 5:
            raise RuntimeError("Failed %d times trying to start HDFS datanode." % retries)
                                   
        return

    def stop(self):
        """
        Stop spark and hdfs worker containers
        """
        log.warn("stop workers\n")

        sudo = []
        if self.sudo:
            sudo = ['sudo']

        subprocess.call(sudo + ["docker", "exec", self.sparkContainerID, "rm", "-r", "/ephemeral/spark"])
        subprocess.call(sudo + ["docker", "stop", self.sparkContainerID])
        subprocess.call(sudo + ["docker", "rm", self.sparkContainerID])
        subprocess.call(sudo + ["docker", "exec", self.hdfsContainerID, "rm", "-r", "/ephemeral/hdfs"])
        subprocess.call(sudo + ["docker", "stop", self.hdfsContainerID])
        subprocess.call(sudo + ["docker", "rm", self.hdfsContainerID])

        return


def build_parser():

    parser = argparse.ArgumentParser()

    parser.add_argument('-i', '--input_file_name', required = True,
                        help = "The full s3 url of the input VCF file")
    parser.add_argument('-n', '--num_nodes', type = int, required = True,
                        help = 'Number of nodes to use')
    parser.add_argument('-o', '--output_directory', required = True,
                        help = 's3 directory url in which to place output files')
    parser.add_argument('-x', '--suffix', default="",
                        help='additional suffix, if any')
    parser.add_argument('-d', '--driver_memory', required = True,
                        help = 'Amount of memory to allocate for Spark Driver.')
    parser.add_argument('-q', '--executor_memory', required = True,
                        help = 'Amount of memory to allocate per Spark Executor.')
    parser.add_argument('-u', '--sudo',
                        dest='sudo', action='store_true',
                        help='Docker usually needs sudo to execute '
                        'locally, but not''when running Mesos '
                        'or when a member of a Docker group.')

    return parser


def main(args):
    
    parser = build_parser()
    Job.Runner.addToilOptions(parser)
    options = parser.parse_args()

    if options.num_nodes <= 1:
        raise ValueError("--num_nodes allocates one Spark/HDFS master and n-1 workers, and thus must be greater than 1. %d was passed." % options.num_nodes)

    inputs = {'numWorkers': options.num_nodes - 1,
              'outDir':     options.output_directory,
              'vcfName':    options.input_file_name,
              'driverMemory': options.driver_memory,
              'executorMemory': options.executor_memory,
              'sudo': options.sudo,
              'suffix': options.suffix}

    Job.Runner.startToil(Job.wrapJobFn(start_master, inputs), options)

if __name__=="__main__":
    sys.exit(main(sys.argv[1:]))
