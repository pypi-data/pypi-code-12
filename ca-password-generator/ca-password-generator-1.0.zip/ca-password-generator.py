# Password Generator

# Import modules
import argparse, string, random;

# Get arguments function
def getArguments():
	# Arguments
	parser = argparse.ArgumentParser();

	# Add argument (length)
	parser.add_argument('length', action = 'store', type = int, help = 'password length');

	# Add argument (passwords)
	parser.add_argument('-p', dest = 'passwords', action = 'store', type = int, help = 'number of passwords');

	# Add argument (uppercase)
	parser.add_argument('-u', dest = 'uppercase', action = 'store_true', help = 'use uppercase characters');

	# Add argument (lowercase)
	parser.add_argument('-l', dest = 'lowercase', action = 'store_true', help = 'use lowercase characters');

	# Add argument (default)
	parser.add_argument('-d', dest = 'default', action = 'store_true', help = 'use default settings')

	# Add argument (numbers)
	parser.add_argument('-n', dest = 'numbers', action = 'store_true', help = 'use numbers');

	# Add argument (symbols)
	parser.add_argument('-s', dest = 'symbols', action = 'store_true', help = 'use symbols');

	# Return all the arguments
	return parser.parse_args();

# Get characters function
def getCharacters(arguments):
	# Initialize characters
	characters = '';

	# Check if uppercase, lowercase, numbers or symbols arguments == true
	if (arguments.uppercase or arguments.lowercase or arguments.numbers or arguments.symbols):
		# Check if not default argument == true and add specified characters
		if not (arguments.default):
			if (arguments.uppercase):
				# Increment uppercase characters
				characters += string.ascii_uppercase;
			if (arguments.lowercase):
				# Increment lowercase characters
				characters += string.ascii_lowercase;
			if (arguments.numbers):
				# Increment number characters
				characters += string.digits;
			if (arguments.symbols):
				# Increment symbols characters
				characters += string.punctuation;
		# Use the default settings
		else:
			# Increment all characters
			characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation;
	# Use the default settings
	else:
		# Increment all characters
		characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + string.punctuation;

	# Return the characters
	return characters;

# Get passwords function
def getPasswords(characters, length, passwords):
	# Initialize passwords
	_passwords = '';

	# Loop
	for i in range(passwords):
		# Create the password (join random characters)
		password = ''.join(random.choice(characters) for i in range(length));

		# Check if not i == passwords - 1 (last password)
		if not (i == passwords - 1):
			# Insert enter
			_passwords += password + '\n';
		# If i == passwords - 1
		else:
			# Don't insert enter
			_passwords += password;

	# Return all the passwords
	return _passwords;

# Get arguments
arguments = getArguments();

# Get characters
characters = getCharacters(arguments);

# Check if not default argument == true or passwords argument == None
if not (arguments.default or arguments.passwords == None):
	# Get passwords
	passwords = getPasswords(characters, arguments.length, arguments.passwords);
# If default argument == true or passwords argument == None
else:
	# Get passwords (default)
	passwords = getPasswords(characters, arguments.length, 5);

# Print all the passwords
print(passwords);