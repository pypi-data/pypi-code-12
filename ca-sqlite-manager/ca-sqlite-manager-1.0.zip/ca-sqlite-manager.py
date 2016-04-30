# SQLite Manager

# Import module
import sqlite3;

# Connect function (send database name and return connection)
def connect (databaseName):
	connection = sqlite3.connect(databaseName);
	return connection;

# Execute function (send connection and query | return connection.execute())
def execute (connection, query):
	if not query.startswith('select'):
		# Execute query
		connection.execute(query);

		# Commit changes
		connection.commit();
	else:
		return connection.execute(query);

# Call connect function and save the return value to connection
connection = connect('databases/sqlite-manager.db');

# Confirm database connection
print('Database: Connected');
print();

# Create table "websites" in database
execute(connection, 'create table websites (id int primary key not null, title text not null, url text not null);');

# Confirm table "websites" creation
print('Table "websites": Created');

# Insert data (Twitter)
execute(connection, 'insert into websites (id, title, url) values (1, "Twitter", "https://twitter.com/caffealgorithm");');

# Insert data (Google+)
execute(connection, 'insert into websites (id, title, url) values (2, "Google+", "https://plus.google.com/+CaffeineAlgorithm");');

# Confirm insert data
print('Table "websites": Data Inserted');
print();

# Select data
cursor = execute(connection, 'select id, title, url from websites;');

# Run and show all row data in cursor
for row in cursor:
	# Print row data
	print(row);

# Confirm select data
print('\nTable "websites": Data selected');

# Update data (Twitter)
execute(connection, 'update websites set url = "twitter.com/caffealgorithm" where id = 1;');

# Update data (Google+)
execute(connection, 'update websites set url = "plus.google.com/+CaffeineAlgorithm" where id = 2;');

# Confirm update data
print('Table "websites": Data updated');

# Delete data
execute(connection, 'delete from websites where id = 1;');

# Confirm delete data
print('Table "websites": Data deleted');

# Close database connection
connection.close();

# Confirm database close connection
print();
print('Database: Disconnected');