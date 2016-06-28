import os, shutil, subprocess
from yac.lib.file import get_file_contents

def get_file_type(file_str):
    """ return a filetype given a file """
    process_list = ["file", "--mime-type", file_str]
    p = subprocess.Popen(process_list, stdout=subprocess.PIPE)
    file_type, err = p.communicate()
    return file_type

def apply_stemplate(string_w_variables, template_variables):

    for key in template_variables:
        if 'value' in template_variables[key]:
            variable_value = template_variables[key]['value']
            if isinstance(variable_value, str) or isinstance(variable_value, unicode):
                to_replace = "{{%s}}"%key
                string_w_variables = string_w_variables.replace(to_replace, str(variable_value))

    return string_w_variables

def apply_ftemplate(file_w_variables, template_variables):

    # read file into string
    string_w_variables = get_file_contents(file_w_variables)

    return apply_stemplate(string_w_variables, template_variables)

def apply_templates_in_file(file_w_variables, template_variables, rendered_file_dest="tmp"):

    # get the file type
    # file_type = mimetypes.guess_type(file_w_variables)
    file_type = get_file_type(file_w_variables)

    # print 'file type for %s: %s'%(file_w_variables,file_type)

    # if the file is a text file render any variables in the file contents using the
    # provided template variables
    if (file_type and
            len(file_type) >= 1 and
            ('text' in file_type or
             'json' in file_type)):

        # read file into string
        file_contents = get_file_contents(file_w_variables)

        # render variables
        rendered_file_contents = apply_stemplate(file_contents, template_variables)

        # create a 'tmp' directory to hold the rendered file contents
        if not os.path.exists(rendered_file_dest):
            os.makedirs(rendered_file_dest)

        file_name = os.path.basename(file_w_variables)

        rendered_file = os.path.join(rendered_file_dest, file_name)

        # print "rf: %s"%rendered_file

        # write the rendered string into the temp file
        with open(rendered_file, 'w') as outfile:
            outfile.write(rendered_file_contents)
    else:

        # this isn't a text file, so don't attemp to render any variables
        # instead copy from source to destination

        # create a 'tmp' directory to hold the files
        if not os.path.exists(rendered_file_dest):
            os.makedirs(rendered_file_dest)

        file_name = os.path.basename(file_w_variables)

        rendered_file = os.path.join(rendered_file_dest, file_name)

        # print "nrf: %s"%rendered_file

        shutil.copy(file_w_variables, rendered_file)


    return rendered_file

def apply_templates_in_dir(source_dir, template_variables, dest_dir="tmp"):

    # get the contents of this directory
    dir_children = os.listdir(source_dir)

    for this_child in dir_children:

        if os.path.isfile(os.path.join(source_dir, this_child)):

            this_file = os.path.join(source_dir, this_child)

            apply_templates_in_file(this_file, template_variables, dest_dir)

        else:

            # destination is relative to the current destination
            new_dest_dir = os.path.join(dest_dir, this_child)

            # source dir is relative to the current source
            new_source_dir = os.path.join(source_dir, this_child)

            apply_templates_in_dir(new_source_dir, template_variables, new_dest_dir)

