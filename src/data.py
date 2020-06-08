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
                 "order_id integer PRIMARY KEY,"
                 "operace text,"
                 "ticker text,"
                 "expirace text,"
                 "typ text,"
                 "strike integer,"
                 "smer text,"
                 "mnozstvi integer,"
                 "nasobeni integer,"
                 "status text)")

  cursor.execute("CREATE TABLE IF NOT EXISTS historie("
                 "internal_id integer PRIMARY KEY AUTOINCREMENT ,"
                 "order_id integer,"
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
  connection.commit()


def db_set_position(diktator: dict):
  cursor.execute(
    "INSERT INTO pozice (order_id,operace,ticker,expirace,typ,strike,smer,mnozstvi,nasobeni,status) VALUES (?,?,?,?,"
    "?,?,?,?,?,?)",
    (diktator['order_id'], diktator['operace'], diktator['ticker'], diktator['expirace'], diktator['typ'],
     diktator['strike'], diktator['smer'], diktator['mnozstvi'], diktator['nasobeni'], diktator['vysledek'])
  )


def db_append_history(diktator: dict):
  cursor.execute(
    "INSERT INTO historie (order_id,operace,akce,ticker,expirace,typ,strike,smer,mnozstvi,cena,nasobeni,puvodni_zprava,cas_zpravy,cas_zpracovani,vysledek) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    (diktator['id'], diktator['operace'],  diktator['akce'], diktator['ticker'], diktator['expirace'],
     diktator['typ'], diktator['strike'], diktator['smer'], diktator['mnozstvi'], diktator['cena'],
     diktator['nasobeni'], diktator['puvodni_zprava'], diktator['cas_zpravy'], diktator['cas_zpracovani'],
     diktator['vysledek']))
  connection.commit()


init_db()

# TODO: Pridat exceptions