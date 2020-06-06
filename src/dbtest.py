import sqlite3
from sqlite3 import Error


connection = None
cursor = None
try:
  connection = sqlite3.connect('cleanliness.db')
  cursor = connection.cursor()
except Error:
  raise Error

if cursor:
  cursor.execute("CREATE TABLE IF NOT EXISTS pozice("
                 "id integer PRIMARY KEY,"
                 "operace text,"
                 "ticker text,"
                 "expirace text,"
                 "typ text,"
                 "strike integer,"
                 "smer text,"
                 "mnozstvi integer,"
                 "nasobeni integer)")

  cursor.execute("CREATE TABLE IF NOT EXISTS historie("
                 "id integer PRIMARY KEY,"
                 "akce text,"
                 "operace text,"
                 "ticker text,"
                 "expirace text,"
                 "typ text,"
                 "strike integer,"
                 "smer text,"
                 "mnozstvi integer,"
                 "cena integer,"
                 "nasobeni integer,"
                 "puvodni_zprava text,"
                 "cas_zpravy text,"
                 "cas_zpracovani text)")

connection.commit()
connection.close()