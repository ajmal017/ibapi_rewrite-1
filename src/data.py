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


def find_matching_position(diktator):
  ticker = diktator['ticker']
  expirace = diktator['expirace']
  typ = diktator['typ']
  strike = diktator['strike']
  cursor.execute("SELECT order_id, mnozstvi FROM pozice WHERE ticker = ? and expirace = ? and typ = ? and strike = ?",
                 (ticker, expirace, typ, strike))
  result = cursor.fetchall()
  if result:
    return result[0]
  else:
    return None


def db_set_position(diktator: dict):
  cursor.execute(
    "INSERT INTO pozice (order_id,operace,ticker,expirace,typ,strike,smer,mnozstvi,nasobeni,status) VALUES (?,?,?,?,"
    "?,?,?,?,?,?)",
    (diktator['order_id'], diktator['operace'], diktator['ticker'], diktator['expirace'], diktator['typ'],
     diktator['strike'], diktator['smer'], diktator['mnozstvi'], diktator['nasobeni'], diktator['vysledek'])
  )

def db_close_position(order_id, amount, result):
  position = cursor.execute("SELECT order_id, mnozstvi, nasobeni  FROM pozice WHERE order_id=%d" % order_id)
  position = cursor.fetchall()[0]

  to_sell = amount
  order_id = position[0]
  held = position[1]
  multiply = position[2]

  if to_sell > held:
    raise ValueError("Pokus o prodej vice kusu nez zbylo z predchozi objednavky")
  else:
    cursor.execute("UPDATE pozice SET mnozstvi=%d WHERE order_id=%d" % (held-to_sell,order_id))
    connection.commit()



def db_append_history(diktator: dict):
  cursor.execute(
    "INSERT INTO historie (order_id,operace,akce,ticker,expirace,typ,strike,smer,mnozstvi,cena,nasobeni,puvodni_zprava,cas_zpravy,cas_zpracovani,vysledek) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    (diktator['order_id'], diktator['operace'], diktator['akce'], diktator['ticker'], diktator['expirace'],
     diktator['typ'], diktator['strike'], diktator['smer'], diktator['mnozstvi'], diktator['cena'],
     diktator['nasobeni'], diktator['puvodni_zprava'], diktator['cas_zpravy'], diktator['cas_zpracovani'],
     diktator['vysledek']))
  connection.commit()


init_db()

# TODO: Pridat exceptions
# TODO: Pridat a integrovat columns pro cenu ze signalu a cenu skutecnou