# Morse Code Translator

# Import module
import argparse;

# Get arguments function
def getArguments():
	# Arguments
	parser = argparse.ArgumentParser();

	# Add argument (message)
	parser.add_argument('-m', dest = 'message', action = 'store', type = str, help = 'message (input)');

	# Add argument (file input)
	parser.add_argument('-fi', dest = 'fileInput', action = 'store', type = str, help = 'file (input)');

	# Add argument (file output)
	parser.add_argument('-fo', dest = 'fileOutput', action = 'store', type = str, help = 'file (output)');

	# Return all the arguments
	return parser.parse_args();

# Translate message function
def translateMessage(morseCode, arguments):
	# Show message
	print('Message:', arguments.message);

	# Show translated message
	print('Translated message: ', end = '');

	# For each character in message
	for character in arguments.message:
		# If the character is in the dictionary
		if character.upper() in morseCode:
			# Print translated character
			print(morseCode[character.upper()], end = ' ');
		# Else if character is a space
		elif character == ' ':
			# Print symbol
			print('| ', end = '');
		# Else
		else:
			# Print character
			print(character, end = '');

	# Print new line
	print();

# Translate file function
def translateFile(morseCode, arguments):
	# Print the input filename
	print('File input:', arguments.fileInput);

	# Print the output filename
	print('File output:', arguments.fileOutput);

	# Open input file to read the content
	fileInput = open(arguments.fileInput, 'r');

	# Open output file to write the translated content
	fileOutput = open(arguments.fileOutput, 'w');

	# For each line in input file
	for line in fileInput:
		# For each character in line
		for character in line:
			# If the character is in the dictionary
			if character.upper() in morseCode:
				# Write translated character
				fileOutput.write(morseCode[character.upper()]);

				# Write space
				fileOutput.write(' ');
			# Else if character is a space
			elif character == ' ':
				# Write symbol
				fileOutput.write('| ');
			# Else
			else:
				# Write character
				fileOutput.write(character);

	# Close input file
	fileInput.close();

	# Close output file
	fileOutput.close();

# Dictionary
morseCode = {
	# Alphabet
	'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 'G': '--.', 'H': '....', 'I': '..',
	'J': '.---', 'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
	'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--', 'Z': '--..',

	# Numbers
	'0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
	'9': '----.',

	# Symbols
	'.': '.-.-.-', ',': '--..--', '?': '..--..', '\'': '.----.', '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
	'&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-', '_': '..--.-', '\"': '.-..-.',
	'$': '...-..-', '@': '.--.-.'
};

# Get arguments
arguments = getArguments();

# If -m, -fi and -fo
if arguments.message and arguments.fileInput and arguments.fileOutput:
	# Call the function to translate the message
	translateMessage(morseCode, arguments);

	# Call the function to translate the file
	translateFile(morseCode, arguments);

# Else if -fi and -fo
elif arguments.fileInput and arguments.fileOutput:
	# Call the function to translate the file
	translateFile(morseCode, arguments);

# Else if -m
elif arguments.message:
	# Call the function to translate the message
	translateMessage(morseCode, arguments);

# Else
else:
	# Print possible combinations of arguments
	print('Possible combinations of arguments:\n');
	print('  - MESSAGE                       \"-m ...\";');
	print('  - FILEINPUT FILEOUTPUT          \"-fi ... -fo ...\";');
	print('  - MESSAGE FILEINPUT FILEOUTPUT  \"-m ... -fi ... -fo ...\";');
	print('\nUse \"-h\"" for more information...');