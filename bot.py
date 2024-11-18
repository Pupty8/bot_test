import logging
import requests
import pdfplumber
from io import BytesIO
import telebot

API_TOKEN = '' # мой токен
bot = telebot.TeleBot(API_TOKEN)

PDF_URL = 'https://aitanapa.ru/download/%d1%80%d0%b0%d1%81%d0%bf%d0%b8%d1%81%d0%b0%d0%bd%d0%b8%d0%b5/?wpdmdl=970&refresh=673b6bdf508e11731947487'

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_schedule_from_pdf():
    try:
        response = requests.get(PDF_URL)
        response.raise_for_status()

        # Сохранение PDF в памяти
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            schedule = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    schedule.append(text)

        return schedule
    except Exception as e:
        logger.error(f"Ошибка при загрузке PDF: {str(e)}")
        return f"Ошибка: {str(e)}"

@bot.message_handler(commands=['schedule_pdf'])
def send_schedule_pdf(message):
    schedule = get_schedule_from_pdf()
    if isinstance(schedule, str):
        bot.send_message(message.chat.id, f"Ошибка: {schedule}")
    else:
        response_message = "Расписание (PDF):\n"
        for page_text in schedule:
            response_message += page_text + "\n\n"

        with open('schedule.txt', 'w', encoding='utf-8') as file:
            file.write(response_message)
        
        with open('schedule.txt', 'rb') as file:
            bot.send_document(message.chat.id, file)

        import os
        os.remove('schedule.txt')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Используй команду /schedule_pdf, чтобы получить расписание из PDF.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
