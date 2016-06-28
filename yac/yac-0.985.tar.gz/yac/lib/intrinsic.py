import os, imp, urlparse
from sets import Set
from yac.lib.file import get_file_contents, file_in_registry, file_in_yac_sources, create_customization_file
from yac.lib.paths import get_yac_path, get_lib_path
from yac.lib.variables import get_variable,set_variable
from yac.lib.naming import get_resource_name

INSTINSICS = ['yac-ref', 'yac-join', 'yac-fxn', 'yac-name']
YAC_REF_ERROR = "ref-error"
YAC_FXN_ERROR = "fxn-error"
INSTRINSIC_ERROR_KEY = 'intrinsic-errors'

def apply_fxn(source_dict, params):

    for key in source_dict.keys():

        if type(source_dict[key])==dict:
            source_dict[key] = apply_fxn_dict(source_dict[key], params)

        elif type(source_dict[key])==list:
            source_dict[key] = apply_fxn_list(source_dict[key], params)

        else:
            source_dict[key] = apply_fxn_leaf(key,source_dict, params)

    return source_dict 

def apply_fxn_dict(source_dict, params):

    sub_keys = source_dict.keys()
    if len(Set(sub_keys) & Set(INSTINSICS))==1:
        # treat this as a leaf
        source_dict = apply_fxn_leaf(sub_keys[0],source_dict, params)
    else:
        source_dict = apply_fxn(source_dict,params)

    return source_dict

def apply_fxn_list(source_list, params):

    for i, item in enumerate(source_list):
        if type(item)==dict:
            source_list[i] = apply_fxn_dict(item, params)           
        elif type(item)==list:
            source_list[i] = apply_fxn_list(item, params) 
        else:
            source_list[i] = item
    return source_list
              
def apply_fxn_leaf(key, source_dict, params):

    # see if any of the values have intrinsics
    if key == 'yac-ref':

        # Pull referenced value from the params. Default to a string
        # containing an error message in case the reference does not have
        # a corresponding value.

        setpoint = get_variable(params,source_dict[key],"M.I.A.")
        if setpoint=="M.I.A.":
            setpoint = '%s: %s'%(YAC_REF_ERROR,source_dict[key])
            error_list = get_variable(params,INSTRINSIC_ERROR_KEY,[])
            set_variable(params,INSTRINSIC_ERROR_KEY,error_list+[setpoint])

        return setpoint

    elif key == 'yac-join':

        delimiters = source_dict[key][0]
        name_parts = source_dict[key][1]

        # apply any intrinsics in list
        filled_parts = apply_fxn_list(name_parts, params)

        # get rid of empty strings before joining with delimitter
        filled_parts = filter(None,filled_parts)

        return delimiters.join(filled_parts)

    elif key == 'yac-fxn':

        # this value should be filled by custom function supplied by service
        fxn_script = source_dict[key]
        return apply_custom_fxn(fxn_script, params)

    elif key == 'yac-name':

        # get the name for this resource
        resource = source_dict[key]
        return get_resource_name(params, resource)

    else:

        return source_dict[key]

def apply_custom_fxn(script_path_arg, params):

    # get the python file that will be used to build this param value
    script_path = get_params_script_path(script_path_arg, params)

    return_val = ""

    if (script_path and os.path.exists(script_path)):

        # module_name = 'yac.lib.customizations.%s.params'%app_alias
        module_name = 'yac.lib.customizations'
        script_module = imp.load_source(module_name,script_path)

        # call the get_value fxn in the script
        return_val = script_module.get_value(params)

    else:
        setpoint = '%s: %s'%(YAC_FXN_ERROR,script_path)
        error_list = get_variable(params,INSTRINSIC_ERROR_KEY,[])
        set_variable(params,INSTRINSIC_ERROR_KEY,error_list+[setpoint])
        
    return return_val 

def get_params_script_path(script_path_arg, params):

    # if the path input is an yac url, download from the registry to a local
    # file
    if file_in_registry(script_path_arg):

        script_file_path = create_customization_file(script_path_arg)
    
    elif file_in_yac_sources(script_path_arg):
        
        script_file_path = os.path.join(get_yac_path(),script_path_arg)

    else:
        # assume the script path is local, and that path is relative to the location
        # of the service file (just like Dockerfile!)
        servicefile_path = get_variable(params,"servicefile-path")
        script_file_path = os.path.join(servicefile_path,script_path_arg)

    return script_file_path
