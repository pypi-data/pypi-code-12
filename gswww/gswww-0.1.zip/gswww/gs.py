import requests
from bs4 import BeautifulSoup
import time

def is_number(s):
    """
    Check and parse entered value as a number
    """
    try:
        int(s)
        return True
    except ValueError:
        return False

def connect(fname, url_to_scrape):
	try:
		r = requests.get(url_to_scrape) 
		soup = BeautifulSoup(r.text, "html.parser")
		with open(fname, "w") as text_file:
			text_file.write("{}".format(soup))
		with open(fname) as f:
			content = f.readlines()
		return content
	except Exception:
		print "ConnectionError"
		print "Retrying...."
		return connect(fname, url_to_scrape)


def find_leaders(content):
	index = 0
	heading_index = 0
	for line in content:
		if line.find("Golden Shoe Ranking") != -1:
			heading_index = index
			break
		index += 1

	angular_brack_open = 0
	angular_brack_closed = 0
	for line in content[heading_index:]:
		if line.find("crimson") != -1:
			print ""
			line_index = 0
			while line_index < len(line):
				char = line[line_index]
				# num_to_be_found = num_found + 1
				# num_found = 0
				try:
					if char == '<':
						angular_brack_open += 1
					elif char == '>':
						angular_brack_closed += 1
				except Exception:
					print "Exc line = " + str(line)
					print "Exc line_index = " + str(line_index)
					print "len line = " + str(len(line))
					exit(0)
				if angular_brack_open == angular_brack_closed and angular_brack_open != 0 and line[line_index + 1] != '<':
					print extract_name(line, line_index) + "		",
					line_index += len(extract_name(line, line_index))
				line_index += 1


def extract_name(line, index):
	end_index = index
	for char in line[index + 1 : ]:
		if char != '<':
			end_index += 1
		else:
			break
	return line[index + 1 : end_index + 1]

if __name__ == "__main__":
	content = connect("temp.txt", "http://www.eurotopfoot.com/gb/soulierdor.php3")
	find_leaders(content)
	key = raw_input("Press Enter to exit")
	exit(0)
	
