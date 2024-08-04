class TokenError(Exception):
    """Нет токена."""


class SendingError(Exception):
    """Ошибка отправки сообщения."""


class ConnectionError(Exception):
    """Ошибка запроса."""


class ResponseStatusError(Exception):
    """Не тот код ответа."""
