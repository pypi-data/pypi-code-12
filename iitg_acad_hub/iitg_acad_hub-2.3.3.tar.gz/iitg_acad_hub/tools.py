def sanitize_roll_number(roll):
	if len(roll) != 9 or not roll.isdigit():
		return False

	validYears = ['12', '13', '14', '15']
	if roll[:2] not in validYears:
		return False

	return True


def sanitize_phone_number(phone):
	if len(phone) != 10 or not phone.isdigit():
		return False

	return True