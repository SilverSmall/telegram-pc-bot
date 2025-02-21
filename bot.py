import telebot
import os
import subprocess
import psutil
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# === Налаштування ===
TOKEN = '7248122948:AAGZkQ5mK69HibnJfStldnd9FzsAgCk_ffA'
ADMIN_ID = 877365085  # Замініть на свій Telegram ID
bot = telebot.TeleBot(TOKEN)

def is_admin(message):
    return message.chat.id == ADMIN_ID

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("📸 Скриншот"),
        KeyboardButton("ℹ️ Інформація про ПК"),
        KeyboardButton("🔄 Перезавантажити"),
        KeyboardButton("⚠️ Вимкнути"),
        KeyboardButton("⏲️ Таймер вимкнення"),
        KeyboardButton("📂 Відкрити програму"),
        KeyboardButton("🚫 Закрити програму"),
        KeyboardButton("🔊 Управління звуком"),
        KeyboardButton("⌨️ Написати текст"),
        KeyboardButton("🖱 Натиснути клавішу")
    ]
    markup.add(*buttons)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "💻 Бот для керування ПК активний!", reply_markup=main_menu())
    else:
        bot.send_message(message.chat.id, "⛔ У вас немає доступу!")

# Таймер вимкнення
@bot.message_handler(func=lambda message: message.text == "⏲️ Таймер вимкнення")
def shutdown_timer(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть час до вимкнення (в хвилинах):")
        bot.register_next_step_handler(message, set_shutdown_timer)

def set_shutdown_timer(message):
    if is_admin(message):
        try:
            timer = int(message.text)
            bot.send_message(message.chat.id, f"Таймер вимкнення встановлено на {timer} хвилин.")
            time.sleep(timer * 60)  # Чекаємо заданий час
            os.system('shutdown /s /t 1')  # Вимикаємо комп'ютер
        except ValueError:
            bot.send_message(message.chat.id, "❌ Будь ласка, введіть правильне число.")

# Закриття програми
@bot.message_handler(func=lambda message: message.text == "🚫 Закрити програму")
def request_program_to_close(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть назву програми для закриття:")
        bot.register_next_step_handler(message, close_program)

def close_program(message):
    if is_admin(message):
        try:
            os.system(f"taskkill /f /im {message.text}")
            bot.send_message(message.chat.id, f"✅ Програму {message.text} закрито.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")

# Управління звуком
@bot.message_handler(func=lambda message: message.text == "🔊 Управління звуком")
def sound_control(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Виберіть дію зі звуком:", reply_markup=sound_menu())

def sound_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        KeyboardButton("🔊 Збільшити гучність"),
        KeyboardButton("🔉 Зменшити гучність"),
        KeyboardButton("🔇 Вимкнути звук")
    ]
    markup.add(*buttons)
    return markup


def increase_volume(message):
    if is_admin(message):
        subprocess.call(["amixer", "set", "Master", "2%+"])  # Збільшити на 2%
        bot.send_message(message.chat.id, "🔊 Гучність збільшено.")

def decrease_volume(message):
    if is_admin(message):
        subprocess.call(["amixer", "set", "Master", "2%-"])  # Зменшити на 2%
        bot.send_message(message.chat.id, "🔉 Гучність зменшено.")

def mute_volume(message):
    if is_admin(message):
        subprocess.call(["amixer", "set", "Master", "mute"])  # Вимкнути звук
        bot.send_message(message.chat.id, "🔇 Звук вимкнено.")

# Інші функції залишаються без змін...

# === Запуск бота ===
bot.polling(none_stop=True)
