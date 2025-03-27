# backend/app/core/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from dotenv import load_dotenv

# Загружаем переменные из .env файла в окружение
# Это нужно, если вы запускаете скрипт напрямую,
# uvicorn/gunicorn часто делают это автоматически, если python-dotenv установлен
load_dotenv()

class Settings(BaseSettings):
    # --- General Settings ---
    PROJECT_NAME: str = "WooCommerce Telegram Mini App Backend"
    API_V1_STR: str = "/api/v1"
    # Настройте уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    LOGGING_LEVEL: str = os.getenv("LOGGING_LEVEL", "INFO")

    # --- WooCommerce Settings ---
    WOOCOMMERCE_URL: str = "https://your-wordpress-site.com" # !!! ЗАМЕНИТЬ В .env !!!
    WOOCOMMERCE_KEY: str = "ck_dummykey" # !!! ЗАМЕНИТЬ В .env !!!
    WOOCOMMERCE_SECRET: str = "cs_dummysecret" # !!! ЗАМЕНИТЬ В .env !!!
    WOOCOMMERCE_API_VERSION: str = "wc/v3"

    # --- Telegram Settings ---
    TELEGRAM_BOT_TOKEN: str = "YOUR_BOT_TOKEN" # !!! ЗАМЕНИТЬ В .env !!!
    # ID менеджеров через запятую в .env, например: 123456,789012
    TELEGRAM_MANAGER_IDS_STR: str = "123456789" # !!! ЗАМЕНИТЬ В .env !!!
    MINI_APP_URL: str = "https://your-frontend-app-url.com" # !!! ЗАМЕНИТЬ В .env !!!

    # --- Derived/Helper Settings ---
    @property
    def TELEGRAM_MANAGER_IDS(self) -> List[int]:
        """Преобразует строку ID менеджеров в список целых чисел."""
        try:
            return [int(uid.strip()) for uid in self.TELEGRAM_MANAGER_IDS_STR.split(',') if uid.strip()]
        except ValueError:
            # Логирование или обработка ошибки, если ID некорректны
            print("ERROR: Invalid TELEGRAM_MANAGER_IDS format in .env. Please provide comma-separated integers.")
            return []

    # Настройки для Pydantic Settings
    model_config = SettingsConfigDict(
        env_file='.env',              # Указываем имя файла .env
        env_file_encoding='utf-8',    # Кодировка файла
        case_sensitive=False,         # Имена переменных окружения не чувствительны к регистру
        extra='ignore'                # Игнорировать лишние переменные в окружении
    )

# Создаем экземпляр настроек, который будет использоваться в приложении
settings = Settings()

# Проверка при старте (опционально, но полезно)
if "dummy" in settings.WOOCOMMERCE_KEY or "dummy" in settings.WOOCOMMERCE_SECRET:
    print("WARNING: WooCommerce API keys seem to be using default dummy values. Please update them in your .env file.")
if "YOUR_BOT_TOKEN" in settings.TELEGRAM_BOT_TOKEN:
    print("WARNING: Telegram Bot Token is not set. Please update it in your .env file.")
if "your-frontend-app-url.com" in settings.MINI_APP_URL:
    print("WARNING: MINI_APP_URL is not set. Please update it in your .env file.")
if not settings.TELEGRAM_MANAGER_IDS:
     print("WARNING: TELEGRAM_MANAGER_IDS list is empty or invalid. Notifications will not be sent.")