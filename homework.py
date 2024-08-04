import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telebot
from dotenv import load_dotenv

import exceptions

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
    tokens = (
        (PRACTICUM_TOKEN, 'PRACTICUM_TOKEN'),
        (TELEGRAM_TOKEN, 'TELEGRAM_TOKEN'),
        (TELEGRAM_CHAT_ID, 'TELEGRAM_CHAT_ID')
    )
    all_tokens = True
    missing_tokens = []
    for token, token_name in tokens:
        if not token:
            all_tokens = False
            missing_tokens.append(token_name)
    if not all_tokens:
        return missing_tokens


def send_message(bot, message):
    """Отправление сообщений в чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except (telebot.apihelper.ApiException,
            requests.RequestException) as error:
        logging.error(f'Сообщение не отправлено: {error}')
        raise exceptions.SendingError(f'Сообщение не отправлено: {error}')
    else:
        logging.debug('Сообщение отправлено.')


def get_api_answer(timestamp):
    """Запрос к API-сервису."""
    params_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp}
        )
    except requests.RequestException:
        raise exceptions.ConnectionError(
            'Неверный код ответа. Параметры запроса: url = {url},'
            'headers = {headers},'
            'params = {params}'.format(**params_request)
        )
    if response.status_code != HTTPStatus.OK:
        raise exceptions.ResponseStatusError('Не удалось сделать запрос')
    return response.json()


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
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Недокументированный статус работы.')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens():
        logging.critical('Отсутствуют токены:', check_tokens())
        sys.exit()
    bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status = ''
    last_message = ''
    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            homeworks = response.get('homeworks')
            if not homeworks:
                logging.debug('Нет новых работ.')
                send_message(bot, 'Нет новых работ')
            else:
                homework = homeworks[0]
                new_status = parse_status(homework)
                if status == new_status:
                    logging.debug('Статус не изменен.')
                else:
                    message = parse_status(homework)
                    if send_message(bot, message):
                        status = homework.get('status')
                        timestamp = response.get('current_date', timestamp)
                    else:
                        logging.error('Сообщение не отправлено')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if last_message != message:
                send_message(bot, message)
                logging.error(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        filemode='w',
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()
