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
                 "id integer PRIMARY KEY AUTOINCREMENT ,"
                 "ticker text,"
                 "expirace text,"
                 "typ text,"
                 "strike integer,"
                 "mnozstvi integer,"
                 "nasobeni integer)")

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


def find_matching_position(diktator):  # Vrati interni id a mnozstvi
  ticker = diktator['ticker']
  expirace = diktator['expirace']
  typ = diktator['typ']
  strike = diktator['strike']
  cursor.execute("SELECT id, mnozstvi FROM pozice WHERE ticker = ? and expirace = ? and typ = ? and strike = ?",
                 (ticker, expirace, typ, strike))
  result = cursor.fetchall()
  print(result)
  if result:
    print(result[0])
    return result[0]
  else:
    return None, None


def db_set_position(diktator: dict):
  id, amt = find_matching_position(diktator)
  if id:
    cursor.execute("UPDATE pozice SET mnozstvi=%d WHERE id=%d" % (amt + diktator['mnozstvi'], id))
  else:
    cursor.execute(
      "INSERT INTO pozice (ticker,expirace,typ,strike,mnozstvi,nasobeni) VALUES (?,?,?,?,?,?)",
      (diktator['ticker'], diktator['expirace'], diktator['typ'],
       diktator['strike'], diktator['mnozstvi'], diktator['nasobeni'])
    )
  connection.commit()


def db_close_position(id, to_sell):
  cursor.execute("SELECT mnozstvi, nasobeni FROM pozice WHERE id=%d" % id)
  position = cursor.fetchall()[0]
  print(position)

  held = position[0]
  to_hold = held - to_sell
  if to_hold < 0:
    raise ValueError("Pokus o prodej vice kusu nez zbylo z predchozi objednavky")
  elif to_hold == 0:
    cursor.execute("DELETE FROM pozice WHERE id=%d" % id)
    pass
  else:
    cursor.execute("UPDATE pozice SET mnozstvi=%d WHERE id=%d" % (to_hold, id))
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
