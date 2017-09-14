#goal print categories from jeapardy database

import sqlite3

connection = sqlite3.connect("jeopardy.db")
cursor = connection.cursor()
cursor.execute("SELECT name FROM category LIMIT 12")
result = cursor.fetchall()
for games in result:
	print str(games[0])
connection.close()	

