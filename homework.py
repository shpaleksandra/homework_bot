import logging
import os
from http import HTTPStatus
import requests

from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()


PRACTICUM_TOKEN = ''
TELEGRAM_TOKEN = ''
TELEGRAM_CHAT_ID = 

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    tokens = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    if not all(tokens):
        logging.critical('Не хватает токенов')
        raise Exception('Не хватает токенов')


def send_message(bot, message):
    ...


def get_api_answer(timestamp):
    try:
        responce = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
        if responce.status_code != HTTPStatus.OK:
            raise Exception('В запросе переданы некорректные данные')
        return responce.json()
    except requests.RequestException() as error:
        raise Exception(error)


def check_response(response):
    ...


def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    # Создаем объект класса бота
    bot = ...
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()
