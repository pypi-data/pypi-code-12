import config
import boto3
import os
import psychic_disco
array_zip = zip
from psychic_disco.util import shell, cp, zip, py_files_in_directory
from virtualenvapi.manage import VirtualEnvironment

_default_package = None

def default():
    global _default_package
    if _default_package == None:
        _default_package = DeploymentPackage()
    return _default_package

class DeploymentPackage(object):
    def __init__(self,key=None,bucket=None):
        self.s3_key = key or psychic_disco.config.default_s3_key_for_deployment_package
        self.s3_bucket = bucket or psychic_disco.config.default_s3_bucket
        self.deployed = False

    @property
    def exists(self):
        return os.path.exists(self.localpath)

    @property
    def bucket(self):
        return self.s3_bucket

    @property
    def key(self):
        return self.s3_key

    @property
    def localpath(self):
        return os.path.join(self.bundle_dir, self.s3_key)

    @property
    def bundle_dir(self):
        return ".psychic_disco"

    def s3_path(self):
        return "s3://%s/%s" % (self.s3_bucket, self.s3_key)

    def deploy(self):
        if not self.deployed:
            s3 = boto3.client('s3')
            if not self.exists:
                self.bundle()
            with open(self.localpath, "r") as f:
                s3.put_object(Body=f,Bucket=self.s3_bucket,Key=self.s3_key)
                self.deployed = True

    def _install_packages_to_environment(self, env, requirements_file):
        with open(requirements_file,'r') as f:
            for line in f:
                package_spec = line.rstrip()
                env.install(package_spec)

    def setup_virtualenv(self, target_dir):
        os.environ['LC_ALL'] = 'C'
        # Contrary to docs, this won't actually initialize anything until you either query or manipulate the installed packages
        env = VirtualEnvironment(target_dir)
        requirements_file = "requirements.txt"
        if os.path.exists(requirements_file):
            self._install_packages_to_environment(env, requirements_file)
        return env.installed_packages

    def bundle(self):
        self.setup_virtualenv(self.bundle_dir)
        dist_packages = os.path.join(self.bundle_dir,"lib/python2.7/dist-packages")
        for python_file in py_files_in_directory("."):
            destination = os.path.join(dist_packages, python_file)
            cp(python_file, destination)
        zip(dist_packages, self.localpath)
