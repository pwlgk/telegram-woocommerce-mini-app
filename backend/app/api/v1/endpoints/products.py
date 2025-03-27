# backend/app/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional, Dict

from app.services.woocommerce import WooCommerceService, WooCommerceServiceError
from app.dependencies import get_woocommerce_service
# Можно импортировать модели Pydantic для response_model, если нужно
# from app.models.product import Product, Category

router = APIRouter()

@router.get(
    "/",
    # response_model=List[Product],
    summary="Получить список товаров",
    description="Получает список товаров из WooCommerce с пагинацией, фильтрацией и сортировкой.",
)
async def get_products_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество товаров на странице"),
    category: Optional[str] = Query(None, description="ID или slug категории"),
    search: Optional[str] = Query(None, description="Поисковый запрос"),
    featured: Optional[bool] = Query(None, description="Фильтр по избранным"),
    on_sale: Optional[bool] = Query(None, description="Фильтр по товарам со скидкой"),
    orderby: str = Query('date', description="Поле сортировки"),
    order: str = Query('desc', description="Направление сортировки (asc, desc)"),
    wc_service: WooCommerceService = Depends(get_woocommerce_service),
):
    try:
        products = await wc_service.get_products(
            page=page,
            per_page=per_page,
            category=category,
            search=search,
            featured=featured,
            on_sale=on_sale,
            orderby=orderby,
            order=order,
        )
        # Проверяем, что результат не None (хотя сервис теперь выбрасывает исключения)
        if products is None:
             # Эта ветка маловероятна при использовании исключений, но оставим для надежности
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Товары не найдены.")
        return products
    except WooCommerceServiceError as e:
        # Ловим ошибку от нашего сервиса
        raise HTTPException(status_code=e.status_code or 503, detail=e.message)
    except Exception as e:
        # Ловим другие непредвиденные ошибки
        # Логирование здесь не нужно, т.к. оно будет в middleware или FastAPI по умолчанию
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера при получении товаров.")


@router.get(
    "/{product_id}",
    # response_model=Product,
    summary="Получить товар по ID",
    description="Получает детальную информацию о конкретном товаре.",
)
async def get_product_details(
    product_id: int,
    wc_service: WooCommerceService = Depends(get_woocommerce_service),
):
    try:
        product = await wc_service.get_product(product_id)
        if product is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товар с ID {product_id} не найден.")
        return product
    except WooCommerceServiceError as e:
        # Если get_product вернул ошибку 404 от WC, она будет перехвачена здесь
        status_code = e.status_code or 503
        if status_code == 404:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Товар с ID {product_id} не найден.") from e
        else:
             raise HTTPException(status_code=status_code, detail=e.message) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Внутренняя ошибка сервера при получении товара.")

