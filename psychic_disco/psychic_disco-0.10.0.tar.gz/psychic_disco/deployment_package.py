import os
import boto3
import psychic_disco.util
from psychic_disco.util import cp, zip, py_files_in_directory
from virtualenvapi.manage import VirtualEnvironment


_default_package = None


def default():
    global _default_package
    if _default_package is None:
        _default_package = DeploymentPackage()
    return _default_package


class DeploymentPackage(object):
    def __init__(self, key=None, bucket=None):
        conf = psychic_disco.config
        self.s3_key = key or conf.default_s3_key_for_deployment_package
        self.s3_bucket = bucket or conf.default_s3_bucket
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
            self.bundle()
            with open(self.localpath, "r") as f:
                s3.put_object(Body=f, Bucket=self.s3_bucket, Key=self.s3_key)
                self.deployed = True

    def _install_packages_to_environment(self, env, requirements_file):
        with open(requirements_file, 'r') as f:
            for line in f:
                package_spec = line.rstrip()
                env.install(package_spec)

    def setup_virtualenv(self, venv_dir):
        os.environ['LC_ALL'] = 'C'
        # Contrary to docs, this won't actually initialize anything
        # until you either query or manipulate the installed packages
        env = VirtualEnvironment(venv_dir)
        requirements_file = "requirements.txt"
        if os.path.exists(requirements_file):
            self._install_packages_to_environment(env, requirements_file)
        return env.installed_packages

    def relative_path(self, path):
        return os.path.join(self.bundle_dir, path)

    @property
    def lambda_root(self):
        d = self.relative_path("lib/python2.7/dist-packages")
        if not os.path.exists(d):
            d = self.relative_path("lib/python2.7/site-packages")
        return d

    def bundle(self):
        self.setup_virtualenv(self.bundle_dir)
        for python_file in py_files_in_directory("."):
            cp(python_file, self.lambda_root)
        zip(self.lambda_root, self.localpath)
