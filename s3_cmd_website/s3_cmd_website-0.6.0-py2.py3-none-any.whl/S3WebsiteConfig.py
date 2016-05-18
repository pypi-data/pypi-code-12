import exitcodes
import helper


class S3WebsiteConfig(object):
    """
    Store the state of the s3 website configuration to be used by the functions
    """

    def __init__(self,
                 site,
                 s3_bucket,
                 cloudfront_distribution_id,
                 cloudfront_cname,
                 cloudfront_comment,
                 cloudfront_root_object,
                 cloudfront_no_access_logging,
                 s3_endpoint,
                 cache_rules,
                 maxage,
                 gzip,
                 guess_mime_type,
                 public,
                 index_file='index.html',
                 error_file='404.html',
                 ):
        self.site = site
        self.s3_bucket = s3_bucket
        self.cloudfront_distribution_id = cloudfront_distribution_id
        self.cloudfront_cname = cloudfront_cname
        self.cloudfront_comment = cloudfront_comment
        self.cloudfront_root_object = cloudfront_root_object
        self.cloudfront_no_access_logging = cloudfront_no_access_logging
        self.s3_endpoint = s3_endpoint
        self.cache_rules = cache_rules
        self.maxage = maxage
        self.gzip = gzip
        self.guess_mime_type = guess_mime_type
        self.public = public
        self.index_file = index_file
        self.error_file = error_file

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
                               cloudfront_cname=config.get(
                                   'cloudfront_cname', None),
                               cloudfront_comment=config.get(
                                   'cloudfront_comment', None),
                               cloudfront_root_object=config.get(
                                   'cloudfront_root_object', None),
                               cloudfront_no_access_logging=config.get(
                                   'cloudfront_no_access_logging', None),
                               s3_endpoint=config.get('s3_endpoint', None),
                               cache_rules=config.get('cache_rules', {}),
                               maxage=config.get('maxage', None),
                               gzip=config.get('gzip', None),
                               guess_mime_type=config.get('guess_mime_type',
                                                          None),
                               public=config.get('public', None),
                               index_file=config.get('index_file', None),
                               error_file=config.get('error_file', None),
                               )
