import os
from threading import Thread
import telebot
from flask import Flask

TOKEN = "9175936387:AAFLLud8tp89eCqX6ScJiadB5FFLqt1GDHU"
bot = telebot.TeleBot(TOKEN)

ADMIN_USERNAMES = ["arimas2824", "akbarshox_lite"]
WEB_APP_URL = "https://magazin-taupe.vercel.app"

app = Flask(__name__)


@app.route("/")
def home():
  return "OK"


def run_web():
  app.run(host="0.0.0.0", port=7860)


@bot.message_handler(commands=["start"])
def send_welcome(message):
  markup = telebot.types.InlineKeyboardMarkup(row_width=2)
  btn_ru = telebot.types.InlineKeyboardButton(
      "🇷🇺 Русский", callback_data="lang_ru"
  )
  btn_uz = telebot.types.InlineKeyboardButton(
      "🇺🇿 O'zbekcha", callback_data="lang_uz"
  )
  markup.add(btn_ru, btn_uz)
  bot.send_message(
      message.chat.id,
      "Добро пожаловать, выберите язык.\nXush kelibsiz, tilni tanlang.",
      reply_markup=markup,
  )


@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def callback_language(call):
  if call.data == "lang_ru":
    bot.answer_callback_query(call.id, "Выбран русский язык 🇷🇺")
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🛍 Открыть каталог",
            web_app=telebot.types.WebAppInfo(url=WEB_APP_URL),
        )
    )
    bot.send_message(
        call.message.chat.id,
        "🎄 **Каталог новогодних игрушек:**",
        reply_markup=markup,
        parse_mode="Markdown",
    )
  elif call.data == "lang_uz":
    bot.answer_callback_query(call.id, "O'zbek tili tanlandi 🇺🇿")
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            "🛍 Katalogni ochish",
            web_app=telebot.types.WebAppInfo(url=WEB_APP_URL),
        )
    )
    bot.send_message(
        call.message.chat.id,
        "🎄 **Yangi yil o'yinchoqlari katalogi:**",
        reply_markup=markup,
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["web_app_data"])
def receive_web_app(message):
  user = message.from_user
  username = f"@{user.username}" if user.username else f"{user.first_name}"
  order_info = message.web_app_data.data
  
  report = (
      f"🚨 **НОВАЯ ЗАЯВКА!**\n\n"
      f"👤 Заказчик: {username}\n"
      f"🔗 Юзернейм: @{user.username if user.username else 'нет'}\n\n"
      f"{order_info}\n\n"
      f"📊 Статус: Ожидание ⏳"
  )
  
  admin_markup = telebot.types.InlineKeyboardMarkup(row_width=2)
  admin_markup.add(
      telebot.types.InlineKeyboardButton(
          "✅ Принять", callback_data="status_accepted"
      ),
      telebot.types.InlineKeyboardButton(
          "🔥 Готов", callback_data="status_ready"
      ),
  )

  bot.send_message(
      message.chat.id,
      "✅ Заказ успешно оформлен! Администраторы скоро свяжутся с вами."
  )

  for admin_username in ADMIN_USERNAMES:
      try:
          bot.send_message(
              f"@{admin_username}", 
              report, 
              reply_markup=admin_markup, 
              parse_mode="Markdown"
          )
      except Exception as e:
          print(f"Не удалось отправить админу {admin_username}: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("status_"))
def change_status(call):
  user = call.from_user
  if not user.username or user.username.lower() not in [
      a.lower() for a in ADMIN_USERNAMES
  ]:
    bot.answer_callback_query(
        call.id, "❌ У вас нет прав администратора!", show_alert=True
    )
    return
  
  new_status_text = (
      "Принят ✅" if call.data == "status_accepted" else "Готов 🔥"
  )
  bot.answer_callback_query(
      call.id,
      f"Статус изменен: {'Принят' if call.data == 'status_accepted' else 'Готов'}",
  )
  
  try:
    old_text = call.message.text
    lines = old_text.split("\n")
    updated_lines = [
        (
            f"📊 Статус: {new_status_text}"
            if line.startswith("📊 Статус:")
            else line
        )
        for line in lines
    ]
    new_text = "\n".join(updated_lines)
    
    admin_markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    admin_markup.add(
        telebot.types.InlineKeyboardButton(
            "✅ Принять", callback_data="status_accepted"
        ),
        telebot.types.InlineKeyboardButton(
            "🔥 Готов", callback_data="status_ready"
        ),
    )
    
    bot.edit_message_text(
        new_text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=admin_markup,
        parse_mode="Markdown",
    )
  except Exception as e:
    print(f"Ошибка обновления: {e}")


if __name__ == "__main__":
  web_thread = Thread(target=run_web)
  web_thread.start()
  bot.infinity_polling()
  
