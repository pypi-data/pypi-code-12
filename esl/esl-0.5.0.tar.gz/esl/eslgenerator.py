# @Author: BingWu Yang <detailyang>
# @Date:   2016-04-06T21:18:58+08:00
# @Email:  detailyang@gmail.com
# @Last modified by:   detailyang
# @Last modified time: 2016-04-10T23:34:51+08:00
# @License: The MIT License (MIT)


import commands
import urllib
from jinja2 import Template

from eslast import QueryStringNode, HeaderNode, BodyNode, ValueNode, ShellNode

class ESLGenerator(object):
    def __init__(self, ast):
        self.ast = ast

    def to_curl(self):
        url = self.ast.left.url
        method = self.ast.method.name
        params = {}
        headers = {}
        body = {}
        for option in self.ast.right.options if self.ast.right else []:
            if isinstance(option.key, QueryStringNode):
                if isinstance(option.value, ValueNode):
                    params[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    params[option.key.key] = commands.getstatusoutput(option.value.value)[1]
            elif isinstance(option.key, HeaderNode):
                if isinstance(option.value, ValueNode):
                    headers[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    headers[option.key.key] = commands.getstatusoutput(option.value.value)[1]
            elif isinstance(option.key, BodyNode):
                if isinstance(option.value, ValueNode):
                    body[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    body[option.key.key] = commands.getstatusoutput(option.value.value)[1]
        if '?' in url:
            url = url + urllib.urlencode(params)
        else:
            url = url + '?' + urllib.urlencode(params)
        headers = ['-H "{k}: {v}"'.format(k=k, v=v) for k, v in headers.items()]
        body = ['-d "{k}={v}"'.format(k=k, v=v) for k, v in body.items()]
        return '''
        curl -X {method} {headers} {data} "{url}"
        '''.format(url=url, method=method, headers=" ".join(headers), data=" ".join(body))

    def to_go(self):
        url = self.ast.left.url
        method = self.ast.method.name
        params = {}
        headers = {}
        body = {}
        for option in self.ast.right.options if self.ast.right else []:
            if isinstance(option.key, QueryStringNode):
                if isinstance(option.value, ValueNode):
                    params[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    params[option.key.key] = commands.getstatusoutput(option.value.value)[1]
            elif isinstance(option.key, HeaderNode):
                if isinstance(option.value, ValueNode):
                    headers[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    headers[option.key.key] = commands.getstatusoutput(option.value.value)[1]
            elif isinstance(option.key, BodyNode):
                if isinstance(option.value, ValueNode):
                    body[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    body[option.key.key] = commands.getstatusoutput(option.value.value)[1]
        if '?' in url:
            url = url + urllib.urlencode(params)
        else:
            url = url + '?' + urllib.urlencode(params)
        template = Template('''
            url = "{{ url }}"
            form := url.Values{}
            {% for k,v in headers.items() -%}
            form.Add("{{k}}", "{{v}}")
            {% endfor -%}
            client := &http.Client{}
            req, err := http.NewRequest("{{ method }}", url, strings.NewReader(form.Encode()))
            if err != nil {
                fmt.Println(err)
                return
            }
            {% for k,v in headers.items() %}
            req.Header.Add("{{k}}", "{{v}}")
            {% endfor -%}
            resp, err := client.Do(req)
        ''')
        return template.render(url=url, headers=headers, method=method)

    def to_python(self):
        url = self.ast.left.url
        method = self.ast.method.name
        params = {}
        headers = {}
        body = {}
        for option in self.ast.right.options if self.ast.right else []:
            if isinstance(option.key, QueryStringNode):
                if isinstance(option.value, ValueNode):
                    params[option.key.key] = option.value.value
                elif isinstance(option.value, ShellNode):
                    params[option.key.key] = commands.getstatusoutput(option.value.value)[1]
            elif isinstance(option.key, HeaderNode):
                headers[option.key.key] = option.value.value
            elif isinstance(option.key, BodyNode):
                body[option.key.key] = option.value.value

        template = Template('Hello {{ name }}!')
        template.render(name='John Doe')
        return '''
    params = {params}
    data = {data}
    headers = {headers}
    requests.{method}('{url}', params=params, data=data, body=body, headers=headers)
        '''.format(url=url, method=method.lower(), params=params, data=body, headers=headers)
