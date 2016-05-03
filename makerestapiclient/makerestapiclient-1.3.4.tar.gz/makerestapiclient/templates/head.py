{% for i in imports %}
{{ i }}
{% endfor %}

class {{ classname }}(object):
	_NO_VALUE = object()

	def __init__(self, scheme, host, port, username, password, httpclass{% if httpclass %} = {{ httpclass }}{% endif %}):
		self.connection = httpclass(
			scheme=scheme,
			host=host,
			port=port,
			username=username,
			password=password,
			)
		self.urlquote = httpclass.urlquote
		self.queryencode = httpclass.queryencode

{% if withcontext %}
	def __enter__(self):
		self._old_connection = self.connection
		self.connection = self.connection.__enter__()
		return self

	def __exit__(self, type, value, traceback):
		self._old_connection.__exit__(type, value, traceback)
		self.connection = self._old_connection
		del self._old_connection
{% endif %}


