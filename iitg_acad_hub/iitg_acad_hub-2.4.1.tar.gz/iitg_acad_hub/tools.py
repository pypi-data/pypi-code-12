"""@package docstring
Documentation for this module.

This module has functions to sanitize inputs
"""

def sanitize_roll_number(roll):
	"""Function to check if the entered string is a valid roll number.
	"""
	validYears = ['12', '13', '14', '15']
	validDeps = ["0101", "0102", "0103", "0104", "0205", "0106", "0107", "0108", "0121", "0122", "0123"]
	if len(roll) == 9 and roll.isdigit():
		if roll[:2] in validYears:
			if roll[2:6] in validDeps:
				return True
	return False


def sanitize_phone_number(phone):
	"""Function to check if the entered string is a valid phone number.
	"""
	if len(phone) != 10 or not phone.isdigit():
		return False

	return True