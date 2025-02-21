import telebot
import os
import subprocess
import psutil
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# === Налаштування ===
TOKEN = '7248122948:AAGZkQ5mK69HibnJfStldnd9FzsAgCk_ffA'
ADMIN_ID = 877365085   # Замініть на свій Telegram ID
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
        KeyboardButton("📂 Відкрити програму"),
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

@bot.message_handler(func=lambda message: message.text == "📸 Скриншот")
def screenshot(message):
    if is_admin(message):
        path = 'screenshot.png'
        pyautogui.screenshot().save(path)
        with open(path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo)
        os.remove(path)

@bot.message_handler(func=lambda message: message.text == "⚠️ Вимкнути")
def shutdown(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "⚠️ Вимикаю комп’ютер...")
        os.system('shutdown /s /t 5')

@bot.message_handler(func=lambda message: message.text == "🔄 Перезавантажити")
def reboot(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "🔄 Перезавантажую комп’ютер...")
        os.system('shutdown /r /t 5')

@bot.message_handler(func=lambda message: message.text == "ℹ️ Інформація про ПК")
def system_info(message):
    if is_admin(message):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        battery_percent = battery.percent if battery else 'N/A'
        bot.send_message(message.chat.id, f"💻 CPU: {cpu}%\n🖥 RAM: {ram}%\n🔋 Battery: {battery_percent}%")

@bot.message_handler(func=lambda message: message.text == "📂 Відкрити програму")
def request_program(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть назву програми для відкриття:")
        bot.register_next_step_handler(message, open_program)

def open_program(message):
    if is_admin(message):
        try:
            subprocess.Popen(message.text, shell=True)
            bot.send_message(message.chat.id, f'✅ Відкрито: {message.text}')
        except Exception as e:
            bot.send_message(message.chat.id, f'❌ Помилка: {str(e)}')

@bot.message_handler(func=lambda message: message.text == "⌨️ Написати текст")
def request_text(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть текст для друку:")
        bot.register_next_step_handler(message, write_text)

def write_text(message):
    if is_admin(message):
        pyautogui.write(message.text)
        bot.send_message(message.chat.id, "📝 Надруковано: " + message.text)

@bot.message_handler(func=lambda message: message.text == "🖱 Натиснути клавішу")
def request_key(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть клавішу для натискання:")
        bot.register_next_step_handler(message, press_key)

def press_key(message):
    if is_admin(message):
        pyautogui.press(message.text)
        bot.send_message(message.chat.id, f'🔘 Натиснута клавіша: {message.text}')

# === Запуск бота ===
bot.polling(none_stop=True)
