	def {{ method.lower() }}_{{ name }}({{ arglist|join(', ') }}):
		{% if description %}'''{{ description }}'''{% endif %}
		{% if all_query_args %}
		_all_query_args = { {% for arg in all_query_args %}'{{arg.replace("'", "\\'")}}': {{arg.lower().replace('-', '_')}}, {% endfor %} }
		_query_args = {k: v for k, v in _all_query_args.items() if v != self._NO_VALUE}
		if _query_args:
			_query_string = "?" + self.queryencode(_query_args)
		else:
			_query_string = ""
		{% endif %}

		_api_endpoint = "{{prefix}}{{endpoint}}{% if all_query_args %}{querystring}{% endif %}"{% if urlargs or all_query_args %}.format({% if urlargs %}{{urlargs}}, {% endif %}{% if all_query_args %}querystring=_query_string{% endif %}){% endif %}
		{% set datamethod = method in ('PUT', 'POST') %}{% if datamethod and all_data_args %}
		_all_data_args = { {% for arg in all_data_args %}'{{arg.replace("'", "\\'")}}': {{arg.lower().replace('-', '_')}}, {% endfor %} }
		_data_args = {k: v for k, v in _all_query_args.items() if v != self._NO_VALUE}
		{% endif %}
		return self.connection.{{method}}(endpoint=_api_endpoint{% if datamethod and all_data_args %}, data=_data_args{% endif %})


