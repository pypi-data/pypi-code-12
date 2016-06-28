import json
from yac.lib.file import get_file_contents
from yac.lib.template import apply_stemplate
from yac.lib.variables import get_variable

# Return a list of boot script lines, one per script line provided in params.
# List is intended to be incorporated into the UserData portion of a EC2 or ASG cloud formation
# template.
def get_value(params):

	boot_script_list=[]

	services_consumed = get_variable(params, 'services-consumed', [])
	servicefile_path = get_variable(params,"servicefile-path")

	boot_file = get_variable(params,'boot-file',"")

	# get the boot script from the user params
	if boot_file:
		
		boot_script_contents = get_file_contents(boot_file,servicefile_path)

		if boot_script_contents:

			# render template variables into the file contents
			boot_script_contents = apply_stemplate(boot_script_contents, params)

			# split script into lines
			boot_script_lines_list = boot_script_contents.split('\n')

			for i,line in enumerate(boot_script_lines_list):

				if ("{" in line and "}" in line and "Ref" in line):
					# this line contains a cloud formation reference which needs to be broken out
					# i.e. something like ...
					# CLUSTER_NAME={"Ref": "ECS"}

					prefix = line[:line.index('{')]
					reference = line[line.index('{'):line.index('}')+1]

					reference_dict = json.loads(reference)

					boot_script_list = boot_script_list + [prefix,{"Ref": reference_dict["Ref"]}] + ["\n"]

				else:
					boot_script_list = boot_script_list + [line] + ["\n"]	


	else:
		boot_script_list = boot_script_list + ["# No boot script provided. See yac docs for more info.\n"]

	# for debugging
	# pp_script(boot_script_list)

	return boot_script_list

def pp_script(boot_script_list):

	for line in boot_script_list:
		print str(line)

