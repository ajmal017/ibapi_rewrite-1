from pyrogram import Client, Filters
import queue


# Trida vytvori spojeni s Tg ktere je pote treba z vnejsi inicializovat
class TgWrapper:
  def __init__(self, tg_config, tg_queue):
    self.session = Client("my_session", tg_config['api_id'], tg_config['api_hash'])

    @self.session.on_message(Filters.chat(tg_config['chat_id']) & Filters.text)
    def echo(self, message):
      if message.text.startswith("🍏") or message.text.startswith("🍇"):
        tg_queue.put({'text': message.text, 'date': message.date})
      else:
        pass