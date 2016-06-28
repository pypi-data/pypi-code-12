#!/usr/bin/env python
import time, os, json
from yac.lib.variables import get_variable, set_variable

# default yac namer

def get_stack_name( params ):  
    
    delimitter = get_variable(params,'delimitter','-')
    
    name_parts = [get_variable(params,'prefix',''), 
                    get_variable(params,'service-alias','')]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    stack_name = delimitter.join(name_parts)

    return stack_name

# name each yac resource
def get_resource_name(params, resource):   

    delimitter = get_variable(params,'delimitter','-')

    name_parts = [get_variable(params,'service-alias',''),
                  resource]

    # get rid of empty strings
    name_parts = filter(None,name_parts)

    resource_name = delimitter.join(name_parts)

    return resource_name  