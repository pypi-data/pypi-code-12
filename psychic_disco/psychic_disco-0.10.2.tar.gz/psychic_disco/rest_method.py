import psychic_disco
import psychic_disco.api_gateway_config as agc


class RestMethod(object):
    def __init__(self, verb):
        self.verb = verb
        self.resource = None
        self.api = None
        self.lambda_name = None
        self.lambda_function = None

    def declare_route(self, lf):
        self.lambda_function = lf
        self.lambda_name = lf.proper_name

    def fetch_from_aws(self):
        if (self.resource is None or self.api is None):
            msg = """I cannot possibly question AWS
            without knowing my resource and api ids"""
            raise Exception(msg)
        record = agc.fetch_method(
                self.api.aws_id,
                self.resource.aws_id,
                self.verb)
        arn = record['methodIntegration']['uri']
        lambda_arn = agc.lambda_arn_from_method_integration_arn(arn)
        self.lambda_name = agc.lambda_name_from_lambda_arn(lambda_arn)

    @property
    def exists_in_aws(self):
        try:
            agc.console.get_method(
                    restApiId=self.api.aws_id,
                    resourceId=self.resource.aws_id,
                    httpMethod=self.verb)
            return True
        except:
            return False

    @property
    def integration_uri(self):
        pattern = "arn:aws:apigateway:%s:lambda:path/2015-03-31/functions/%s/invocations"  # noqa
        region = psychic_disco.config.default_aws_region
        lambda_arn = self.lambda_function.arn
        return pattern % (region, lambda_arn)

    def deploy(self):
        print "\t\tDeploying Method: %s" % self.verb
        should_put_integration = False
        if not self.exists_in_aws:
            should_put_integration = True
            agc.console.put_method(
                    restApiId=self.api.aws_id,
                    resourceId=self.resource.aws_id,
                    httpMethod=self.verb,
                    authorizationType='NONE')
        if self.lambda_function:
            self.lambda_function.deploy()
        if should_put_integration:
            agc.console.put_integration(
                    restApiId=self.api.aws_id,
                    resourceId=self.resource.aws_id,
                    httpMethod=self.verb,
                    type='AWS',
                    integrationHttpMethod=self.verb,
                    uri=self.integration_uri)
