import json
from django import forms
from django.template import Template, Context


template_content = Template("""
<br/>
<pre>{{value}}</pre>
<br/>
<table>
    <thead>
        <tr>
            <th>#</th>
            {% for k in keys %}
            <th>{{k}}</th>
            {% endfor %}
            <th></th>
        </tr>
    </thead>
    <tbody>
        {{markup|safe}}
    </tbody>
</table>
<br/>
""")


class LODWidget(forms.Widget):

    def __init__(self, keys, lines):
        """
        Initialize
            :keys
            :lines
            :seperator
        """
        self.keys = keys
        self.lines = lines
        self.separator = "__________"
        super(LODWidget, self).__init__()

    def value_from_datadict(self, data, files, name):
        """ Create JSON text from POST Dictionary """
        sep = self.separator
        keys = self.keys
        value = []
        for i in range(0, self.lines):
            dic = {k: data.get("%d%s%s" % (
                i, sep, k)) for k in keys}
            if all([not x for x in dic.values()]):
                continue
            value.append(dic)
        return json.dumps(value)

    def render(self, name, value, attrs=None):
        """ Render HTML Input for Field """
        sep = self.separator
        keys = self.keys

        value = value or []
        values = []
        for i in range(0, self.lines):
            values.append([])
            for key in keys:
                k = "%d%s%s" % (i, sep, key)
                v = value[i].get(key) or "" if i < len(value) else ""
                values[i].append((k, v))

        markup = "".join(
            """
            <tr>
                <td style="vertical-align:middle">%d</td>
                %s
            </tr>
            """ % (i+1, "".join([
                """
                <td style="vertical-align:middle">
                    <input name="%s" value="%s" />
                </td>
                """ % (k, v)
                for k, v in val]))
            for i, val in enumerate(values)
        )

        data = {
            'keys': keys,
            'value': value,
            'markup': markup
        }
        html = template_content.render(Context(data))
        return html
