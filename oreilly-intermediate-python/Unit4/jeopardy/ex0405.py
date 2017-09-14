#print dollar value and question and answer

import sqlite3

connection = sqlite3.connect("jeopardy.db")
cursor = connection.cursor()
cursor.execute("SELECT text, answer, value FROM clue LIMIT 10")
result = cursor.fetchall()
#print result
for clue in result:
	#[$200]
	#Question: asdg
	#Answer: What is :
	print "[$%s]\n, Question: %s, Answer: %s\n: "%(clue[2],clue[0], clue[1])
	#print clue

connection.close()