import os
import sys
import time
import datetime
import traceback
import data
from tws import EjPiPi
from telegram import TgWrapper
from order_manager import OrderManager
import queue

# Globalni konstanty
MONTHS = {
  'Jan': "01",
  'Feb': "02",
  'Mar': "03",
  'Apr': "04",
  'May': "05",
  'Jun': "06",
  'Jul': "07",
  'Aug': "08",
  'Sep': "09",
  'Oct': "10",
  'Nov': "11",
  'Dec': "12"
}

# Globalni fronty
tg_queue = queue.Queue()
tws_queue = queue.Queue()

# Hodnoty nemenne za chodu programu - konfigurace
tg_config = {
  'chat_id': -1001222852629,
  'api_id': 1281725,
  'api_hash': "6d5593e5f014de19ab29e96dec9c5fec"
}
excel_config = {
  'file': "/home/ktbsh/tmp/orders.xlsx"
}
tws_config = {
  'nasobeni': 3,
  'typ_objednavky': "MKT",  # Muze byt MIT nebo MKT
  'ip': "127.0.0.1",
  'port': 7497
}


# Pomocne funkce pro transformaci dat, nemeni stav programu

def transform_expiration(date):  # Prelozi expiraci z formatu May1'19 do 20190501
  month = date[:3]
  if "'" in date:
    day, year = date[3:].split("'")
  elif "-" in date:
    day, year = date[3:].split("-")
  else:
    raise ValueError("Chyba formatu expirace v signalu")
  if int(day) < 10:
    day = "0%d" % int(day)
  return "20%s%s%s" % (year, MONTHS[month], day)


def parse_signal(signal):  # Prijme text a datum zpravy z telegramu jako dict, vrati slovnik z prijatych parametru
  try:
    signal_text = signal['text']
    signal_date = signal['date']
    parts = signal_text.split()
    if parts[0] == u"\U0001F34F":  # jablko
      parts[0] = "open"
    elif parts[0] == u"\U0001F347":  # hrozen
      parts[0] = "close"
    processed_signal = {
      'operace': parts[0],  # Open/Close pro otevreni/uzavreni pozice
      'akce': parts[1],  # Go/Close - duplikat, info
      'ticker': parts[2],  # Symbol
      'expirace': transform_expiration(parts[3]),  # Expirace ve formatu YYYYMMDD (String)
      'typ': parts[4].split("-")[0],  # Right (Call/Put)
      'strike': parts[4].split("-")[1],  # Hodnota strike
      'smer': parts[5],  # Action (BUY/SELL) - podle otevreni/uzavreni pozice
      'mnozstvi': int(parts[6]),  # Quantity
      'cena': int(parts[9]),  # Cena signalu
      'skutecna_cena': float(0),
      'nasobeni': tws_config['nasobeni'],
      'puvodni_zprava': signal_text,
      'cas_zpravy': datetime.datetime.fromtimestamp(signal_date),
      'order_id': 0,
      'cas_zpracovani': "Nebylo zpracovano",
      'vysledek': "V objednavce nastala chyba",
      'order_type': tws_config['typ_objednavky']
    }
    return processed_signal
  except Exception as ee:
    raise ValueError("Nelze zpracovat signal - chyba formatu zpravy", ee)
    # https://stackoverflow.com/questions/2052390/manually-raising-throwing-an-exception-in-python


# Funkce pro komunikaci s TWS modulem TODO: Presunout do tws modulu


def process_order(signal):
  if signal['operace'] == "open":  # Odesli objednavku podle signalu
    print("ODESILAM OBJEDNAVKU: ", signal['puvodni_zprava'])

    signal['vysledek'], signal['order_id'], signal['skutecna_cena'] = tws_client.send_order(signal)
    data.db_set_position(signal)
    signal['cas_zpracovani'] = datetime.datetime.now()

  elif signal['operace'] == "close":  # Zkontroluj otevrene pozice a pripadne uzavri, odecti/odstran aktivni stav v db
    print("RUSIM POZICI: ", signal['puvodni_zprava'])

    id, active_positions = data.find_matching_position(signal)
    # TODO: Vratit nasobic pozice a nastavit do signalu
    if id and active_positions >= signal['mnozstvi']:
      signal['vysledek'], signal['order_id'], signal['skutecna_cena'] = tws_client.send_order(signal)
      signal['cas_zpracovani'] = datetime.datetime.now()
      data.db_close_position(id, signal['mnozstvi'])
    else:
      print("Neni dostatek aktivnich pozic pro uzavreni (pozice zalozene uzivatelem nejsou zahrnuty)")
      # TODO: Pridat do vysledku


# Instance klientu pro komunikaci s TG a TWS
def get_clients():
  tg_client = TgWrapper(tg_config, tg_queue).session
  tws_client = EjPiPi(tws_config['ip'], tws_config['port'], 0, tws_queue)
  return tg_client, tws_client


# Hlavni event loop programu

def the_loop():
  while True:
    try:
      time.sleep(1)
      if not tg_queue.empty():
        orderman.updateOrders()
        raw_signal = tg_queue.get(timeout=5)
        signal_dict = parse_signal(raw_signal)
        orderman.createOrder(signal_dict)

        # process_order(signal_dict)
        # data.db_append_history(signal_dict)
        # print('Signal "%s" zpracovan s nasledujicimi parametry:' % signal_dict['puvodni_zprava'])
        # print("Operace: ", signal_dict['operace'])
        # print("Mnozstvi:", int(signal_dict['mnozstvi'])*int(signal_dict['nasobeni']))
        # print("Cena (signal/skutecnost): %d/%d" % (signal_dict['cena'], signal_dict['skutecna_cena']))
        # print("Vysledek: %s - ID: %d" % (signal_dict['vysledek'], signal_dict['order_id']))
    except Exception as loop_error:
      tg_client.send_message("me", "CHYBA: %s" % loop_error)


if __name__ == "__main__":
  print("Spoustim pripojeni k API")
  try:
    tg_client, tws_client = get_clients()

    orderman = OrderManager(tws_client, tws_queue)

    tg_client.start()
    # TODO: Vytvorit sjednocenou inicializacni metodu obsahujici server clock a ID printout
    while tws_client.is_error():
      print(tws_client.get_error())
    tws_client.refresh_next_id()
  except Exception as e:
    print("[CHYBA!]: Nepovedlo se pripojit k TWS nebo Telegramu")
    traceback.print_exc()

  the_loop()
