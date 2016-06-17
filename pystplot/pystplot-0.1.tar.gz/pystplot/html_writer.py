import html_page
import jstemplate
import plot_api_templates
import webbrowser
from string import Template

NEWLINE = '\n'
COMMA = ','

def write_string_to_file(file_string, file_name):
    out_file = open(file_name,'w')
    out_file.write(file_string)
    out_file.close()

def write_html_to_file(html_file_string, plot_file):
    write_string_to_file(html_file_string, plot_file)

def write_data_to_file(data_file_string, plot_list):
    write_string_to_file(data_file_string, plot_list)

def put_data_into_js_string(plot_list_as_string):
    get_data_function = Template(jstemplate.get_data_function_template)
    return get_data_function.substitute(plot_data_string = plot_list_as_string)

def get_function_call_tag(plot_info_dict):
    script_tag = Template(html_page.script_tag_template)
    function_call_js = Template(jstemplate.function_call_template)
    function_call_string = function_call_js.substitute(plot_info_dict)
    return script_tag.substitute(script = function_call_string)

def get_plot_api_scripts():
    script_transforms = Template(html_page.script_tag_template)
    script_plotmain = Template(html_page.script_tag_template)
    script_numerics = Template(html_page.script_tag_template)
    script_string = script_transforms.substitute(script = plot_api_templates.transforms_script_template)
    script_string += script_transforms.substitute(script = plot_api_templates.plotmain_script_template)
    script_string += script_transforms.substitute(script = plot_api_templates.numerics_script_template)
    return script_string

def get_function_tags(fig_info):
    tags = ""
    for p in range(fig_info.no_plots()):
        plot_info = fig_info.get_plot(p)
        plot_info_dict = plot_info.get_container_info()
        tags += get_function_call_tag(plot_info_dict)
    return tags

def get_container_tag(plot_info_dict):
    container = Template(html_page.container_tag_template)
    return container.substitute(plot_info_dict)

def get_row(fig_info, row_index):
    row= ""
    start_index = fig_info.cols() * row_index
    col_indices = range(start_index, start_index + fig_info.cols())
    for cols in col_indices:
        plot_info = fig_info.get_plot(cols)
        plot_info_dict = plot_info.get_container_info()
        row += get_container_tag(plot_info_dict)
    return row

def get_rows(fig_info):
    table = ""
    for row_index in range(fig_info.rows()):
        row_content = get_row(fig_info, row_index)
        row = Template(html_page.table_row_template)
        table += row.substitute(container = row_content)
    return table

def get_plot_table(fig_info):
    table = Template(html_page.table_template)
    row = get_rows(fig_info)
    return table.substitute(table_row = row)

def get_html(fig_info):
    html = Template(html_page.body_template)
    tags = {}
    tags['plot_api_scripts'] = get_plot_api_scripts()
    tags['function_call_tag'] = get_function_tags(fig_info)
    tags['plot_table'] = get_plot_table(fig_info)
    return html.substitute(tags)

def data_to_flotr_format(x_list, y_list):
    zipped = zip(x_list, y_list)
    return_list = []
    for z in zipped:
        return_list.append(list(z))
    return return_list

def set_line_properties(property_string, line_object):
    line_object['lines'] = {'show':True}
    if 'o' in property_string:
        line_object['points'] = {'show':True}
        line_object['lines'] = {'show':False}
    if '-' in property_string:
        line_object['lines'] = {'show':True}
    if 'r' in property_string:
        line_object['color'] = 'red'
    if 'b' in property_string:
        line_object['color'] = 'blue'
    if 'g' in property_string:
        line_object['color'] = 'green'
    if 'y' in property_string:
        line_object['color'] = 'yellow'
    if 'm' in property_string:
        line_object['color'] = 'magenta'
    if 'c' in property_string:
        line_object['color'] = 'cyan'
    if 'w' in property_string:
        line_object['color'] = 'white'
    if 'k' in property_string:
        line_object['color'] = 'black'
    return line_object

def flotr_line_object(data, property_string):
    line_object = {'data':data}
    line_object = set_line_properties(property_string, line_object)
    return line_object

def make_html_file(fig_info, plot_file):
    html_string = get_html(fig_info)
    write_html_to_file(html_string, plot_file)

