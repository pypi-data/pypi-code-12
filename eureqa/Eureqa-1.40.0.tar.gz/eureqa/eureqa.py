# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
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

from analysis import Analysis
from analysis_templates import AnalysisTemplate
from data_source import DataSource
from organization import _Organization
from search import Search
from search_templates import SearchTemplates
from session import _Session, Http404Exception
from solution import Solution
from error_metric import ErrorMetrics

class Eureqa:
    """Represents an interface to the Eureqa server. All interactions with the server should start from this class.

    :var ~eureqa.Solution `~eureqa.Eureqa.search_templates`: Provides access to predefined search templates.

    :param str url: The URL of the eureqa server. It should be the same URL as used to access the web UI.
    :param str user_name:
        The user name to login into the server. It should be the same user name as used to login into the web UI.
        If the user name is not provided and the interactive mode is enabled, the user name will be requested
        during the script execution.
    :param str password:
        The password.
        If the password is not provided and the interactive mode is enabled, the password will be requested
        during the script execution.
    :param str organization:
        The name of the organization.
        All request to API will be executed in the context of this organization.
        If the organization name is not provided and the user is assigned to only one organization, then that
        organization will be used by default.
    :param bool interactive_mode:
        If set to True, enables interactive mode. In the interactive mode the script will request user name, password,
        and potentially other information if it is not provided or incorrect.
        If set to False (default), throws an exception if a login or password is incorrect, or if the two factor
        authentication is enabled. This is the default behaviour which prevents scripts from indefinitely waiting
        for the user input if they are executed automatically by a CRON job or a Windows Scheduler task.
    :param bool save_credentials:
        If set to True, saves user name and password to the '.eureqa_passwd' in the user directory. If after that any
        script on the same machine is trying to connect to the same server and does not provide credentials, it reuses
        the saved credentials.
        It does not save a temporary password when the two-factor authentication is enabled.
        When used with the two-factor authentication, the interactive_mode parameter should also be enabled.
    :param bool verify_ssl_certificate:
        If set to False will not verify SSL certificate authenticity while connecting to Eureqa.
    :param bool verify_version:
        If set to False will allow to use Python API library with incompatible version of Eureqa.
        Should only be used for the diagnostic purpose.
    :param bool verbose:
        If set to True will print to the console the detailed information for each request to the server.
        Should only be used for the diagnostic purpose.
    :param int retries:  The number of attempts to establish a session before an Exception is raised
    :param str session_key: The session identifier.  
    :param int timeout_seconds:
        The HTTP connection and transmission timeout. Any request to Eureqa API will abort with an exception if it
        takes more time, than set in the timeout, to either connect to the server or to receive a next data package.
    :param str key:
        Authentication key.  Provide either this field or `password`.

    :raise Exception: If the authentication fails or cannot be completed.
    """

    # note that if session_key is present, we don't actually try to do
    # a login and instead use the existing session key directly

    from api_version import API_VERSION

    def __init__(self, url='https://rds.nutonian.com', user_name=None, password=None,
                 organization=None,
                 interactive_mode=False, save_credentials=False,
                 verify_ssl_certificate=True, verify_version=True, verbose=False, retries=5,
                 session_key=None, timeout_seconds=None, key=None):
        self._session = _Session(url, user_name, password, key, verbose, save_credentials, organization,
                                verify_ssl_certificate, retries, timeout_seconds, session_key, interactive_mode)
        if verify_version:
            self._verify_version()

    def create_data_source(self, name, file_or_path, _hidden = False):
        """Creates a new data source on the server.

        Uploads data and performs all the same preproccessing that happen
        when a new data set is created through the UI.

        :param str name: A name for the new data source.
        :param str file_or_path:
            A path to a local CSV file with data for the data source.
            It can be either an absolute path or path relative to the current working directory.
            Alternatively, a Python file-like object.

        :return: A DataSource object that represents a newly created data source on the server.
        :rtype: ~eureqa.DataSource
        :raise Exception: If data source with the same name already exists and get_existing is set to False.
        """

        # Trying to open before creating data source. So if there is a problem
        # with opening this file, a data source will not be even created.
        # Otherwise if there is a problem later, the call will terminal with exception
        # and an empty data source will stay in the system.

        if isinstance(file_or_path, basestring):
            f = open(file_or_path, 'rb')
            f.close()

        self._session.report_progress('Creating datasource: \'%s\'.' % name)
        result = self._session.execute('/fxp/datasources', 'POST', args={'datasource_name': name, 'hidden': _hidden})
        data_source = DataSource(self, result)

        if isinstance(file_or_path, basestring):
            f = open(file_or_path, 'rb')
            file_path = file_or_path
        else:
            f = file_or_path
            file_path = getattr(file_or_path, 'name', str(file_or_path))

        try:
            self._session.report_progress('Uploading file: \'%s\' to datasource: \'%s\'.' % (file_path, data_source._data_source_id))
            self._session.execute('/fxp/datasources/%s/data' % data_source._data_source_id, 'POST', files={'file': f})
            return self.get_data_source_by_id(data_source._data_source_id)
        finally:
            if isinstance(file_or_path, basestring):
                f.close()

    def get_all_data_sources(self):
        """Get all data sources from the server

        :return: A list of DataSource objects for all data sources within the organization.
        """

        self._session.report_progress('Getting details for all datasource')
        data_source_bodies = self._session.execute('/fxp/datasources', 'GET')
        data_sources = []
        for data_source_body in data_source_bodies:
            data_sources.append(DataSource(self, data_source_body))
        return data_sources

    def get_data_source(self, data_source_name):
        """Get a data source by its name.

        Searches on the server for a data source given its name.

        :param str data_source_name: The name of the data source.
        :return: A DataSource object if such data source exists, otherwise None.
        :rtype: ~eureqa.DataSource
        """

        self._session.report_progress('Getting details for datasource with name: \'%s\'.' % data_source_name)
        data_source_bodies = self._session.execute('/fxp/datasources', 'GET')
        data_sources = []
        for data_source_body in data_source_bodies:
            datasource = DataSource(self, data_source_body)
            if datasource.name == data_source_name:
                data_sources.append(datasource)
        if len(data_sources) == 0:
            message = 'Unknown datasource_name: \'%s\'' % data_source_name
            raise Exception(message)
        elif len(data_sources) == 1:
            return data_sources[0]
        else:
            ids = ''
            for data_source in data_sources:
                ids += data_source._data_source_id + " "
            message = 'Multiple data sources exist with the name: \'%s\' Use get_data_source_by_id instead with one of the following ids: %s' %(data_source_name, ids)
            raise Exception(message)

    def get_data_source_by_id(self, data_source_id):
        """Get a data source by its id.

        Searches on the server for a data source given its id.

        :param str data_source_id: The ID of the data source.
        :return: A DataSource object if such data source exists, otherwise None.
        :rtype: ~eureqa.DataSource
        """
        self._session.report_progress('Getting details for datasource with id: \'%s\'.' % data_source_id)
        data_source_body = self._session.execute('/fxp/datasources/%s' % data_source_id, 'GET')
        return DataSource(self, data_source_body)

    def create_analysis(self, name, description=None):
        """Creates an analysis.

        :param str name: The analysis name. It will be used as the Analysis title.
        :param str description: The analysis description.
        :return: An Analysis object that represents a newly created data source on the server.
        :rtype: ~eureqa.Analysis
        """

        body = {'analysis_name': name, 'analysis_metadata': {'description': description}, 'items': []}
        self._session.report_progress('Creating analysis: \'%s\'.' % name)
        result = self._session.execute('/analysis', 'POST', body)
        return Analysis(result, self)

    def get_analyses(self):
        """Return the list of all analyses from the server.

        :rtype: list of :class:`~eureqa.Analysis`
        """
        self._session.report_progress('Getting details for analyses.')
        results = self._session.execute('/analysis', 'GET')
        return [Analysis(x, self) for x in results]

    def get_analysis(self, analysis_id):
        """Return a specific analysis from the server, by id

        :param str analysis_id: The id of the analysis to return
        :rtype: :class:`~eureqa.Analysis`
        """
        self._session.report_progress('Getting details for analysis: \'%s\'.' % analysis_id)
        results = self._session.execute('/analysis/%s' % analysis_id, 'GET')
        return Analysis(results, self)

    def create_analysis_template(self, name, description, parameters, icon=None):
        """ Create a new Analysis Template on the Eureqa server.

        :param str name: The analysis template's name.  Will be used to identify the template.
        :param str description: The analysis template's description.  Will be used where more space is available for an expanded description.
        :param ~eureqa.analysis_template.Parameters parameters: Object describing the parameters that a user must fill in via the UI in order to specify the template's behavior
        :param str icon: The path to an icon to use in the UI for this analysis.

        :return: An AnalysisTemplate object representing the template on the server
        :rtype: :class:`~eureqa.AnalysisTemplate`"""
        if not self._session._is_root():
            raise Exception("Analysis templates can only be modified by a root user. You are '%s'" %(self._session.user))
        body = {"name": name,
                "description": description,
                "icon_url": icon}
        body.update(parameters._to_json())
        self._session.report_progress('Creating analysis_template: %s' % name)
        result = self._session.execute('/analysis_templates', 'POST', body)
        return AnalysisTemplate(result, self)

    def get_all_analysis_templates(self):
        """Get a list of all Analysis Template objects currently available to this connection

        :rtype: list of :class:`~eureqa.AnalysisTemplate`
        """

        self._session.report_progress('Getting details for analysis_templates.')
        results = self._session.execute('/analysis_templates', 'GET')
        return [AnalysisTemplate(x, self) for x in results]

    @property
    def search_templates(self):
        """Return all Search Templates available to the current connection

        :rtype: :class:`~eureqa.SearchTemplates`
        """
        return SearchTemplates(self)

    def _get_analysis_template(self, template_id):
        self._session.report_progress('Getting details for analysis_template: \'%s\'.' % template_id)
        result = self._session.execute('/analysis_templates/%s' % template_id, 'GET')
        return AnalysisTemplate(result, self)

    def _get_analysis_template_by_name(self, template_name):
        self._session.report_progress('Finding first analysis template with name: \'%s\'.' % template_name)
        for t in self.get_all_analysis_templates():
            if (t.name == template_name):
                return t
        raise Exception("No analysis template has name '%s'" % (template_name))

    def _get_search_by_search_id(self, data_source_id, search_id):
        self._session.report_progress('Getting details for search: \'%s\' in datasource: \'%s\'.' % (search_id, data_source_id))
        endpoint = "/fxp/datasources/%s/searches/%s" % (data_source_id, search_id)
        result = self._session.execute(endpoint, 'GET')
        return Search(result, self)

    def _get_solution_by_id(self, data_source_id, search_id, solution_id):
        self._session.report_progress('Getting details for solution: \'%s\' in search: \'%s\' in datasource: \'%s\'.' % (solution_id, search_id, data_source_id))
        endpoint = "/fxp/datasources/%s/searches/%s/solutions/%s" % (data_source_id, search_id, solution_id)
        result = self._session.execute(endpoint, 'GET')
        return Solution(result, self._get_search_by_search_id(data_source_id, search_id))

    def _get_rest_endpoint_version(self):
        try:
            self._session.report_progress('Getting settings_info.')
            settings = self._session.execute('/api/v2/fxp/settings_info', 'GET')
            return settings['api_version']
        except Http404Exception:
            # The version of eeb that don't expose this endpoint will return this.
            return 0

    def _get_session_key(self):
        return self._session._get_session_key()

    def _verify_version(self):
        server_version = self._get_rest_endpoint_version()
        if Eureqa.API_VERSION != server_version:
            message = 'An incorrect version of the API library is used. ' \
                      'The server version is %s, but the library version is %s.' % (server_version, Eureqa.API_VERSION)
            raise Exception(message)

    def _create_organization(self, name):
        self._session.report_progress('Creating organization: \'%s\'.' % name)
        self._session.execute('/api/v2/organizations', 'POST', args={'name': '%s' % name})
        return _Organization(self, name)

    def _get_organization(self, id):
        self._session.report_progress('Getting organization: \'%s\'.' % id)
        self._session.execute('/api/v2/organizations/%s' % id, 'GET')
        return _Organization(self, id)

    def compute_error_metrics(self, datasource, target_variable, model_expression, template_search=None,
                              variable_options=[], row_weight="1.0", row_weight_type="uniform", _data_split="all"):
        """
        Compute the :py:class:`eureqa.error_metric.ErrorMetrics` for the specified model, against the specified target_variable

        :param DataSource datasource: DataSource to compute error against
        :param str target_variable: Variable (or expression) to compare the model to
        :param str model_expression: Model whose error is to be computed
        :param Search template_search: If specified, inherit variable options from the specified search.  Values specified in :variable_options: take precedence over values in this search; use it for finer-grained control instead of or on top of this argument.
        :param VariableOptionsDict variable_options: Override any default behavior for the specified variables.  If the data contains nulls and no null-handling policy is specified, this method will return an error. A list of :py:class:`eureqa.variable_options.VariableOptions` may also be provided.
        :param str row_weight: Expression to compute the weight of a row (how much that row contributes to the computed error)
        :param str row_weight_type: The type of expression to use to compute row weight (uniform, target_frequency, variable, or custom_expr)
        :return: The computed error metrics
        :rtype: ErrorMetrics
        """
        # '_data_split' parameter is for internal use.  Non-default valid values are 'training' and 'validation'.
        
        if isinstance(variable_options, list):
            var_options = [x._to_json() for x in variable_options]
        else:
            var_options = [x._to_json() for x in variable_options.itervalues()]
            
        args = {
            'row_weight': row_weight,
            'row_weight_type': row_weight_type,
            'lhs_expression': target_variable,
            'rhs_expression': model_expression,
            'data_type': _data_split,
            'variable_options': var_options
        }
        if template_search:
            args["search_id"] = template_search._id
        result = self._session.execute('/fxp/datasources/%s/compute_error_metric' % datasource._data_source_id, 'POST', args=args)
        metrics = ErrorMetrics()
        metrics._from_json(result)
        return metrics

    def evaluate_expression(self, datasource, expressions, template_search=None, variable_options=[], _data_split='all'):
	"""
	Evaluates the provided expression against the specified datasource.  Returns the value of the evaluated computation.

        Example:

            values = eureqa.evaluate_expression(['x','y','x^2']) # where

            values['x']   --> [1,2,3,4]

            values['y']   --> [5,6,7,8]

            values['x^2'] --> [1,4,9,16]

            data = pandas.DataFrame(values)  # convert to pandas.DataFrame

        :param DataSource datasource: DataSource to perform the computation against
        :param str expressions: If only one expression is to be evaluated, that expression.  If multiple expressions are to be evaluated, a list of those expressions.
        :param Search template_search: If specified, inherit variable options from the specified search.  Values specified in :variable_options: take precedence over values in this search; use it for finer-grained control instead of or on top of this argument.
        :param VariableOptionsDict variable_options: Override default variable options directly for particular variables.  Set interpretation of NaN values, outliers, etc.  default behavior is to make no changes to the original data.  By default, missing values are not filled; missing values in input data may result in missing values in corresponding computed values. A list of :py:class:`eureqa.variable_options.VariableOptions` may also be provided.
        """
        # '_data_split' parameter is for internal use only.  Non-default valid values are 'training' and 'validation'.

        if isinstance(expressions, basestring): expressions = [expressions]
        
        if isinstance(variable_options, list):
            var_options = [x._to_json() for x in variable_options]
        else:
            var_options = [x._to_json() for x in variable_options.itervalues()]

        # 'datasource' should be a DataSource instance.
        # Allow it to be a string too.  For internal use only.
        data_source_id = (datasource if isinstance(datasource, basestring) else datasource._data_source_id)

        endpoint = '/fxp/datasources/%s/evaluate_expression' % data_source_id

        args = {
            'expression': expressions,
            'data_type': _data_split,
            'variable_options': var_options
        }
        if template_search:
            args['search_id'] = template_search._id

        self._session.report_progress('Evaluating expression on datasource: \'%s\'.' % data_source_id)
        body = self._session.execute(endpoint, 'POST', args)
        values = {expr: [] for expr in expressions}
        for series in body['series_details']:
            used_expression = set()
            for expr, column in zip(expressions, series['values']):
                if expr not in used_expression:
                    values[expr].extend(column)
                    used_expression.add(expr)
        return values

    def _grant_user_api_access(self, username, organization, as_role="org_admin"):
        # Function is not public; API may change
        if as_role == "org_admin":
            endpoint = "/api/%(organization)s/auth/user/%(username)s/api_access"
        elif as_role == "user_admin":
            endpoint = "/api/auth/user/%(username)s/api_access/%(organization)s"

        endpoint = endpoint % { 'username': username, 'organization': organization }

        self._session.execute(endpoint, 'PUT', {})

    def _revoke_user_api_access(self, username, organization, as_role="org_admin"):
        # Function is not public; API may change
        if as_role == "org_admin":
            endpoint = "/api/%(organization)s/auth/user/%(username)s/api_access"
        elif as_role == "user_admin":
            endpoint = "/api/auth/user/%(username)s/api_access/%(organization)s"

        endpoint = endpoint % { 'username': username, 'organization': organization }

        self._session.execute(endpoint, 'DELETE', {})

    def _generate_api_key(self, key_name):
        # Function is not public; API may change
        endpoint = "/api/auth/keys"
        result = self._session.execute(endpoint, 'POST', {'name': key_name})
        return result

    def _revoke_api_key_by_id(self, key_id):
        # Function is not public; API may change
        endpoint = "/api/auth/keys/%s" % key_id
        self._session.execute(endpoint, 'DELETE', {})

    def _revoke_api_key_by_name(self, key_name):
        # Function is not public; API may change
        # get all (both) keys and then find the key_id for the key_name
        endpoint = "/api/auth/keys"
        keys = self._session.execute(endpoint, 'GET', {})
        id = next((key['id'] for key in keys if key['name'] == key_name), -1)
        ## send the -1 default if not found so that we get the same Exception as _by_id
        endpoint = "/api/auth/keys/%s" % id 
        self._session.execute(endpoint, 'DELETE', {})

    def _list_api_keys(self):
        # Function is not public; API may change
        endpoint = "/api/auth/keys"
        result = self._session.execute(endpoint, 'GET', {})
        return result


class EureqaLocal(Eureqa):
    """Represents an interface to the Eureqa Local server.
    
    Works exactly the same as :class:`~eureqa.Eureqa`, its parent class, except as documented.

    :param int instance: Instance number.  Default, 1, points to the first Eureqa launched on the machine.  The second is 2, etc.  Use this instead of the 'url' argument on the parent class.

    All constructor arguments for the :class:`~eureqa.Eureqa` class are also supported.
    """
    def __init__(self, instance = 1, *args, **kwargs):
        # Instance numbers start at 1 and are sequential integers.
        # Eureqa Local tries port 10002 initially on startup;
        # if that's busy, it walks up to 20002 in multiples of 100.
        port = 9902 + (instance*100)
        Eureqa.__init__(self, url="http://localhost:%d" % port, *args, **kwargs)
