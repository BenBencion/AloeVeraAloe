from datetime import datetime
import telebot

# Твой токен бота
api_id = 34096249
api_hash = '2c7bde0885bafb5ecb20d8cbf29d421d'

TOKEN = '8258065758:AAF6tc5-4reHZNQGRE2XdOVPkCUZcpJVMo4'
bot = telebot.TeleBot(TOKEN)

# Текущее локальное время
now = datetime.now()

# Форматируем время красиво
time_str = now.strftime("🕒 Сейчас: %d.%m.%Y %H:%M:%S")

# Отправляем в канал
try:
    bot.send_message("@BurkinaFaso11", time_str)
    print("Сообщение отправлено!")
except Exception as e:
    print("Ошибка:", e)