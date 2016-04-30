# SQLite Manager (Menu)

# Import module
import sqlite3;

# Connect function (send database name and return connection)
def connect (databaseName):
	connection = sqlite3.connect('databases/' + databaseName + '.db');
	return connection;

# Execute function (send connection and query)
def execute (connection, query):
	if query.startswith('select'):
		# Select data
		cursor = connection.execute(query);

		# Run and show all row data in cursor
		for row in cursor:
			# Print row data
			print(row);
	else:
		# Execute query
		connection.execute(query);

		# Commit changes
		connection.commit();

# Initialize the loop
isLooping = True;

# Enter database name
databaseName = input('Enter database name: ');

# Call connect function and save the return value to connection
connection = connect(databaseName);

# Loop
while isLooping:
	# Menu
	print('\nDatabase: Connected')
	print('Database name: ' + databaseName + '.db');
	print('------------------------------------------');
	print('[Press 1] - Database query');
	print('[Press 0] - Close connection');

	# Enter the number
	choice = input('\nPress the number you want and press enter: ');

	# Choices
	if choice == '1':
		# Initialize the loop
		isQuerying = True;

		# Loop
		while isQuerying:
			# Enter the query
			query = input('Enter the query (write 'stop' to stop writing queries): ');

			if query == 'stop':
				# Stop loop
				isQuerying = False;
			else:
				# Execute query
				execute(connection, query);

	elif choice == '0':
		# Close database connection
		connection.close();

		# Confirm database close connection
		print('Database: Disconnected');

		# Stop loop
		isLooping = False;
	else:
		# Warning
		print('You need to try again.');