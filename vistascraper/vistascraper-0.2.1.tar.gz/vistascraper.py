#!/usr/bin/env python3
# Celyn Walters <celyn.walters@stfc.ac.uk>
# Jan+ 2016

# Colours, progressbars, SIGINT and other special features don't work on Cygwin
# TODO colours?
# TODO raw XML seperates arrays with \r

import click # CLI functions
import requests # For accessing remote xml file
import xml.etree.ElementTree as ET # For navigating it
import re # Regex
import time # Delays and timestamps
import sys # CLI functions
import os # For Windows cmd to clear screen
import csv # For writing the output file
import collections # For parsing the channel names
import platform # For determining the type of Python which is being called

ostype = platform.system() # Can be "Windows", "Linux", "CYGWIN_NT-6.1" or similar. TODO test OSX etc.

# Depending on the terminal, can make a sound or flash the window
# Used for debugging, uses echo to print immediately on all platforms
def bell():
	click.echo("\a", nl=False)

# Tiny code-cleaning function
# Expects: Error string
def error_quit(*args):
	click.echo(" ".join(map(str, args))+"\n") # Emulates 'print()' behaviour for comma separated args
	sys.exit(1)

# Alphabetical sorting for ambiguous equal-common channel name halves
# Expects: SORTED list using channel name halves and how many times used: (TEXT, occurences)
# Lists are mutable so I don't need to return anything
def sort_equal_common(lst):
	sublst = [] # To be alphabetically sorted and to replace
	indexes = [] # Which ones to replace, to avoid None types
	if (len(lst) == 1): return # Nothing needs to be sorted
	for i in range(0, len(lst)):
		if (i == len(lst)-1):
			sublst.append(lst[i])
			indexes.append(i)
			break # We've hit the end of the list, is as frequent as previous
		if (lst[i][0]) is not None:
			if (lst[i+1][0] is not None):
				if (lst[i][1] == lst[i+1][1]):
					sublst.append(lst[i]) # Occurs as frequently as next
					indexes.append(i)
				else:
					break # Next one occurs fewer times, stop here
	sublst = sorted(sublst, key=lambda x: x[0]) # Sorted by the name field (e.g. "NAME, 3"")
	#lst[0:len(sublst)-1] = sublst # Replace that subsection with alphabetically sorted name parts
	i = 0
	for index in range(0, len(indexes)):
		lst[indexes[index]] = sublst[i]
		i += 1

# Sorts channels by the most common name halves
# Channels should already be sorted alphabetically by Vista...
# Expects: List of Vista channel names formatted TEXT:TEXT
# Returns: Sorted list of channel indexes
def most_common(lst):
	from collections import Counter
	try: # Split each element
		if (len(lst) < 1): raise Exception("No channels present")
		new = map(lambda x: re.split(":", x), lst) # Split channel names, all should have a central colon
		tr = list(map(list, zip(*new))) # Transpose 2D list, map into list from tuple
		if (len(tr) <= 1): raise Exception("A channel name is formatted incorrectly, probably missing ':'") # Not all channel names could be split
	except Exception as error: error_quit(error)
	indexes = []
	while (True): # Records and removes names with a side which is most common, until all done
		l = Counter(tr[0]).most_common() # Sorted list by most common, left side
		sort_equal_common(l) # Removes any alphabetical ambiguity in channel name sorting
		if (len(l) <= 1): break # Only one key remains now: 'None'. All have been removed (toremove)
		if (l[0][0] is None): leftCom = l[1] # Skip removed, as 'None' is now the most common
		else: leftCom = l[0] # Probably first run, no 'None' exists yet
		r = Counter(tr[1]).most_common() # Sorted list by most common, right side
		sort_equal_common(r) # Removes any ambiguity in channel name sorting
		if (r[0][0] is None): rightCom = r[1] # Skip removed, as 'None' is now the most common
		else: rightCom = r[0] # Probably first run, no 'None' exists yet
		side = int(rightCom[1]>leftCom[1]) # Which side is greater?
		if (side): mostCom = rightCom # Right side is more common
		else: mostCom = leftCom # Left side is more common
		for i in range(mostCom[1]): # Runs for each instance the most common channel name part occurs
			toremove = tr[side].index(mostCom[0]) # Find the channel name part in the search list
			indexes.append(toremove) # Adds the next index to the results
			tr[0][toremove], tr[1][toremove] = None, None # Removes it from the search list
	# TODO each category could be displayed in a columnated list
	return(indexes)

