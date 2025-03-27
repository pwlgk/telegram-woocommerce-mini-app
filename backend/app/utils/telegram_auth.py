# backend/app/utils/telegram_auth.py
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Tuple, Any
from urllib.parse import unquote, parse_qsl

from app.core.config import settings

logger = logging.getLogger(__name__)

class TelegramAuthError(Exception):
    """Custom exception for Telegram authentication errors."""
    pass

def parse_init_data(init_data: str) -> Dict[str, Any]:
    """
    Парсит строку initData в словарь, корректно обрабатывая URL-кодированные значения,
    включая вложенный JSON в поле 'user'.
    """
    parsed_data = {}
    # parse_qsl сохраняет порядок и обрабатывает дубликаты (хотя их не должно быть в initData)
    for key, value in parse_qsl(init_data):
        # Декодируем значение из URL-формата
        decoded_value = unquote(value)
        # Особая обработка для поля 'user' и 'receiver', которые содержат JSON
        if key in ('user', 'receiver', 'chat') and decoded_value.startswith('{') and decoded_value.endswith('}'):
            try:
                parsed_data[key] = json.loads(decoded_value)
            except json.JSONDecodeError:
                logger.warning(f"Failed to decode JSON for key '{key}' in initData: {decoded_value[:100]}...")
                parsed_data[key] = decoded_value # Оставляем как строку в случае ошибки
        else:
            parsed_data[key] = decoded_value
    return parsed_data

def validate_init_data(
    init_data: str,
    bot_token: str,
    max_age_seconds: int = 3600 # 1 час
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Валидирует строку initData, полученную от Telegram Web App.

    Args:
        init_data: Строка initData (window.Telegram.WebApp.initData).
        bot_token: Секретный токен Telegram бота.
        max_age_seconds: Максимально допустимый возраст данных в секундах.

    Returns:
        Кортеж (is_valid: bool, parsed_data: Optional[Dict]).
        parsed_data содержит расшифрованные данные, если валидация прошла успешно
        (даже если данные устарели или хеш не совпал).
    """
    try:
        # 1. Парсим строку initData
        parsed_data = parse_init_data(init_data)
        if not parsed_data or 'hash' not in parsed_data:
            raise TelegramAuthError("Invalid initData structure or missing hash.")

        received_hash = parsed_data.pop('hash')

        # 2. Проверяем возраст данных (поле auth_date)
        if 'auth_date' in parsed_data:
            try:
                # auth_date это Unix timestamp в секундах
                auth_timestamp = int(parsed_data['auth_date'])
                # Получаем текущее время UTC
                current_timestamp = int(datetime.now(timezone.utc).timestamp())
                time_diff = current_timestamp - auth_timestamp

                if time_diff < 0:
                     logger.warning(f"initData auth_date is in the future? Auth: {auth_timestamp}, Now: {current_timestamp}")
                     # Можно считать это ошибкой
                     # raise TelegramAuthError("Authentication date is in the future.")
                elif time_diff > max_age_seconds:
                    logger.warning(f"initData is too old. Age: {time_diff}s, Max allowed: {max_age_seconds}s")
                    # Данные устарели, но хеш все равно проверим, вернем False
                    # raise TelegramAuthError(f"Data is outdated (age: {time_diff}s > {max_age_seconds}s)")
                    # Не вызываем ошибку, просто вернем is_valid=False
                else:
                     logger.debug(f"initData age is valid: {time_diff}s")

            except (ValueError, TypeError) as e:
                raise TelegramAuthError(f"Invalid auth_date format: {parsed_data.get('auth_date')}. Error: {e}")
        else:
            # Отсутствие auth_date делает невозможным проверку возраста
            raise TelegramAuthError("auth_date field is missing in initData.")

        # 3. Формируем строку для проверки хеша
        # Ключи сортируются в алфавитном порядке
        data_check_string_parts = [f"{key}={value}" for key, value in sorted(parsed_data.items())]
        data_check_string = "\n".join(data_check_string_parts)
        logger.debug(f"Data check string:\n{data_check_string}")

        # 4. Вычисляем хеш
        # Секретный ключ - это HMAC-SHA256 от токена бота с солью "WebAppData"
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        # 5. Сравниваем хеши
        if calculated_hash == received_hash:
            logger.info("initData validation successful.")
            # Проверяем возраст еще раз, чтобы вернуть корректный флаг is_valid
            auth_ts = int(parsed_data.get('auth_date', 0))
            now_ts = int(datetime.now(timezone.utc).timestamp())
            if now_ts - auth_ts > max_age_seconds:
                return False, parsed_data # Хеш верный, но данные старые
            return True, parsed_data
        else:
            logger.warning(f"initData validation FAILED! Hash mismatch.")
            logger.debug(f"Calculated Hash: {calculated_hash}")
            logger.debug(f"Received Hash:   {received_hash}")
            # Не вызываем ошибку, просто вернем is_valid=False
            return False, parsed_data

    except TelegramAuthError as e:
        logger.error(f"Telegram authentication error: {e}")
        return False, parsed_data if 'parsed_data' in locals() else None # Возвращаем распарсенные данные, если есть
    except Exception as e:
        logger.exception(f"Unexpected error during initData validation: {e}") # Логируем с traceback
        return False, None