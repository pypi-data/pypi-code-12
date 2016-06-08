"""
fav_movies = ["The Holy Grail", "The Life of Brain"]

for each_flick in fav_movies:
	print(each_flick)

print("-------------------------------------------------------------")
"""

movies = [
	"The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
	["Greham Chapman",
		["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

def print_lol(the_list):
	for each_item in the_list:
		if isinstance(each_item, list):
			print_lol(each_item)
		else:
			print(each_item)
