#
# This file is part of RESORT.
#
# RESORT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RESORT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RESORT.  If not, see <http://www.gnu.org/licenses/>.
#

import resort.engine
import resort.engine.execution

import argparse
import colorama
import io
import os
import sys

#
# Entry point
#
def setup(
	work_dir=".resort",
	profiles=None
):

	"""
	Configures a project to be managed by *resort*.
	
	:param str work_dir:
	   Path of directory were profiles will be created.
	:param dict profiles:
	   Dictionary containing profile type and instance entries.
	"""
	
	# Initialize colorama
	colorama.init()
	
	# Program name
	prog_name = sys.argv[0]
	
	# Profile manager
	prof_mgr = engine.ProfileManager(os.getcwd(), work_dir, profiles)
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	parser.add_argument(
		"profile",
		metavar="profile",
		type=str,
		nargs=1,
		help="Profile name"
	)
	parser.add_argument(
		"command",
		metavar="command",
		type=argparse_command,
		nargs=1,
		help="Command name"
	)
	parser.add_argument(
		"arguments",
		metavar="args",
		nargs=argparse.REMAINDER,
		help="Command arguments"
	)
	args = parser.parse_args(sys.argv[1:])
	
	# Execute command
	cmd_name, cmd_fn = args.command[0]
	cmd_prog_name = "{} profile {}".format(prog_name, cmd_name)
	prof_name = args.profile[0]
	prog_args = args.arguments
	cmd_fn(cmd_prog_name, prof_mgr, prof_name, prog_args)
	
#
# Argument parser for command
#
def argparse_command(value):

	try:
		cmd_prefix = "command_"
		return (value, globals()["{}{}".format(cmd_prefix, value)])
	except:
		msg = io.StringIO()
		msg.write("unrecognized command '")
		msg.write(value)
		msg.write("'\n\nAvailable commands:\n")
		cmds = [
			(g_name[len(cmd_prefix):], globals()[g_name])
			for g_name in sorted(globals())
			if g_name.startswith(cmd_prefix)
		]
		desc_pos = 0
		for cmd_name, cmd in cmds:
			desc_pos = max(desc_pos, len(cmd_name))
		for cmd_name, cmd in cmds:
			msg.write(cmd_name.ljust(desc_pos))
			msg.write("  ")
			msg.write(cmd.__doc__.strip())
			msg.write("\n")
		msg.seek(0)
		raise argparse.ArgumentTypeError(msg.read())
		
#
# Argument parser for status depth
#
def argparse_status_depth(value):

	try:
		if int(value) > 0:
			return int(value)
	except:
		pass
	raise argparse.ArgumentTypeError("Bad tree depth {}".format(value))
	
#
# Component existence check
#
def component_exists(prof_stub, comp_stub):

	if comp_stub not in prof_stub.component_list():
		msg = "Component \"{}\" does not exist"
		raise Exception(msg.format(comp_stub.name()))
		
#		
# Component status printer
#
def print_component_status(out, context, comp_stub, last, depth, indent,
		show_type, tree_depth):

	for indent_last in indent:
		if indent_last:
			out.write(" ")
		else:
			out.write("\u2502")
		out.write("   ")
	if last:
		out.write("\u2514")
	else:
		out.write("\u251c")
	out.write("\u2500 ")
	
	avail = comp_stub.available(context)
	if avail is True:
		out.write(colorama.Style.BRIGHT)
	elif avail is False:
		out.write(colorama.Style.DIM)
	out.write(comp_stub.name())
	
	type_name = comp_stub.type_name()
	if show_type and type_name is not None:
		out.write(" (")
		out.write(type_name)
		out.write(")")
	out.write(colorama.Style.RESET_ALL)
	out.write("\n")
	
	deps = list(comp_stub.dependencies())
	new_depth = depth + 1
	new_indent = []
	new_indent.extend(indent)
	new_indent.append(last)
	for i, dep_stub in enumerate(deps):
		last = i == len(deps) - 1
		if tree_depth is None or depth < tree_depth:
			print_component_status(out, context, dep_stub, last, new_depth,
					new_indent, show_type, tree_depth)
					
#
# Operation executor
#
def operation_execute(op, context):

	try:
		op.execute(context)
	except Exception as ex:
		print(ex)
		
#
# Command init
#
def command_init(prog_name, prof_mgr, prof_name, prog_args):

	"""
	Initialize a profile.
	"""
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	parser.add_argument(
		"type",
		metavar="type",
		type=str,
		nargs=1,
		help="profile type"
	)
	args = parser.parse_args(prog_args)
	
	# Profile store
	prof_type = args.type[0]
	prof_mgr.store(prof_name, prof_type)
	
#
# Command list
#
def command_list(prog_name, prof_mgr, prof_name, prog_args):

	"""
	Print the list of components.
	"""
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	args = parser.parse_args(prog_args)
	
	# Profile load
	prof_stub = prof_mgr.load(prof_name)
	
	# Print component list
	out = io.StringIO()
	for comp_stub in prof_stub.component_list():
		if comp_stub.name() is not None:
			out.write(comp_stub.name())
			out.write("\n")
	out.seek(0)
	sys.stdout.write(out.read())
	
