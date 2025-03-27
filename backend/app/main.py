# backend/app/main.py
import logging
import asyncio # <<<<<<<<<<<< Импортируем asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.api.v1.router import api_router_v1
from app.core.config import settings
from app.services.woocommerce import WooCommerceService
from app.services.telegram import TelegramService
from app.bot.instance import initialize_bot, shutdown_bot

# --- Настройка логирования ---
log_level = settings.LOGGING_LEVEL.upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
# >>>>>>>>>> Повысим уровень логов aiogram для отладки <<<<<<<<<<
logging.getLogger("aiogram").setLevel(logging.INFO) # Можно поставить DEBUG для большей детализации

logger = logging.getLogger(__name__)
logger.info(f"Starting application with log level: {log_level}")


# --- Lifespan для управления ресурсами ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: Initializing resources...")
    bot, dp = await initialize_bot()
    woo_service = WooCommerceService()
    telegram_service = TelegramService(bot=bot)

    app.state.woocommerce_service = woo_service
    app.state.telegram_service = telegram_service
    app.state.bot_instance = bot
    app.state.dispatcher_instance = dp

    logger.info("WooCommerce service, Telegram service, Bot, and Dispatcher initialized.")

    # >>>>>>>>>> Запускаем polling в фоновой задаче <<<<<<<<<<
    logger.info("Starting bot polling in background...")
    # Пропускаем старые апдейты, чтобы не реагировать на /start, отправленный до запуска
    polling_task = asyncio.create_task(dp.start_polling(bot, skip_updates=True))
    # >>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    try:
        yield # Приложение работает здесь
    finally:
        # Код, выполняемый при остановке приложения
        logger.info("Application shutdown: Cleaning up resources...")

        # >>>>>>>>>> Останавливаем polling <<<<<<<<<<
        if polling_task and not polling_task.done():
             logger.info("Stopping bot polling...")
             polling_task.cancel()
             try:
                 # Даем задаче шанс завершиться корректно
                 await asyncio.wait_for(polling_task, timeout=5.0)
             except asyncio.CancelledError:
                 logger.info("Bot polling task cancelled.")
             except asyncio.TimeoutError:
                 logger.warning("Bot polling task did not finish in time.")
             except Exception as e:
                  logger.exception(f"Error stopping polling task: {e}")
        # >>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<

        # Закрываем HTTP клиент WooCommerce
        await woo_service.close_client()
        # Корректно останавливаем сессию бота
        await shutdown_bot(bot=app.state.bot_instance)
        logger.info("Resources cleaned up successfully.")

# --- Создание экземпляра FastAPI (остальной код без изменений) ---
# ... (FastAPI initialization, CORS, Error Handlers, Routers, Root endpoint) ...
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API бэкенд для Telegram Mini App магазина WooCommerce.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

origins = [
    settings.MINI_APP_URL,
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "null",
]
logger.info(f"Allowed CORS origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "X-Telegram-Init-Data"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Более подробное логирование ошибок валидации Pydantic
    logger.warning(f"Request validation error: {exc.errors()} for {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Ошибка валидации входных данных", "errors": exc.errors()},
    ) # <<< Проверьте эту строку

@app.exception_handler(ValidationError) # Ошибки валидации Pydantic внутри кода
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    logger.error(f"Pydantic model validation error: {exc.errors()} for {request.method} {request.url}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ошибка валидации данных", "errors": exc.errors()},
    ) # <<< Проверьте эту строку

@app.exception_handler(Exception) # Обработчик для всех остальных исключений
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc} for {request.method} {request.url}") # Логируем с traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Внутренняя ошибка сервера."},
    ) # <<< Проверьте эту строку - особенно отступ и закрывающие скобки
    
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
logger.info(f"Included API router at prefix: {settings.API_V1_STR}")

@app.get("/", tags=["Root"], summary="Health check")
async def read_root():
    """Простой эндпоинт для проверки работоспособности API."""
    return {"status": "ok", "project": settings.PROJECT_NAME}