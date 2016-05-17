
import json
import hashlib
import os
import shutil
from smartlingApiSdk.UploadData import UploadData
from smartlingApiSdk.SmartlingDirective import SmartlingDirective
from smartlingApiSdk.SmartlingFileApi import \
    SmartlingFileApiFactory, \
    ProxySettings
import tempfile
import yaml

class SmarterlingError(Exception):
    """ Thrown for various errors
    """
    pass

class AttributeDict(dict):
    """ Quick dictionary that allows for getting items
        as attributes in a convenient manner
    """
    __getattr__ = lambda self, key: self.get(key, require_value=True)
    __setattr__ = dict.__setitem__
    def get(self, key, default_val=None, require_value=False):
        """ Returns a dictionary value
        """
        val = dict.get(self, key, default_val)
        if val is None and require_value:
            raise KeyError('key "%s" not found' % key)
        if isinstance(val, dict):
            return AttributeDict(val)
        return val

def sha1(s):
    """ Returns a sha1 of the given string
    """
    h = hashlib.new('sha1')
    h.update(s)
    return h.hexdigest()

def write_to_file(file_name, data):
    """ Writes data to file_name
    """
    with open(file_name, 'w') as f:
        f.write(data)

def read_from_file(file_name):
    """ Reads from a file
    """
    with open(file_name, 'r') as f:
        return f.read()

def file_uri(file_name, conf):
    """ Return the file's uri
    """
    return conf.get('uri') if conf.has_key('uri') else file_name

def get_translated_items(fapi, file_uri, use_cache, cache_dir=None):
    """ Returns the last modified from smarterling
    """
    items = None
    cache_file = os.path.join(cache_dir, sha1(file_uri)) if use_cache else None
    if use_cache and os.path.exists(cache_file):
        print("Using cache file %s for translated items for: %s" % (cache_file, file_uri))
        items = json.loads(read_from_file(cache_file))
    if not items:
        print("Downloading %s from smartling" % file_uri)
        (response, code) = fapi.last_modified(file_uri)
        items = response.data.items
        if cache_file:
            print("Caching %s to %s" % (file_uri, cache_file))
            write_to_file(cache_file, json.dumps(items))
    return items

def get_translated_file(fapi, file_uri, locale, retrieval_type, include_original_strings, use_cache, cache_dir=None):
    """ Returns a translated file from smartling
    """
    file_data = None
    cache_name = str(file_uri)+"."+str(locale)+"."+str(retrieval_type)+"."+str(include_original_strings)
    cache_file = os.path.join(cache_dir, sha1(cache_name)) if cache_dir else None

    if use_cache and os.path.exists(cache_file):
        print("Using cache file %s for %s translation file: %s" % (cache_file, locale, file_uri))
        file_data = read_from_file(cache_file)
    elif not use_cache:
        (file_data, code) = fapi.get(file_uri, locale,
            retrievalType=retrieval_type,
            includeOriginalStrings=include_original_strings)
        file_data = str(file_data).strip()
        if cache_file and code == 200 and len(file_data)>0:
            print("Chaching to %s for %s translation file: %s" % (cache_file, locale, file_uri))
            write_to_file(cache_file, file_data)
    if not file_data or len(file_data)==0:
        print("%s translation not found for %s" % (locale, file_uri))
        return None
    return file_data

