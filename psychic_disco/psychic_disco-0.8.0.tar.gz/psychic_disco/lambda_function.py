import deployment_package
import config
import boto3

console = boto3.client('lambda')
_declared_functions = []


def installed_functions():
    return [f['FunctionName'] for f in console.list_functions()['Functions']]


def declared_functions():
    return _declared_functions


class LambdaFunction(object):
    def __init__(self, func_name, module_name):
        global _declared_functions
        self.full_name = "%s.%s" % (module_name, func_name)
        _declared_functions.append(self)

    @property
    def proper_name(self):
        return self.full_name.replace('.', '-')

    def update(self, package):
        print("Updating %s" % self.proper_name)
        console.update_function_code(
                FunctionName=self.proper_name,
                S3Bucket=package.bucket,
                S3Key=package.key)

    def install(self, package):
        print("Installing %s" % self.proper_name)
        console.create_function(
                FunctionName=self.proper_name,
                Runtime="python2.7",
                Role=config.default_iam_role,
                Handler=self.full_name,
                Code={"S3Bucket": package.bucket, "S3Key": package.key})

    def deploy(self):
        package = deployment_package.default()
        package.deploy()
        if self.proper_name in installed_functions():
            self.update(package)
        else:
            self.install(package)

    def __str__(self):
        return self.proper_name
