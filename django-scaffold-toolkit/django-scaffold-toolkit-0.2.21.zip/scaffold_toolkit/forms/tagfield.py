# coding=utf-8
from django.forms import forms
from django.shortcuts import resolve_url
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe


class TagAutocompleteInput(forms.TextInput):
    class Media:
        css = {'all': ['javascript/library/select2-3.5.2/select2.css',
                       'javascript/library/select2-3.5.2/select2-bootstrap.css']}
        js = ['javascript/library/select2-3.5.2/select2.min.js',
              'javascript/library/select2-3.5.2/select2_locale_zh-CN.js']

    key_value_splitter = '`~`'

    def __init__(self, allow_create_tag=True, suggestion_url=None, attrs=None):
        super(TagAutocompleteInput, self).__init__(attrs=attrs)
        self.allow_create_tag = allow_create_tag
        self.suggestion_url = suggestion_url

    def render(self, name, value, attrs=None):
        """
        :param name: 控件名字
        :param value: 默认值. 可以采用 v1_:_text1,v2_:_text2 ...形式
        :param attrs: 附加的html属性
        """
        create_new_tag = self.allow_create_tag
        suggestion_url = resolve_url(self.suggestion_url if self.suggestion_url else 'tag_suggestion')
        js = u"""<script>
        $(document).ready(function(){{
        $("#{id_for_label}").select2({{
        placeholder: '{placeholder}',
            tags:{tag_model},
            multiple: true,
            tokenSeparators:{tag_model}?[",", " ",";"]:[],
            ajax: {{
                url: "{url}",
                dataType: 'json',
                data: function (term) {{
                    return{{term: term}}
                }},
                results: function (data) {{
                    return {{results: data}};
                }}
            }},
            {create_choice}
            initSelection: function (element, callback) {{
                var data = [],vals=[];
                $(element.val().split(",")).each(function (index,name) {{
                var kv=name.split("{splitter}");
                if (kv.length==1){{
                    data.push({{id: this, text: name}});
                    vals.push(this);
                }}
                else{{
                    data.push({{id:kv[0], text: kv[1]}});
                    vals.push(kv[0]);
                }}
                }});
                callback(data);
                element.val(vals.toString());
            }},
            minimumInputLength: 1,
            triggerChange: true
        }})
        }})
        </script>
        """
        js = js.format(id_for_label=force_text(self.id_for_label('id_%s' % name)),
                       url=force_text(suggestion_url),
                       placeholder=attrs.get('placeholder', '') if attrs else '',
                       tag_model='true' if self.allow_create_tag else 'false',
                       create_choice=""" createSearchChoice: function(term, data) {
                if ($(data).filter(function() {
                  return this.text == undefined || this.text.localeCompare(term) === 0;
                }).length === 0) {
                  return {
                    id: term,
                    text: term
                  };
                }
           },""" if create_new_tag else "",
                       splitter=self.key_value_splitter
                       )

        code = "%s %s" % (super(TagAutocompleteInput, self).render(name, value, attrs), js)
        return mark_safe(code)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value and self.key_value_splitter in value:
            result = []
            for item in value.split(','):
                v = item.split(self.key_value_splitter)[0]
                if v not in result:
                    result.append(v)
            value = u','.join(result)
        return value
