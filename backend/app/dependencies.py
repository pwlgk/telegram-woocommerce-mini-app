# backend/app/dependencies.py
from datetime import datetime, timezone
from fastapi import Request, HTTPException, status, Depends, Header
from typing import Annotated, Dict, Optional

from app.services.woocommerce import WooCommerceService, WooCommerceServiceError
from app.services.telegram import TelegramService, TelegramNotificationError
from app.utils.telegram_auth import validate_init_data, TelegramAuthError # Импортируем
from app.core.config import settings

# --- Зависимости для сервисов ---

async def get_woocommerce_service(request: Request) -> WooCommerceService:
    """Зависимость для получения экземпляра WooCommerceService из app.state."""
    service = getattr(request.app.state, 'woocommerce_service', None)
    if not service or not isinstance(service, WooCommerceService):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис WooCommerce недоступен."
        )
    return service

async def get_telegram_service(request: Request) -> TelegramService:
    """Зависимость для получения экземпляра TelegramService из app.state."""
    service = getattr(request.app.state, 'telegram_service', None)
    if not service or not isinstance(service, TelegramService):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Сервис Telegram недоступен."
        )
    return service

# --- Зависимость для валидации Telegram initData ---

async def validate_telegram_data(
    x_telegram_init_data: Annotated[Optional[str], Header(description="Строка initData из Telegram Mini App")] = None
) -> Dict:
    """
    Зависимость для валидации заголовка X-Telegram-Init-Data.
    Возвращает распарсенные и валидированные данные пользователя или вызывает HTTPException.
    """
    if not x_telegram_init_data:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отсутствует заголовок X-Telegram-Init-Data.",
        )

    is_valid, parsed_data = validate_init_data(
        init_data=x_telegram_init_data,
        bot_token=settings.TELEGRAM_BOT_TOKEN
    )

    if not parsed_data: # Ошибка парсинга или внутренняя ошибка валидатора
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка обработки данных аутентификации Telegram.",
        )

    if not is_valid:
        # Проверяем, был ли хеш неверным или данные просто устарели
        auth_ts = int(parsed_data.get('auth_date', 0))
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if now_ts - auth_ts > 3600: # Используем тот же max_age, что и в валидаторе
             detail = "Данные аутентификации Telegram устарели."
        else:
             detail = "Недействительные данные аутентификации Telegram (неверный хеш)."

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )

    # Достаем информацию о пользователе
    user_info = parsed_data.get('user')
    if not user_info or not isinstance(user_info, dict) or 'id' not in user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось извлечь информацию о пользователе Telegram из initData.",
        )

    # Возвращаем все распарсенные данные на случай, если нужны другие поля (start_param и т.д.)
    return parsed_data

# --- Пример использования зависимости валидации в эндпоинте: ---
# @router.post("/some_protected_route")
# async def protected_route(
#     telegram_data: Annotated[Dict, Depends(validate_telegram_data)],
#     # ... другие зависимости и параметры
# ):
#     user_info = telegram_data.get('user')
#     user_id = user_info.get('id')
#     # ... ваша логика
#     return {"message": f"Hello, user {user_id}!"}