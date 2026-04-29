import sqlite3

# Connect to the database
conn = sqlite3.connect('lost_and_found.db')
cursor = conn.cursor()

# Check users table
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
print('Users in database:')
for user in users:
    print(user)

# Check admins table
cursor.execute('SELECT * FROM admins')
admins = cursor.fetchall()
print('\nAdmins in database:')
for admin in admins:
    print(admin)

conn.close()