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
			if all (len(row) == len(command.header) for row in command.rows):
				# same amout of columns everywhere => multiple 1-dimensional datasets
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
						namespace[name] = assign (values, header.error, header.unit, header.name, header.longname)
			elif len(command.header) == 1:
				# only one header, but more columns => one 2-dimensional dataset
				values = []
				for row in command.rows:
					row_values = []
					for entry in row:
						value = parse_expr(entry, namespace)
						row_values.append(value)
					values.append(row_values)
				header = command.header[0]
				namespace[header.name] = assign (values, header.error, header.unit, header.name, header.longname)
			elif len(command.header) == 2 and command.header[0].name + "_err" == command.header[1].name:
				# two headers, but more columns => one 2-dimensional dataset with error
				values = []
				errors = []
				for row in command.rows:
					row_values = []
					for entry in row:
						value = parse_expr(entry, namespace)
						row_values.append(value)
					values.append(row_values[::2])
					errors.append(row_values[1::2])
				header = command.header[0]
				namespace[command.header[0].name] = assign (values, errors, command.header[0].unit, command.header[0].name, command.header[0].longname, None, command.header[1].unit)
			else:
				raise RuntimeError("Wrong number of columns in multiassignment.")

		elif command.parseinfo.rule == "python_code":
			code = '\n'.join(command.code)
			exec (code, None, namespace)
		else:
			raise RuntimeError("Unknown syntactic command type")
	return namespace
