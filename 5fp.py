import telebot
import wikipediaapi
import logging
import requests

TOKEN = '6661648795:AAH8YbU9Gmr4rv5xRco3bAcreAhb7y19gJU'

bot = telebot.TeleBot(TOKEN)

# Настройка логирования
logging.basicConfig(filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация объекта Wikipedia
wiki_wiki = wikipediaapi.Wikipedia('Your_User_Agent', 'ru')

# Получение информации о погоде
def get_weather(city):
    api_key = '5878e766d2eb77995a3384d912a79ad5'
    base_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    response = requests.get(base_url)
    data = response.json()
    if data['cod'] == 200:
        weather_desc = data['weather'][0]['description']
        temp = round(data['main']['temp'] - 273.15, 2)  # Конвертация в градусы Цельсия
        return f"Погода в {city}: {weather_desc}. Температура: {temp}°C"
    else:
        return "Извините, не могу получить информацию о погоде."


# Получение курса валюты
# Получение курса валюты и конвертация суммы
def send_exchange_rate(chat_id, currency_code):
    api_key = '76240424f472831fb409620e487d45d2' # my token

    # Используем USD как базовую валюту, чтобы получить курсы для различных валют по отношению к USD
    url = f'https://www.freeforexapi.com/api/live?pairs=USDRUB,{currency_code}USD&apikey={api_key}'

    try:
        exchange_data = requests.get(url).json()

        rub_rate = exchange_data['rates']['USDRUB']['rate']
        if currency_code != 'USD':
            other_rate = exchange_data['rates'][f'{currency_code}USD']['rate']
        else:
            other_rate = 1

        rate = rub_rate * other_rate

        exchange_message = f'Курс {currency_code} к RUB сейчас: {rate}'
        bot.send_message(chat_id, exchange_message)
    except Exception as e:
        print(f'Error fetching exchange rate data: {e}')
        bot.send_message(chat_id, 'Не удалось получить данные о курсе валюты. Убедитесь, что название валюты'
                                  ' введено верно. Пример: USD, EUR, GBP, CAD, PLN.')

def search_wikipedia(query):
    page = wiki_wiki.page(query)  # Getting Wikipedia page for the query

    if page.exists():
        title = page.title  # Title of the page
        summary = page.summary[0:60]  # Summary of the page (first 60 characters)
        url = page.fullurl  # URL of the page
        return f"Page - Title: {title}\nPage - Summary: {summary}\nPage - URL: {url}"
    else:
        return "Страницы не существует."



# Обработка команд /start и /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_message = (
        "Привет! Я чат-бот.\n"
        "Я могу помочь вам узнать погоду в городе или курс валюты.\n"
        "Просто напишите 'погода Город' или 'курс валюты Валюта1'.\n"
        "Или напишите интересующую вас вещь, а я найду ее страничку в Википедии."
    )
    bot.reply_to(message, welcome_message)

# Обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    if 'погода' in text:
        city = text.split('погода')[1].strip()
        weather_info = get_weather(city)
        bot.send_message(message.chat.id, weather_info)
        logger.info(f"Пользователь запросил погоду в городе {city}")
    elif 'курс валюты' in text:
        currency_code = text.replace('курс валюты', '').strip().upper()

        if not currency_code:
            bot.send_message(message.chat.id, "Пожалуйста, укажите код валюты. Например: 'курс валюты USD'")
            return

        send_exchange_rate(message.chat.id, currency_code)
        logger.info(f"Пользователь запросил курс валюты для {currency_code}")
    else:
        wikipedia_summary = search_wikipedia(text)
        bot.send_message(message.chat.id, wikipedia_summary)
        logger.info(f"Пользователь искал информацию в Википедии по запросу: '{text}'.")


# Запуск бота
bot.polling(none_stop=True)