@click.version_option(version=0.1)
@click.command(name="ISIS Vista scraper", context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("-V", "--version", is_flag=True, default=False, help="Displays the program version and exits")
@click.option("-u", "--url", help="Full URL to xml page")
@click.option("-i", "--ip", help="ip:port - Uses function 14: All database channels")
@click.option("-v", "--verbose", is_flag=True, help="Display more information than usual")
@click.option("-q", "--quiet", is_flag=True, help="Display less information than usual")
@click.option("-t", "--times", type=int, help="Repeat for this many times")
@click.option("-c", "--continuous", is_flag=True, help="Runs forever allowing you to see values updating")
@click.option("-a", "--append", is_flag=True, help="Append the original output rather than overwriting it")
@click.option("-o", "--out", type=click.File("r+"), multiple=True, help="Path for the output CSV file. This can be used multiple times. use \'-\' as FILENAME for stdout") # Allow appending and seeking
@click.option("-d", "--delay", type=float, help="If running more than once, the seconds between each data request")
@click.option("-n", "--no_overtype", is_flag=True, help="Disables overwriting text when --times is greater than 1 or --continuous is set")

# Main program should run inside this block
def cli(version, url, ip, verbose, quiet, times, continuous, append, out, delay, no_overtype): # Any dashes are converted to underscores here
	# Arguments can't have helptext, so should be documented here
	'''ISIS Vista scraper\n
	Takes a hosted XML formatted for Vista and displays in in the terminal.
	Can run continuously and output to file.
	Work in progress...
	<celyn.walters@stfc.ac.uk>'''

	# Initialisation
	stringBuffer = "" # The strings waiting to be printed go in here
	indent = "   "
	headings = ["Timestamp"] # The rest of the column headings will be found on the first xml get
	if (times is None): times = 1 # We only want one reading
	if (delay is None): delay = 1 # In seconds
	winX = click.get_terminal_size()[0] # For wrapping. In here in case the window is resized

	#print("argc =", argc)
	if (ip is None):
		click.echo(click.Context.get_help(click.get_current_context()))
		sys.exit(0)

	# Only prints the string if verbose is True
	# Expects: Anything you can put in 'print()'
	def debug(*args):
		if (verbose): echo_temp(*args)

	# Stores the string in a global buffer and limits rows to the row height
	# Expects: Anything you can put in 'print()'
	def echo_temp(*args):
		nonlocal stringBuffer
		winY = click.get_terminal_size()[1]
		if (quiet):
			return
		lines = stringBuffer.count("\n")
		if (winY > lines+2) or (no_overtype): #TODO I think this '2' is how big your PS1 is??
			stringBuffer += " ".join(map(str, args))+"\n" # Emulates 'print()' behaviour for comma separated args
		elif (winY == lines+2):
			stringBuffer += "~~~ Output Truncated. Perhaps enable '--no_overtype' or allow more rows in your terminal ~~~\n"

	# Moves to cursor back to the location before the last loop iteration
	def flush_buffer():
		nonlocal stringBuffer
		if not (no_overtype):
			lines = stringBuffer.count("\n")
			if (ostype == "Windows"):
				os.system("cls") # For Windows cmd, clears entire scrollback
			else:
				# Only occurs when iteration > 0
				for i in range(0, lines): # Clear each line, ensures no 'layers' occur
					#\x1b["+num+"A")
					#TODO quitting whilst in here can leave some lines off
					sys.stdout.write("\x1b[1A") # Doesn't work on Windows cmd
					sys.stdout.write("\x1b[K") # Can use \033 but \x1b is googlable
		click.echo(stringBuffer, nl=False) # Prints
		stringBuffer = "" # The strings waiting to be printed go in here


	#TODO make this easier to read and follow
	debug("platform.system = "+ostype)
	if (ip):
		if not (url):
			url = "http://"+ip+"/cgi-bin/examples/database.vi?function=14"
		else:
			error_quit("URL and IP address both supplied")
	if (ostype == "Windows" and "SHELL" in os.environ) and (continuous or times > 1): # Doesn't handle SIGINT. 'os.environ' is sometimes case-sensitive
		error_quit("WARNING: Running in continuously in Cygwin using Windows Python can not be quit internally!")
	iteration = 0
	click.echo(stringBuffer, nl=False) # stringBuffer is about to be cleared, flush
	while (continuous or iteration < times):
		# Initialisations
		stringBuffer = ""
		debug("iteration:", iteration)
		row = []
		try:
			response = requests.get(url, timeout=1.0)
		except requests.exceptions.MissingSchema:
			error_quit("No URL or IP address supplied")
		except requests.exceptions.InvalidSchema:
			error_quit("Protocol unsupported")
		except requests.ConnectionError:
			error_quit("Connection error\nURL: "+url)
		except requests.HTTPError:
			error_quit("HTTPError\nURL: "+url)
		except requests.Timeout:
			error_quit("Request timed out\nURL: "+url)
		except requests.TooManyRedirects:
			error_quit("TooManyRedirects\nURL: "+url)
		except requests.RequestException as e:
			error_quit(e+"\nURL: "+url)
		except:
			error_quit("Requests module: Something went wrong\nURL: "+url)
		if (response.status_code != 200):
			error_quit("HTTP code "+str(response.status_code)+"\nURL: "+url)
		debug("XML received at: "+time.asctime())
		for line in (response.text+"\n").split("\n"): # Cannot use click.wrap_text on entire text and keep nice indentation
			debug(click.wrap_text(line, width=winX, initial_indent=indent, subsequent_indent=indent))
		#print url.replace('.com','')
		try:
			root = ET.fromstring(response.text)
		except ET.ParseError as e: error_quit("XML error:", e) #TODO print 'as e' in other places too?
		#root = ET.fromstring(response.content)
		# Store the values
		#TODO not many error checks in here...
		row.append(time.asctime()) #TODO custom display format
		codes = [] # Channel names. Called codes to mirror the XML
		values = []
		for channel in root.iter("channel"):
			code = channel.find("code")
			value = channel.find("value")
			array = channel.find("array")
			codes.append(code.text)
			if (value is not None):
				values.append(value.text)
			elif (array is not None):
				elementnum = 0
				elements = []
				for element in array.iter("element"):
					if (iteration == 0): headings.append(code.text+"["+str(elementnum)+"]")
					row.append(element.text)
					elementnum += 1
					elements.append(element.text)
				values.append(str(elements))
		# Print (and save) in easy-to-read order
		indexes = most_common(codes) # This is my function (see above)
		for i in indexes:
			if (values[i] is None): values[i] = ""
			echo_temp(click.wrap_text(codes[i]+" "+values[i], width=winX, subsequent_indent=indent))
			row.append(values[i])
			if (iteration == 0): headings.append(codes[i])
		for csvfile in out:
			try:
				writer = csv.writer(csvfile, dialect="excel", lineterminator="\n") # Avoids extra '\r' each row # TODO can I move this up?
				#TODO maybe use writer.writeheader
				#TODO double quotes can do new lines (hidden). Use this?
				if (iteration == 0) and not (append):
					csvfile.seek(0, 0)
					csvfile.truncate()
					writer.writerow(headings)
				csvfile.seek(0, 2)
				writer.writerow(row)
			except TypeError as e:
				click.echo(e)
				error_quit("Write error: \'"+csvfile.name+"\' may be open in another program")
		if (iteration > 0):
			if (no_overtype): stringBuffer = "\n"+stringBuffer # Seperate each scrape
			flush_buffer() # Prints stringBuffer after clearing screen
			if (iteration < times-1) or (continuous):
				time.sleep(delay) #TODO use time synchro rather than delay
		else:
			if (ostype == "Windows") and ((times > 1) or (continuous)) and not (no_overtype): # Running cmd, can only clear entire window, so do this first
				os.system("cls") # Clears cmd for first scrape
			click.echo(stringBuffer, nl=False) # Prints normally
			stringBuffer = ""
			if (times > 1) or (continuous):
				time.sleep(delay)
		iteration += 1
