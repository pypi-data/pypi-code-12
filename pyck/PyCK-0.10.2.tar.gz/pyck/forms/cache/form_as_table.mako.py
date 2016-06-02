# -*- coding:utf8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1459077794.0478497
_enable_loop = True
_template_filename = '/MyWork/Projects/PyCK/pyck/forms/templates/form_as_table.mako'
_template_uri = 'form_as_table.mako'
_source_encoding = 'utf8'
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        form = context.get('form', UNDEFINED)
        labels_position = context.get('labels_position', UNDEFINED)
        errors_position = context.get('errors_position', UNDEFINED)
        str = context.get('str', UNDEFINED)
        include_table_tag = context.get('include_table_tag', UNDEFINED)
        __M_writer = context.writer()

        num_cols = 2
        num_rows = 2
        
        if labels_position in ['left', 'right'] and errors_position in ['left', 'right']:
            num_cols = 3
            num_rows = 1
        elif labels_position in ['top', 'bottom'] and errors_position in ['top', 'bottom']:
            num_cols = 1
            num_rows = 3
        
        
        __M_locals_builtin_stored = __M_locals_builtin()
        __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['num_rows','num_cols'] if __M_key in __M_locals_builtin_stored]))
        __M_writer('\n')
        if include_table_tag:
            __M_writer('<table class="table table-striped table-hover">\n')
        if form._use_csrf_protection:
            __M_writer('    <input type="hidden" name="csrf_token" value="')
            __M_writer(str(form._csrf_token))
            __M_writer('" />\n')
        if '_csrf' in form.errors:
            __M_writer('    <tr><td class="errors" colspan="')
            __M_writer(str(num_cols))
            __M_writer('">')
            __M_writer(str(form.errors['_csrf'][0]))
            __M_writer('</td></tr>\n')
        for field in form:
            __M_writer('    ')

            field_label = '<td>' + str(field.label) + '</td>'
            field_content = '<td>' + str(field(class_="form-control")) + '</td>'
            field_errors = '<td></td>'
            if field.errors:
                field_errors = '<td class="errors">'
                for e in field.errors:
                    field_errors += e + ', '
                
                field_errors = field_errors[:-2] + '</td>'
            
            
            __M_locals_builtin_stored = __M_locals_builtin()
            __M_locals.update(__M_dict_builtin([(__M_key, __M_locals_builtin_stored[__M_key]) for __M_key in ['field_content','field_label','e','field_errors'] if __M_key in __M_locals_builtin_stored]))
            __M_writer('\n')
            if 1 == num_rows:
                __M_writer('    <tr>\n')
                if 'left'==labels_position:
                    __M_writer('        ')
                    __M_writer(str(field_label))
                    __M_writer('\n')
                if 'left'==errors_position:
                    __M_writer('        ')
                    __M_writer(str(field_errors))
                    __M_writer('\n')
                __M_writer('        ')
                __M_writer(str(field_content))
                __M_writer('\n')
                if 'right'==labels_position:
                    __M_writer('        ')
                    __M_writer(str(field_label))
                    __M_writer('\n')
                if 'right'==errors_position:
                    __M_writer('        ')
                    __M_writer(str(field_errors))
                    __M_writer('\n')
                __M_writer('    </tr>\n')
            elif 3 == num_rows:
                __M_writer('    <tr>\n    <td>\n        <table>\n')
                if 'top'==labels_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_label))
                    __M_writer('</tr>\n')
                if 'top'==errors_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_errors))
                    __M_writer('</tr>\n')
                __M_writer('        <tr>')
                __M_writer(str(field_content))
                __M_writer('</tr>\n')
                if 'bottom'==labels_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_label))
                    __M_writer('</tr>\n')
                if 'bottom'==errors_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_errors))
                    __M_writer('</tr>\n')
                __M_writer('        </table>\n    </td>\n    </tr>\n')
            else: ## 2 rows and 2 cols
                __M_writer('    <tr>\n    <td>\n        <table>\n')
                if 'top'==labels_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_label))
                    __M_writer('</tr> \n        <tr> ')
                elif 'left'==labels_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_label))
                    __M_writer(' ')
                __M_writer('        ')
                if 'top'==errors_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_errors))
                    __M_writer('</tr> \n        <tr> ')
                elif 'left'==errors_position:
                    __M_writer('        <tr>')
                    __M_writer(str(field_errors))
                    __M_writer(' ')
                __M_writer('        ')
                __M_writer('        ')
                __M_writer(str(field_content))
                __M_writer('\n        ')
                if 'bottom'==labels_position:
                    __M_writer('        </tr>\n        <tr>')
                    __M_writer(str(field_label))
                    __M_writer('</tr>\n')
                elif 'right'==labels_position:
                    __M_writer('        ')
                    __M_writer(str(field_label))
                    __M_writer('</tr>\n')
                __M_writer('        ')
                if 'bottom'==errors_position:
                    __M_writer('        </tr>\n        <tr>')
                    __M_writer(str(field_errors))
                    __M_writer('</tr>\n')
                elif 'right'==errors_position:
                    __M_writer('        ')
                    __M_writer(str(field_errors))
                    __M_writer('</tr>\n')
                __M_writer('        </table>\n    </td>\n    </tr>\n')
            __M_writer('    \n')
        if include_table_tag:
            __M_writer('</table>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"uri": "form_as_table.mako", "line_map": {"16": 0, "26": 1, "40": 11, "41": 12, "42": 13, "43": 15, "44": 16, "45": 16, "46": 16, "47": 18, "48": 19, "49": 19, "50": 19, "51": 19, "52": 19, "53": 21, "54": 22, "55": 22, "69": 32, "70": 33, "71": 34, "72": 35, "73": 36, "74": 36, "75": 36, "76": 38, "77": 39, "78": 39, "79": 39, "80": 41, "81": 41, "82": 41, "83": 42, "84": 43, "85": 43, "86": 43, "87": 45, "88": 46, "89": 46, "90": 46, "91": 48, "92": 49, "93": 50, "94": 53, "95": 54, "96": 54, "97": 54, "98": 56, "99": 57, "100": 57, "101": 57, "102": 59, "103": 59, "104": 59, "105": 60, "106": 61, "107": 61, "108": 61, "109": 63, "110": 64, "111": 64, "112": 64, "113": 66, "114": 69, "115": 70, "116": 73, "117": 74, "118": 74, "119": 74, "120": 76, "121": 77, "122": 77, "123": 77, "124": 79, "125": 80, "126": 81, "127": 81, "128": 81, "129": 83, "130": 84, "131": 84, "132": 84, "133": 86, "134": 87, "135": 87, "136": 87, "137": 89, "138": 90, "139": 91, "140": 91, "141": 92, "142": 93, "143": 93, "144": 93, "145": 95, "146": 96, "147": 97, "148": 98, "149": 98, "150": 99, "151": 100, "152": 100, "153": 100, "154": 102, "155": 106, "156": 108, "157": 109, "163": 157}, "source_encoding": "utf8", "filename": "/MyWork/Projects/PyCK/pyck/forms/templates/form_as_table.mako"}
__M_END_METADATA
"""
