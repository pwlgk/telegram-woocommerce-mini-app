# backend/app/services/woocommerce.py
import httpx
import logging
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel
from app.core.config import settings
from app.models.product import Product, Category
from app.models.order import OrderCreateWooCommerce, OrderWooCommerce

# Настройка логирования
logging.basicConfig(level=settings.LOGGING_LEVEL.upper())
logger = logging.getLogger(__name__)

class WooCommerceServiceError(Exception):
    """Базовый класс для ошибок сервиса WooCommerce."""
    def __init__(self, message="Ошибка при взаимодействии с WooCommerce API", status_code=None, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)

class WooCommerceService:
    """
    Асинхронный сервис для взаимодействия с WooCommerce REST API.
    """
    def __init__(self):
        self.base_url = f"{settings.WOOCOMMERCE_URL.rstrip('/')}/wp-json/{settings.WOOCOMMERCE_API_VERSION}"
        self.auth = (settings.WOOCOMMERCE_KEY, settings.WOOCOMMERCE_SECRET)
        # Используем таймауты для предотвращения зависания запросов
        timeouts = httpx.Timeout(10.0, read=20.0, write=10.0, connect=5.0)
        # Используем AsyncClient для переиспользования соединений
        self._client = httpx.AsyncClient(base_url=self.base_url, auth=self.auth, timeout=timeouts)
        logger.info(f"WooCommerceService initialized for URL: {self.base_url}")

    async def close_client(self):
        """Закрывает httpx клиент."""
        if hasattr(self, '_client') and self._client:
            await self._client.aclose()
            logger.info("WooCommerce HTTP client closed.")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Union[Dict, BaseModel]] = None
    ) -> Optional[Any]:
        """
        Внутренний метод для выполнения запросов к API с обработкой ошибок.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        payload = None
        if json_data:
             # Если передана Pydantic модель, преобразуем в словарь
            if isinstance(json_data, BaseModel):
                 payload = json_data.model_dump(exclude_unset=True, by_alias=True) # exclude_unset - не отправлять None
            else:
                 payload = json_data

        try:
            logger.debug(f"Requesting {method} {endpoint} | Params: {params} | Payload: {payload}")
            response = await self._client.request(method, endpoint, params=params, json=payload)

            # Проверяем статус ответа
            response.raise_for_status() # Выбросит HTTPStatusError для 4xx/5xx

            # Некоторые запросы (DELETE) могут не возвращать тело
            if response.status_code == 204: # No Content
                logger.debug(f"Received {response.status_code} No Content for {method} {endpoint}")
                return True # Успех без данных

            # Проверяем Content-Type, чтобы убедиться, что это JSON
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                 logger.warning(f"Unexpected Content-Type '{content_type}' for {method} {endpoint}. Response text: {response.text[:500]}...")
                 # Можно вернуть как текст или вызвать ошибку
                 # raise WooCommerceServiceError("Non-JSON response received", status_code=response.status_code, details=response.text)
                 return response.text # Возвращаем текст как есть

            response_data = response.json()
            logger.debug(f"Received {response.status_code} response for {method} {endpoint}") # Логируем только статус успеха

            return response_data

        except httpx.HTTPStatusError as e:
            # Ошибка от сервера (4xx, 5xx)
            error_details = e.response.text
            try:
                # Пытаемся извлечь сообщение об ошибке из JSON ответа WC
                wc_error = e.response.json()
                error_message = wc_error.get("message", "No error message in response")
                error_code = wc_error.get("code", "unknown_error_code")
                logger.error(f"WooCommerce API error: {e.response.status_code} {error_code} - {error_message} for {e.request.url}")
                raise WooCommerceServiceError(
                    message=f"Ошибка WooCommerce: {error_message}",
                    status_code=e.response.status_code,
                    details=wc_error
                ) from e
            except (ValueError, KeyError):
                 # Если ответ не JSON или структура другая
                 logger.error(f"HTTP error: {e.response.status_code} for {e.request.url}. Response: {error_details[:500]}...")
                 raise WooCommerceServiceError(
                     message=f"HTTP ошибка {e.response.status_code} от WooCommerce API",
                     status_code=e.response.status_code,
                     details=error_details
                 ) from e

        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e} for {e.request.url}")
            raise WooCommerceServiceError("Превышен таймаут запроса к WooCommerce API") from e
        except httpx.RequestError as e:
            # Ошибка сети или соединения
            logger.error(f"Network error: {e} for {e.request.url}")
            raise WooCommerceServiceError("Ошибка сети при подключении к WooCommerce API") from e
        except Exception as e:
             # Другие непредвиденные ошибки
             logger.exception(f"Unexpected error during WooCommerce request to {endpoint}: {e}")
             raise WooCommerceServiceError("Непредвиденная ошибка при работе с WooCommerce API") from e

    # --- Методы для получения данных ---

    async def get_products(
        self,
        page: int = 1,
        per_page: int = 10,
        category: Optional[str] = None,
        search: Optional[str] = None,
        status: str = 'publish',
        featured: Optional[bool] = None,
        on_sale: Optional[bool] = None,
        orderby: str = 'date',
        order: str = 'desc',
        **kwargs # Дополнительные параметры API WC
    ) -> Optional[List[Dict]]: # Пока возвращаем Dict для гибкости
        """Получает список товаров из WooCommerce."""
        params = {
            'page': page,
            'per_page': per_page,
            'status': status,
            'orderby': orderby,
            'order': order,
            'category': category,
            'search': search,
            'featured': featured,
            'on_sale': on_sale,
            **kwargs
        }
        # Убираем None значения
        params = {k: v for k, v in params.items() if v is not None}

        logger.info(f"Fetching products with params: {params}")
        # Тут можно обернуть в try/except и вернуть None или пустой список при ошибке,
        # либо пробросить исключение WooCommerceServiceError наверх (в эндпоинт)
        return await self._request("GET", "products", params=params)

    async def get_product(self, product_id: int) -> Optional[Dict]:
        """Получает детальную информацию о товаре по ID."""
        logger.info(f"Fetching product with ID: {product_id}")
        return await self._request("GET", f"products/{product_id}")

    async def get_categories(
        self,
        per_page: int = 100,
        parent: Optional[int] = None,
        orderby: str = 'name',
        order: str = 'asc',
        hide_empty: bool = True, # Скрывать пустые категории
        **kwargs
    ) -> Optional[List[Dict]]:
        """Получает список категорий товаров."""
        params = {
            'per_page': per_page,
            'parent': parent,
            'orderby': orderby,
            'order': order,
            'hide_empty': hide_empty,
            **kwargs
        }
        params = {k: v for k, v in params.items() if v is not None}
        logger.info(f"Fetching categories with params: {params}")
        return await self._request("GET", "products/categories", params=params)

    # --- Метод для создания заказа ---

    async def create_order(self, order_data: OrderCreateWooCommerce) -> Optional[Dict]:
        """
        Создает новый заказ в WooCommerce.
        :param order_data: Pydantic модель OrderCreateWooCommerce с данными заказа.
        :return: Словарь с данными созданного заказа или пробрасывает WooCommerceServiceError.
        """
        logger.info(f"Attempting to create order...")
        # Валидация данных через Pydantic модель уже произошла при ее создании

        # Используем _request для отправки данных, он обработает ошибки
        created_order_data = await self._request("POST", "orders", json_data=order_data)

        if created_order_data and isinstance(created_order_data, dict):
            order_id = created_order_data.get('id')
            logger.info(f"Order created successfully with ID: {order_id}")
            # Тут можно валидировать ответ через OrderWooCommerce.model_validate(created_order_data)
            return created_order_data
        else:
            # _request должен был выбросить исключение при ошибке, но на всякий случай
            logger.error(f"Failed to create order. Received unexpected response: {created_order_data}")
            raise WooCommerceServiceError(
                "Не удалось создать заказ или получен некорректный ответ от WooCommerce",
                details=created_order_data
            )

