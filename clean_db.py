import sqlite3

# Connect to the database
conn = sqlite3.connect('lost_and_found.db')
cursor = conn.cursor()

# Delete entries with leading or trailing spaces
cursor.execute("DELETE FROM users WHERE user_id LIKE '% ' OR user_id LIKE ' %'")
conn.commit()

# Display remaining users
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
print("Remaining users in database:")
for user in users:
    print(user)

conn.close()