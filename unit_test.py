import main
import pytest


def test_transform_expiration_date():
  assert main.transform_expiration("Aug9'20") == "20200809", "Should be 20200809"


def test_digest_signal():
  assert main.digest_signal("🍏 Go TWLO May15'20 C-200 BUY 1 kontrakt za 332") == {
      'emoji': "🍏",
      'akce': "Go",
      'ticker': "TWLO",
      'expirace': "20200515",
      'typ': "C",
      'strike': "200",
      'smer': "BUY",
      'mnozstvi': "1",
      'cena': "332"
    }
