import probe.log
import pkg_resources
probe.log.read_yaml_config(pkg_resources.resource_stream(__name__, 'cfg/logging.yml'))
