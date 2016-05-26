"""nester
i am a nester"""

def print_lol_test(the_list):
	for i in the_list:
		if isinstance(i, list):
			print_lol_test(i)
		else:
			print(i)
