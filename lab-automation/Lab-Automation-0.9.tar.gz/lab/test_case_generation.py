import exrex
import re

MAX_LEN=100

def parse(regevar):											#parses the regex given tby the instructor
	if bool(re.search('=', regevar)):
		var, regex = regevar.split('=')
		var = var.strip()
		regex = regex.strip()
		return var,regex
	else:
		regex = regevar.strip()
		return None,regex


def generate(regex_file):								#generates the random test cases based on the regex
	test_case=list()
	variables={}
	for regevar in regex_file.splitlines():
		var, regex = parse(regevar)
		for v,val in variables.iteritems():
			regex = regex.replace(v, val)
		if(var != None):
			variables[var]=exrex.getone(regex,MAX_LEN)
		else:
			test_case.append(exrex.getone(regex,MAX_LEN))
	return test_case


