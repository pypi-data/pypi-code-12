import re
from errorpro.core import assign
from errorpro.quantities import parse_expr

def interpret (program, namespace):
	"""
	executes the program
	"""
	for command in program:
		if command.parseinfo.rule == "assignment":
			value = command.value
			error = command.error
			if value is not None:
			    value = parse_expr(value, namespace)
			if error is not None:
			    error = parse_expr(error, namespace)

			namespace[command.name] = assign (value, error, command.unit, command.name, command.longname)

		elif command.parseinfo.rule == "multi_assignment":
			# collect columns:
			columns = {}
			for columnIndex in range(len(command.header)):
				values = []
				for row in command.rows:
					value = parse_expr(row[columnIndex], namespace)
					values.append(value)
				columns[command.header[columnIndex].name] = {
				 "header": command.header[columnIndex],
				 "values": values
				}
			# pair value columns with err-columns:
			for name in columns:
				if name.endswith("_err"):
					continue
				header = columns[name]["header"]
				values = columns[name]["values"]
				if name + "_err" in columns:
					errorColumn = columns[name + "_err"]
					if errorColumn["header"].error is not None:
						raise RuntimeError("Variables with _err notation cannot use the <...> notation:  %s"%errorColumn["header"].name)
					if errorColumn["header"].longname is not None:
						raise RuntimeError("Variables with _err notation cannot have a long name: %s"%errorColumn["header"].longname)
					if header.error is not None:
						raise RuntimeError("Variables with a corresponding _err column cannot have a general error specified: %s"%header.name)
					namespace[name] = assign (values, errorColumn["values"], header.unit, name, header.longname, None, errorColumn["header"].unit)
				else:
					namespace[header.name] = assign (values, header.error, header.unit, header.name, header.longname)

		elif command.parseinfo.rule == "python_code":
			code = '\n'.join(command.code)
			exec (code, None, namespace)
		else:
			raise RuntimeError("Unknown syntactic command type")
	return namespace
