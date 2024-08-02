import logging
import os
from http import HTTPStatus
import requests
import time

import telebot
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)


def check_tokens():
    """Проверка доступности переменных окружения."""
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(tokens):
        logging.critical('Не хватает токенов')
        raise Exception('Не хватает токенов')


def send_message(bot, message):
    """Отправление сообщений в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение отправлено.')
    except (telebot.apihelper.ApiException,
            requests.RequestException) as error:
        logging.error(f'Сообщение не отправлено: {error}')


def get_api_answer(timestamp):
    """Запрос к API-сервису."""
    try:
        responce = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if responce.status_code != HTTPStatus.OK:
            raise Exception('Не удалось сделать запрос')
        return responce.json()
    except requests.RequestException() as error:
        raise Exception(error)


def check_response(response):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        raise TypeError('Неверный тип.')
    if 'homeworks' not in response:
        raise KeyError('homeworks отсутствует.')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Неверный тип.')


def parse_status(homework):
    """Извлечение статуса работы."""
    if not isinstance(homework, dict):
        raise TypeError('Неверный тип.')
    if 'homework_name' not in homework:
        raise KeyError('В домашке нет ключа `homework_name`.')
    homework_name = homework['homework_name']
    status = homework['status']
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Недокументированный статус работы.')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response['homeworks']
            if not homeworks:
                logging.debug('Статус не изменен.')
            homework = homeworks[0]
            if status == homework['status']:
                logging.debug('Статус не изменен.')
                continue
            message = parse_status(homework)
            send_message(bot, message)
            status = homework['status']
            timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