#
# Command status
#
def command_status(prog_name, prof_mgr, prof_name, prog_args):

	"""
	Show status of component tree.
	"""
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	parser.add_argument(
		"-t",
		"--type",
		required=False,
		action="store_true",
		default=False,
		dest="show_type",
		help="show component qualified class name"
	)
	parser.add_argument(
		"-d",
		"--depth",
		metavar="tree_depth",
		required=False,
		type=argparse_status_depth,
		default=None,
		dest="tree_depth",
		help="integer value of dependency tree depth"
	)
	parser.add_argument(
		"components",
		metavar="comps",
		nargs=argparse.REMAINDER,
		help="system components"
	)
	args = parser.parse_args(prog_args)
	
	# Profile load
	prof_stub = prof_mgr.load(prof_name)
	
	# Collect component stubs
	comp_stubs = []
	if len(args.components) == 0:
		raise Exception("Empty component list")
	for comp_name in args.components:
		comp_stub = prof_stub.component(comp_name)
		component_exists(prof_stub, comp_stub)
		comp_stubs.append(comp_stub)
		
	# Print status
	show_type = args.show_type
	tree_depth = args.tree_depth
	context = prof_stub.context()
	out = io.StringIO()
	for i, comp_stub in enumerate(comp_stubs):
		last = i == len(comp_stubs) - 1
		print_component_status(out, context, comp_stub, last, 1, [], show_type,
				tree_depth)
	out.seek(0)
	sys.stdout.write(out.read())
	
#
# Command insert
#
def command_insert(prog_name, prof_mgr, prof_name, prog_args):

	"""
	Insert components.
	"""
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	parser.add_argument(
		"components",
		metavar="comps",
		nargs=argparse.REMAINDER,
		help="system components"
	)
	args = parser.parse_args(prog_args)
	
	# Profile load
	prof_stub = prof_mgr.load(prof_name)
	
	# Collect component stubs
	comp_stubs = []
	if len(args.components) == 0:
		raise Exception("Empty component list")
	for comp_name in args.components:
		comp_stub = prof_stub.component(comp_name)
		component_exists(prof_stub, comp_stub)
		comp_stubs.append(comp_stub)
		
	# Create insert plan
	context = prof_stub.context()
	plan = []
	for comp_stub in comp_stubs:
		comp_stub.insert(context, plan)
		
	# Execute insert plan
	for op in plan:
		operation_execute(op, context)
		
#
# Command delete
#
def command_delete(prog_name, prof_mgr, prof_name, prog_args):

	"""
	Delete components.
	"""
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	parser.add_argument(
		"components",
		metavar="comps",
		nargs=argparse.REMAINDER,
		help="system components"
	)
	args = parser.parse_args(prog_args)
	
	# Profile load
	prof_stub = prof_mgr.load(prof_name)
	
	# Collect component stubs
	comp_stubs = []
	if len(args.components) == 0:
		raise Exception("Empty component list")
	for comp_name in args.components:
		comp_stub = prof_stub.component(comp_name)
		component_exists(prof_stub, comp_stub)
		comp_stubs.append(comp_stub)
			
	# Create delete plan
	context = prof_stub.context()
	plan = []
	for comp_stub in comp_stubs:
		comp_stub.delete(context, plan)
		
	# Execute delete plan
	for op in plan:
		operation_execute(op, context)
		
#
# Command update
#
def command_update(prog_name, prof_mgr, prof_name, prog_args):

	"""
	Update components.
	"""
	
	# Retrieve arguments
	parser = argparse.ArgumentParser(
		prog=prog_name
	)
	parser.add_argument(
		"components",
		metavar="comps",
		nargs=argparse.REMAINDER,
		help="system components"
	)
	args = parser.parse_args(prog_args)
	
	# Profile load
	prof_stub = prof_mgr.load(prof_name)
	
	# Collect component stubs
	comp_stubs = []
	if len(args.components) == 0:
		raise Exception("Empty component list")
	for comp_name in args.components:
		comp_stub = prof_stub.component(comp_name)
		component_exists(prof_stub, comp_stub)
		comp_stubs.append(comp_stub)
		
	context = prof_stub.context()
	
	# Create delete plan
	plan = []
	for comp_stub in comp_stubs:
		comp_stub.delete(context, plan)
		
	# Execute delete plan
	for op in plan:
		operation_execute(op, context)
		
	# Update component stub list
	for op in plan:
		comp_stub = prof_stub.component(op.name())
		if comp_stub not in comp_stubs:
			comp_stubs.append(comp_stub)
	
	# Create insert plan
	plan = []
	for comp_stub in comp_stubs:
		comp_stub.insert(context, plan)
		
	# Execute insert plan
	for op in plan:
		operation_execute(op, context)

