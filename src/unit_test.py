import main
import data
import pytest


def test_transform_expiration_date():
  assert main.transform_expiration("Aug9'20") == "20200809", "Should be 20200809"


def test_digest_signal():
  assert main.parse_signal({'text': "🍏 Go TWLO May15'20 C-200 BUY 1 kontrakt za 332", 'date': "1234567"}) == {
      'operace': "open",
      'akce': "Go",
      'ticker': "TWLO",
      'expirace': "20200515",
      'typ': "C",
      'strike': "200",
      'smer': "BUY",
      'mnozstvi': "1",
      'cena': "332",
      'puvodni_zprava': "🍏 Go TWLO May15'20 C-200 BUY 1 kontrakt za 332",
      'cas_zpravy': "1234567"
    }


diktator = main.parse_signal({'text': "🍏 Go TWLO May15'20 C-200 BUY 1 kontrakt za 332", 'date': "1234567"})
diktator['nasobeni'] = 1
diktator['cas_zpracovani'] = "7654321"
diktator['vysledek'] = "Pozice zalozena."
diktator['id'] = 214
print(diktator)
data.db_append_history(diktator)
