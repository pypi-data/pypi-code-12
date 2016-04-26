def get_cpp_proxy_code(df_sig_info, extra_header=None, extra_footer=None,
                       pointer_width=16):
    '''
    Generate C++ `Proxy` class, with one method for each corresponding
    method signature in `df_sig_info`.  Each method on the `Proxy` class:

     - Encodes method command and arguments into a serialized command array.
     - Sends command to remote device.
     - Decodes the result into C type.

    Arguments
    ---------

     - `df_sig_info`: A `pandas.DataFrame` with one row per method argument (as
       returned by `arduino_rpc.code_gen.get_multilevel_method_sig_frame`).
     - `extra_header`: Extra text to insert before class definition (optional).
     - `extra_footer`: Extra text to insert after class definition (optional).
     - `pointer_width`: Pointer bit-width on the target device. Specifically,
        on 8-bit AVR processors, addresses are 16-bit, but on 32-bit processors
        (e.g., Teensy 3.2 ARM) addresses are 32-bit.  Since one of the `*Array`
        struct member variables (i.e., `data`) is a pointer, the size of the
        structure differs based on the pointer size for the architecture.
    '''
    template = jinja2.Template(r'''
#include "Commands.h"

{% if extra_header is not none %}
{{ extra_header }}
{% endif %}

class Proxy {
{% for (method_i, method_name, camel_name, arg_count), df_method_i in df_sig_info.groupby(['method_i', 'method_name', 'camel_name', 'arg_count']) %}
    def {{ method_name }}(self{% if arg_count > 0 %}, {{ ', '.join(df_method_i.arg_name) }}{% endif %}):
        command = np.dtype('uint16').type(self._CMD_{{ method_name.upper() }})
{%- if arg_count > 0 %}
        ARG_STRUCT_SIZE = {{ df_method_i.struct_size.sum() }}
{%- if df_method_i.ndims.max() > 0 %}
{% for i, array_i in df_method_i[df_method_i.ndims > 0].iterrows() %}
        {{ array_i['arg_name'] }} = _translate({{ array_i['arg_name'] }})
        if isinstance({{ array_i['arg_name'] }}, str):
            {{ array_i['arg_name'] }} = map(ord, {{ array_i['arg_name'] }})
        # Argument is an array, so cast to appropriate array type.
        {{ array_i['arg_name'] }} = np.ascontiguousarray({{ array_i['arg_name'] }}, dtype='{{ array_i.atom_np_type }}')
{%- endfor %}
        array_info = pd.DataFrame([
{%- for arg_name in df_method_i.loc[df_method_i.ndims > 0, 'arg_name'] -%}
        {{ arg_name }}.shape[0], {% endfor -%}],
                                  index=[
{%- for arg_name in df_method_i.loc[df_method_i.ndims > 0, 'arg_name'] -%}
        '{{ arg_name }}', {% endfor -%}],
                                  columns=['length'])
        array_info['start'] = array_info.length.cumsum() - array_info.length
        array_data = ''.join([
{%- for arg_name in df_method_i.loc[df_method_i.ndims > 0, 'arg_name'] -%}
        {{ arg_name }}.tostring(), {% endfor -%}])
{%- else %}
        array_data = ''
{%- endif %}
        payload_size = ARG_STRUCT_SIZE + len(array_data)
        struct_data = np.array([(
{%- for i, (arg_name, ndims, np_atom_type) in df_method_i[['arg_name', 'ndims', 'atom_np_type']].iterrows() -%}
{%- if ndims > 0 -%}
        array_info.length['{{ arg_name }}'], ARG_STRUCT_SIZE + array_info.start['{{ arg_name }}'], {# #}
{%- else -%}
        {{ arg_name }}, {# #}
{%- endif -%}
{% endfor %})],
                               dtype=[
{%- for i, (arg_name, ndims, np_atom_type) in df_method_i[['arg_name', 'ndims', 'atom_np_type']].iterrows() -%}
{%- if ndims > 0 -%}
        ('{{ arg_name }}_length', 'uint32'), ('{{ arg_name }}_data', 'uint{{ pointer_width }}'), {% else -%}
        ('{{ arg_name }}', '{{ np_atom_type }}'), {% endif %}{% endfor %}])
        payload_data = struct_data.tostring() + array_data
{%- else %}
        payload_size = 0
        payload_data = ''
{%- endif %}

        payload_data = command.tostring() + payload_data
        packet = cPacket(data=payload_data, type_=PACKET_TYPES.DATA)
        response = self._send_command(packet)
{% if df_method_i.return_atom_type.iloc[0] is not none %}
        result = np.fromstring(response.data(), dtype='{{ df_method_i.return_atom_np_type.iloc[0] }}')
{% if df_method_i.return_ndims.iloc[0] > 0 %}
        # Return type is an array, so return entire array.
        return result
{% else %}
        # Return type is a scalar, so return first entry in array.
        return result[0]
{% endif %}{% endif %}
{% endfor %}
};


{% if extra_footer is not none %}
{{ extra_footer }}
{% endif %}
'''.strip())
    return template.render(df_sig_info=df_sig_info, extra_header=extra_header,
                           extra_footer=extra_footer,
                           pointer_width=pointer_width)