def download_files(fapi, file_name, conf, use_cache, cache_dir=None):
    """ Downloads translated versions of the files
    """
    retrieval_type              = conf.get('retrieval-type', 'published')
    include_original_strings    = 'true' if conf.get('include-original-strings', False) else 'false'
    save_pattern                = conf.get('save-pattern')

    if not save_pattern:
        raise SmarterlingError("File %s doesn't have a save-pattern" % file_name)

    if cache_dir and not os.path.exists(cache_dir):
        print("Creating cache dir: %s" % (cache_dir, ))
        os.makedirs(cache_dir)

    uri = file_uri(file_name, conf)
    translated_items = get_translated_items(fapi, uri, use_cache, cache_dir=cache_dir)

    for item in translated_items:
        item                = AttributeDict(item)
        locale              = item.locale
        locale_underscore   = locale.replace("-", "_")
        locale_android_res  = locale.replace("-", "-r")
        locale_parts        = locale.split("-")
        language            = locale_parts[0]
        region              = locale_parts[1] if len(locale_parts)>1 else ""

        file_response = get_translated_file(
            fapi, file_uri(file_name, conf), locale, retrieval_type,
            include_original_strings, use_cache, cache_dir=cache_dir)

        if not file_response:
            print("%s translation not found for %s" % (item.locale, file_name))
            continue
        print("Processing %s translation for %s" % (item.locale, file_name))

        (fd, work_file) = tempfile.mkstemp()
        try:
            with open(work_file, 'w') as f:
                f.write(file_response)
        finally:
            os.close(fd)

        for filter_cmd in conf.get('filters', []):
            (fd, tmp_file) = tempfile.mkstemp()
            try :
                filter_cmd = filter_cmd.replace("{input_file}", work_file)
                filter_cmd = filter_cmd.replace("{output_file}", tmp_file)
                filter_cmd = filter_cmd.replace("{locale}", locale)
                filter_cmd = filter_cmd.replace("{locale_underscore}", locale_underscore)
                filter_cmd = filter_cmd.replace("{locale_android_res}", locale_android_res)
                filter_cmd = filter_cmd.replace("{language}", language)
                filter_cmd = filter_cmd.replace("{region}", region)
                print(" running filter: %s " % filter_cmd)
                if os.system(filter_cmd) != 0:
                    raise SmarterlingError("Non 0 exit code from filter: %s" % filter_cmd)
                shutil.move(tmp_file, work_file)
            finally:
                os.close(fd)

        if conf.has_key('save-cmd'):
            save_command = conf.get('save-cmd')
            save_command = save_command.replace("{input_file}", work_file)
            save_command = save_command.replace("{locale}", locale)
            save_command = save_command.replace("{locale_underscore}", locale_underscore)
            save_command = save_command.replace("{locale_android_res}", locale_android_res)
            save_command = save_command.replace("{language}", language)
            save_command = save_command.replace("{region}", region)
            print(" running save command: %s " % save_command)
            if os.system(save_command) != 0:
                raise SmarterlingError("Non 0 exit code from save command: %s" % save_command)

        elif conf.has_key('save-pattern'):
            save_file = conf.get('save-pattern')
            save_file = save_file.replace("{locale}", locale)
            save_file = save_file.replace("{locale_underscore}", locale_underscore)
            save_file = save_file.replace("{locale_android_res}", locale_android_res)
            save_file = save_file.replace("{language}", language)
            save_file = save_file.replace("{region}", region)
            save_dir = os.path.dirname(save_file)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            elif not os.path.isdir(save_dir):
                raise SmarterlingError("Expected %s to be a directory, but it's an existing file" % save_dir)
            print(" saving output to: %s " % save_file)
            shutil.move(work_file, save_file)

        else:
            raise SmarterlingError("no save-cmd or save-pattern for: %s" % file_name)


def upload_file(fapi, file_name, conf):
    """ Uploads a file to smartling
    """
    if not conf.has_key('file-type'):
        raise SmarterlingError("%s doesn't have a file-type" % file_name)
    print("Uploading %s to smartling" % file_name)
    data = UploadData(
        os.path.dirname(file_name)+os.sep,
        os.path.basename(file_name),
        conf.get('file-type'))
    data.setUri(file_uri(file_name, conf))
    if conf.has_key('approve-content'):
        data.setApproveContent("true" if conf.get('approve-content', True) else "false")
    if conf.has_key('callback-url'):
        data.setCallbackUrl(conf.get('callback-url'))
    for name, value in conf.get('directives', {}).items():
        data.addDirective(SmartlingDirective(name, value))
    (response, code) = fapi.upload(data)
    if code!=200:
        print(repr(response))
        raise SmarterlingError("Error uploading file: %s" % file_name)
    else:
        print("Uploaded %s, wordCount: %s, stringCount: %s" % (file_name, response.data.wordCount, response.data.stringCount))

def create_file_api(conf):
    """ Creates a SmartlingFileApi from the given config
    """
    api_key = conf.config.get('api-key', os.environ.get('SMARTLING_API_KEY'))
    project_id = conf.config.get('project-id', os.environ.get('SMARTLING_PROJECT_ID'))

    if not project_id or not api_key:
        raise SmarterlingError('config.api-key and config.project-id are required configuration items')
    proxy_settings=None
    if conf.config.has_key('proxy-settings'):
        proxy_settings = ProxySettings(
            conf.config.get('proxy-settings').get('username', ''),
            conf.config.get('proxy-settings').get('password', ''),
            conf.config.get('proxy-settings').get('host', ''),
            int(conf.config.get('proxy-settings').get('port', '80')))
    return SmartlingFileApiFactory().getSmartlingTranslationApi(
        not conf.config.get('sandbox', False),
        api_key,
        project_id,
        proxySettings=proxy_settings)

def parse_config(file_name='smarterling.config'):
    """ Parses a smarterling configuration file
    """
    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        raise SmarterlingError('Config file not found: %s' % file_name)
    try:
        contents = read_from_file(file_name)
        contents_with_environment_variables_expanded = os.path.expandvars(contents)
        return AttributeDict(yaml.load(contents_with_environment_variables_expanded))
    except Exception as e:
        raise SmarterlingError("Error paring config file: %s" % str(e))

