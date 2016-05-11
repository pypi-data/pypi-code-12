import exitcodes
import helper


class S3WebsiteConfig(object):
    """
    Store the state of the s3 website configuration to be used by the functions
    """

    def __init__(self, site, s3_bucket, cloudfront_distribution_id,
                 s3_endpoint, cache_rules, maxage, gzip):
        self.site = site
        self.s3_bucket = s3_bucket
        self.cloudfront_distribution_id = cloudfront_distribution_id
        self.s3_endpoint = s3_endpoint
        self.cache_rules = cache_rules
        self.maxage = maxage
        self.gzip = gzip

    @staticmethod
    def load_configuration(path, logger):
        """
        Load the configuration file and return the S3 website object

        :param path: String - Path to configuration file
        :param logger: Logger - Logger for logging events
        """
        return S3WebsiteConfig._load_configuration_from_yaml(path, logger)

    @staticmethod
    def _load_configuration_from_yaml(path, logger):
        """
        Load the configuration file based off a yaml file and return the
         S3 website object

        :param path: String - Path to configuration file
        :param logger: Logger - Logger for logging events
        """
        if not helper.file_exists(path):
            logger.error("s3_cmd_website config file not found at '%s'"
                         % path)
            return exitcodes.EX_CONFIG_FILE_NOT_FOUND

        config = helper.load_yaml(path, logger)
        if config is None:
            return None
        return S3WebsiteConfig(site=config.get('site', None),
                               s3_bucket=config.get('s3_bucket', None),
                               cloudfront_distribution_id=config.get(
                                   'cloudfront_distribution_id', None),
                               s3_endpoint=config.get('s3_endpoint', None),
                               cache_rules=config.get('cache_rules', {}),
                               maxage=config.get('maxage', None),
                               gzip=config.get('gzip', None),
                               )
