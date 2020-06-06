import sqlite3

# globals
connection = None
cursor = None


def init_db():
  global connection
  global cursor
  connection = sqlite3.connect('storage.db')
  cursor = connection.cursor()
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
                 "internal_id integer PRIMARY KEY,"
                 "operace text,"
                 "akce text,"
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
                 "cas_zpracovani text,"
                 "vysledek text)")
  print("Tables checked and/or created")
  connection.commit()


def db_set_position(diktator: dict):
  #cursor.execute()
  pass


def db_append_history(diktator: dict):
  cursor.execute("INSERT INTO historie VALUES (%d,%s,%s,%s,%s,%s,%d,%s,%d,%d,%d,%s,%s,%s)"), \
  diktator['id'], diktator['akce'], diktator['operace'], diktator['ticker'], diktator['expirace'], \
  diktator['typ'], diktator['strike'], diktator['smer'], diktator['mnozstvi'], diktator['cena'], \
  diktator['nasobeni'], diktator['puvodni_zprava'], diktator['cas_zpravy'], diktator['cas_zpracovani']

