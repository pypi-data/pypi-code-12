from yac.lib.file import get_file_contents
from yac.lib.template import apply_stemplate
from yac.lib.variables import get_variable

# Return a list of boot script lines, one per script line provided in params.
# List is intended to be incorporated into the UserData portion of a EC2 or ASG cloud formation
# template.
def get_value(params):

	boot_script_list=[]

	stock_resources = get_variable(params, 'stock-resources', [])
	servicefile_path = get_variable(params,"servicefile-path")
	includes_efs = 'efs' in stock_resources

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

				if (i==0):
					# first line should always describe shell env
					boot_script_list = [line] + ["\n"]

				elif (i==1):

					# inject the cluster name
					cluster_ref = ["CLUSTER_NAME=",{ "Ref": "ECS" },"\n"]

					boot_script_list = boot_script_list + cluster_ref + [line] + ["\n"]

					# inject the efs reference
					if includes_efs:

						efs_ref = ["export EFS_ID=",{ "Ref": "AppEFS" },"\n"]
						boot_script_list = boot_script_list + efs_ref + ["\n"]

				else:
					# add line as is
					boot_script_list = boot_script_list + [line] + ["\n"]

	else:
		boot_script_list = boot_script_list + ["# No boot script provided. See yac docs for more info.\n"]

	return boot_script_list
