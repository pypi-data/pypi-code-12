# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from execution import Execution
from parameters import Parameters
from eureqa.utils.modulefiles import module_path

import json
import tempfile
import zipfile
import os
import io

class AnalysisTemplate(object):
    """Represents an analysis template on the server.

    :param dict body: Class metadata as dictionary
    :param Eureqa eureqa: A eureqa connection

    :var str `~eureqa.analysis_templates.analysis_template.name`: The name of the analysis template.
    :var str `~eureqa.analysis_templates.analysis_template.description`: The description of the analysis template.
    :var str `~eureqa.analysis_templates.analysis_template.icon_url`: The url of the icon for the analysis template.
    :var list `~eureqa.analysis_templates.analysis_template.parameters`: The list of parameters for the analysis template.
    """

    def __init__(self, body, eureqa):
        """For internal use only"""
        self._icon_url = body['icon_url']
        self._eureqa = eureqa
        self._body = body

    @property
    def _id(self):
        return self._body['id']
    # No setter -- don't change the ID; it's provided and opaque.
    # Also a private member.

    @property
    def name(self):
        """ Analysis Template's name """
        return self._body['name']
    @name.setter
    def name(self, val):
        self._body['name'] = val
        self._update_template()

    @property
    def description(self):
        """ Analysis Template's extended description """
        return self._body['description']
    @description.setter
    def description(self, val):
        self._body['description'] = val
        self._update_template()

    @property
    def parameters(self):
        """ Parameters object representing this template """
        return Parameters._from_json(self._body)
    @parameters.setter
    def parameters(self, val):
        if val is not None:
            self._body.update(val if isinstance(val, dict) else val._to_json())
        else:
            self._body['parameters'] = []
        self._update_template()

    def _update_template(self):
        endpoint = '/analysis_templates/%s' % (self._id)
        self._eureqa._session.report_progress('Updating analysis template: \'%s\'.' % (self._id))
        new_body = self._eureqa._session.execute(endpoint, 'POST', self._body)
        new_instance = self.__class__(new_body, self._eureqa)
        self.__dict__ = new_instance.__dict__

    def delete(self):
        """Delete the analysis template."""
        self._eureqa._session.report_progress('Deleting analysis_template: \'%s\'.' % self._id)
        self._eureqa._session.execute('/analysis_templates/%s' % (self._id), 'DELETE')

    def execute(self, values):
        """Start execution of an analysis template with given parameters.
  
        :param dict values: Analysis template settings as dictionary

        """
        request = values._to_json()
        self._eureqa._session.report_progress('Creating execution for analysis_template: \'%s\'.' % self._id)
        result = self._eureqa._session.execute('/analysis_templates/%s/executions/' % (self._id), 'POST', request)
        return Execution(result, self._id, self._eureqa)

    def get_executions(self):
        """Get all executions of the analysis template."""
        self._eureqa._session.report_progress('Getting details for executions of analysis_template: \'%s\'.' % self._id)
        results = self._eureqa._session.execute('/analysis_templates/%s/executions' % (self._id), 'GET')
        return [Execution(x, self._id, self) for x in results]

    def _get_execution(self, execution_id):
        """Get a specific execution of the analysis template.

        :param str execution_id: Execution identifier for this execution instance
        """
        self._eureqa._session.report_progress('Getting details of execution: \'%s\' of analysis_template: \'%s\'.' % (execution_id, self._id))
        result = self._eureqa._session.execute('/analysis_templates/%s/executions/%s' % (self._id, execution_id), 'GET')
        return Execution(result, self._id, self._eureqa)

    def set_module(self, main_module_name, module_fs_path, ignore_files=None, additional_modules_paths=[]):
        """Set the the python module and function that specifies the execution of this analysis template.

        :param str main_module_name: Absolute Python-import name of the main module to run.
                                   For example, "example_module".
        :param str module_fs_path: Filesystem path where the module containing the function lives.
                                 For example, "C:\\Users\\eureqa\\example_module".
                                 If omitted, this is inferred by importing the function above and
                                 taking the parent directory of the file that contains it.
        :param list[str] ignore_files: List of names of files that, if encountered, will not be uploaded to the Eureqa server.
        :param list additional_modules_paths: List of other directory names, that, if encountered, will be uploaded to the Eureqa server as well
        """

        with tempfile.TemporaryFile() as f:
            AnalysisTemplate._create_analysis_template_zip(f, main_module_name, module_fs_path, ignore_files, additional_modules_paths)
            self._eureqa._session.report_progress('Setting module for analysis_template: \'%s\' (%s).' % (self.name, self._id))
            raw_data = f.read()
            result = self._eureqa._session.execute('/analysis_templates/%s/script' % (self._id), method='POST', raw_data=raw_data)

    def get_module(self, output_filename):
        """Download the Python code which implementes this analysis template, as a .zip package,
        to the specified file on the local filesystem. Returns the main_module's name

        :param str output_filename: The filename to be used for the resulting zip file containing the analysis template code.
        """

        self._eureqa._session.report_progress('Getting module for analysis_template: \'%s\' (%s).' % (self.name, self._id))
        contents = self._eureqa._session.execute('/analysis_templates/%s/script' % (self._id), 'GET', raw_return=True)

        with open(output_filename, "wb") as f:
            f.write(contents)

        return AnalysisTemplate._get_main_module_name_from_analysis_template_zip(output_filename)

    def _to_json(self):
        body = {
            'name': self.name,
            'description': self.description,
            'icon_url': self._icon_url,
            'parameter': self.parameters._to_json()
        }
        return body

    def __str__(self):
        return json.dumps(self._to_json(), indent=4)

    @staticmethod
    def _create_analysis_template_zip(f, main_module_name, module_fs_path, ignore_files, additional_modules_paths=[]):
        """Given arguments described in set_module, packs the files and
        manifest appropriately into f as a .zip package which can be
        executed as an analysis template. Leaves f at the beginning of
        the bytes written.
        """
        with zipfile.ZipFile(f, 'w') as package_zip:
            # Create _entry.py which has a get_main_module_name() funcion
            package_zip.writestr("manifest/eureqa_main_module_name.txt",  main_module_name)
            for module_dir in [ module_fs_path ] + additional_modules_paths:
                AnalysisTemplate._add_module_to_zip(module_dir, package_zip, ignore_files)
        f.seek(0)

    @staticmethod
    def _get_main_module_name_from_analysis_template_zip(file_or_filename):
        with zipfile.ZipFile(file_or_filename, 'r') as package_zip:
            return package_zip.open('manifest/eureqa_main_module_name.txt').read()


    @staticmethod
    def _add_module_to_zip(module_dir, package_zip, _ignore_files = None):

        """Given a module object and a ZipFile object,
        write all files within the module's filesystem directory into the ZipFile."""

        if _ignore_files is None:
            _ignore_files = []

        if not os.path.isdir(module_dir):
            raise Exception("%s is not an exising directory" % (module_dir))

        containing_dir, module_name = os.path.split(module_dir)

        for dirpath, dirnames, filenames in os.walk(module_dir):
            for filename in filenames:
                if filename in _ignore_files:
                    continue
                abs_filename = os.path.join(dirpath, filename)
                assert abs_filename.startswith(containing_dir), \
                  "Internal Error:  File %s should have path starting with %s" % (repr(abs_filename), repr(containing_dir))
                relative_filename = abs_filename[len(containing_dir):]
                package_zip.write(abs_filename, relative_filename)
