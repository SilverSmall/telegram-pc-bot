import telebot
import os
import subprocess
import psutil
from wakeonlan import send_magic_packet
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from threading import Thread

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
        KeyboardButton("🖱 Натиснути клавішу"),
        KeyboardButton("💡 Увімкнути комп'ютер")  # New button for turning on the PC
    ]
    markup.add(*buttons)
    return markup

# === Команди ===
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
            global shutdown_thread
            shutdown_thread = Thread(target=shutdown_in, args=(timer,))
            shutdown_thread.start()
        except ValueError:
            bot.send_message(message.chat.id, "❌ Будь ласка, введіть правильне число.")

def shutdown_in(timer):
    time.sleep(timer * 60)  # Wait for the specified time
    os.system('shutdown /s /t 1')  # Shutdown the system

# Увімкнення комп'ютера (Wake-on-LAN)
@bot.message_handler(func=lambda message: message.text == "💡 Увімкнути комп'ютер")
def wake_computer(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть MAC-адресу комп'ютера для пробудження (формат: XX:XX:XX:XX:XX:XX):")
        bot.register_next_step_handler(message, send_wake_packet)

def send_wake_packet(message):
    if is_admin(message):
        try:
            mac_address = message.text.strip()
            send_magic_packet(mac_address)
            bot.send_message(message.chat.id, f"✅ Відправлено сигнал для пробудження ПК з MAC-адресою {mac_address}.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")

# Перегляд процесів
@bot.message_handler(func=lambda message: message.text == "🔍 Перегляд процесів")
def list_processes(message):
    if is_admin(message):
        processes = [p.info for p in psutil.process_iter(attrs=['pid', 'name'])]
        process_list = "\n".join([f"{p['pid']} - {p['name']}" for p in processes])
        bot.send_message(message.chat.id, f"🔄 Список процесів:\n{process_list}")

# Інформація про ПК
@bot.message_handler(func=lambda message: message.text == "ℹ️ Інформація про ПК")
def system_info(message):
    if is_admin(message):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        bot.send_message(message.chat.id, f"💻 CPU: {cpu}%\n🖥 RAM: {ram}%\n💾 Диск: {disk}%")

# Відкриття програми
@bot.message_handler(func=lambda message: message.text == "📂 Відкрити програму")
def request_program_to_open(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть назву програми для відкриття:")
        bot.register_next_step_handler(message, open_program)

def open_program(message):
    if is_admin(message):
        try:
            os.startfile(message.text)
            bot.send_message(message.chat.id, f"✅ Програма {message.text} відкрита.")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Помилка: {str(e)}")

# Закриття програми
@bot.message_handler(func=lambda message: message.text == "🚫 Закрити програму")
def request_program_to_close(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "Введіть назву програми для закриття:")
        bot.register_next_step_handler(message, close_program)

# Закриття програми (Linux/Mac)
def close_program(message):
    if is_admin(message):
        try:
            os.system(f"pkill -f {message.text}")  # Use pkill instead of taskkill
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

# Перезавантаження комп'ютера
@bot.message_handler(func=lambda message: message.text == "🔄 Перезавантажити")
def restart_computer(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "🔄 Перезавантажую комп'ютер...")
        os.system('shutdown /r /t 1')

# Вимкнення комп'ютера (Linux/Mac)
@bot.message_handler(func=lambda message: message.text == "⚠️ Вимкнути")
def shutdown_computer(message):
    if is_admin(message):
        bot.send_message(message.chat.id, "🔴 Вимикаю комп'ютер...")
        os.system("sudo shutdown -h now")  # For Linux/Mac

# === Запуск бота ===
if __name__ == "__main__":
    print("Даров бандіти!")  # Виводиться при запуску бота
    bot.polling(none_stop=True)
