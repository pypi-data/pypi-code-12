from __future__ import absolute_import

import os

import jinja2
from jinja2.exceptions import TemplateNotFound
from jinja2.loaders import BaseLoader as Jinja2BaseLoader


# Jinja2 loader that understand django apps structure
class Jinja2AppSpecificLoader(Jinja2BaseLoader):
    """Loads templates from the file system by the given app name only.

    This is a Jinja2 loader.

    A template name should contain the python module path and the template
    name relative to that python module's templates dir in the form:

    appName.submodule:path/to/template.jinja

    dirs should be all of the regular templates dirs when an appName is not specified.

    app_dirs should be a list of the registered applications' templates dirs.

    app_dirname is the name of the dir that holds the templates within each app and defaults to 'templates'.

    encoding specifies the default encoding for the template file its self and defaults to 'utf-8'.

    
    A quick example:
    >>> loader = Jinja2AppSpecificLoader(['/path/to/django/website/templates'],['/path/to/django/website/apps/user/templates'])
    >>> loader.get_source(env,'user:list.jinja2')

    will return the template if it is found at:
    /path/to/django/website/apps/user/templates/list.jinja2
    """
    def __init__(self,dirs,app_dirs,app_dirname='templates',encoding='utf-8',only_match_filename_extensions=None):
        self.dirs=dirs
        self.app_dirs=app_dirs
        self.app_dirname=app_dirname
        self.encoding=encoding
        self.only_match_filename_extensions=only_match_filename_extensions


    def list_specific_templates(self,template):
        # return an empty list straight away if the template path doesn't end in one of our defined extensions 
        if self.only_match_filename_extensions and not any(template.endswith('.'+ext) for ext in self.only_match_filename_extensions): return []
        # split the template string into appName and templatePath
        t=template if ':' in template else ':'+template
        app_name,template_path=t.split(':',1)

        # then create a path to the app's templates dir, if an appName was given
        valid_search_path_suffix=os.path.join(*app_name.split('.'))

        template_paths=[]
        # if an appName was specified
        if valid_search_path_suffix:
            valid_search_path_suffix=os.path.join(valid_search_path_suffix,self.app_dirname)
            # only return paths in app_dirs that match the given appName
            template_paths=[os.path.normpath(os.path.join(d,template_path)) for d in self.app_dirs if d.endswith(valid_search_path_suffix)]

        else:
            # else no appName, so just search regular dirs
            template_paths=[os.path.normpath(os.path.join(d,template_path)) for d in self.dirs]

        return template_paths


    def get_source(self,environment,template):
        for tp in self.list_specific_templates(template):
            if os.path.isfile(tp):
                f=open(tp,'rb')
                try:
                    source=f.read().decode(self.encoding)
                finally:
                    f.close()

                # create an is up-to-date function
                mtime=os.path.getmtime(tp)
                def is_up_to_date():
                    try:
                        return os.path.getmtime(tp)==mtime
                    except OSError:
                        return False

                return (source,tp,is_up_to_date)
        raise TemplateNotFound(template)
