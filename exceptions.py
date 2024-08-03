class TokenError(Exception):
    """Нет токена."""
    pass


class SendingError(Exception):
    """Ошибка отправки сообщения."""
    pass


class ConnectionError(Exception):
    """Не верный код ответа."""
    pass


class ResponseStatusError(Exception):
    """Не тот код ответа."""
    pass
