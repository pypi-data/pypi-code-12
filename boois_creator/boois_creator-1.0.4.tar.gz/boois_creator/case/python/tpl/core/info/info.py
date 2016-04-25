# -*- coding: utf-8 -*-
from utils.vali_rule_chker import ValiRuleChker
import datetime
{%for x in obj.fields-%}
{% if x.cls_file-%}
from core.info.{{top_obj_name}} import {{x.cls_file}}_info
{%endif%}
{%-endfor%}

class {{obj.name_cap}}Info(object):
    # region raw json data
    '''
    {{obj.data_json}}
    '''
    # endregion
    # region fields


    {%for x in obj.fields-%}
    {{x.name_field_name}} = "{{x.name}}"
    {%endfor%}

    F_NAME_TOTAL=[
        {%for x in obj.fields-%}
        {{x.name_field_name}},
        {%endfor%}
    ]
    # endregion
    # region changed_fields
    def get_changed_fields(self):
        if self._changed_fields is None:
            self._changed_fields=[]
        return self._changed_fields

    def add_changed_field(self, field, *args):
        fields=list(args)
        fields.append(field)
        for f in fields:
            if f in {{obj.name_cap}}Info.F_NAME_TOTAL:
                self._changed_fields.append(f)
    def del_changed_field(self, field,*args):
        fields=list(args)
        fields.append(field)
        for f in fields:
            if f in {{obj.name_cap}}Info.F_NAME_TOTAL:
                self._changed_fields.remove(f)

    def set_total_changed_fields(self):
        self._changed_fields={{obj.name_cap}}Info.F_NAME_TOTAL

    def clear_changed_fields(self):
        self._changed_fields=[]

    # endregion

    changed_fields=property(fget = get_changed_fields)


    {%for x in obj.fields-%}
    # region {{x.name}} {{x.comment}}
    def get_{{x.name}}(self):
        if not hasattr(self,"_{{x.name}}"):
            self._{{x.name}}={{x.default_val}}
        return self._{{x.name}}

    def set_{{x.name}}(self, val,raise_err=True):
        if val is not None:
            try:
                self.check_{{x.name}}(val)
            except ValueError,ex:
                if raise_err:
                    raise ex
                else:
                    val={{x.default_val}}
        else:
            val={{x.default_val}}
        self._{{x.name}}=val
        self._changed_fields.append({{obj.name_cap}}Info.{{x.name_field_name}})

    def check_{{x.name}}(self,val):
        {{x.checker}}

    {{x.name}} = property(fget = get_{{x.name}}, fset = set_{{x.name}})

    # endregion
    {%endfor%}
    def __init__(self, {%for x in obj.fields-%}
                 {{-x.name}}=None
                 {%-if not loop.last-%}, {%endif-%}
                 {%-endfor-%}):
        self._changed_fields=[]
        {%for x in obj.fields-%}
        if {{x.name}} is not None:
            self.set_{{x.name}}({{x.name}})
        {%endfor%}
if __name__ == '__main__':
    # g=GoodsInfo()
    # g.set_app_key("a")
    # g.set_cmnt_count(0)
    # g.add_changed_field(GoodsInfo.F_CATEGORY_LIST_NAME)
    # g.add_changed_field(GoodsInfo.F_COLL_COUNT_NAME,GoodsInfo.F_TITLE_NAME)
    # g.del_changed_field(GoodsInfo.F_COLL_COUNT_NAME,GoodsInfo.F_CATEGORY_LIST_NAME)
    # g.set_total_changed_fields()
    # g.clear_changed_fields()
    # print g.changed_fields
    pass
