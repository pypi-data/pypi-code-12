
main_template = """
<html>
<body>
{% for entry in entries %}
<h3><a href="{{ entry.link }}">{{ entry.title }}</a></h3>
<p>
{{ entry.summary }}
</p>
{% endfor %}
</body>
</html>
"""
