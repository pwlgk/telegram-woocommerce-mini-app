# backend/app/models/order.py
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, List, Optional
from app.models.common import MetaData # Импортируем общую модель MetaData

# Модели для СОЗДАНИЯ заказа
class BillingAddress(BaseModel):
    # Сделаем поля опциональными, т.к. основная связь через TG
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    # WooCommerce может требовать email для создания гостевого заказа,
    # можно использовать плейсхолдер или генерировать временный.
    email: Optional[EmailStr] = Field(None, description="Может быть обязательным для WC")
    phone: Optional[str] = None
    # Можно добавить address_1, city, postcode, country, state если нужно

class ShippingAddress(BillingAddress):
    pass

class LineItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0) # Количество должно быть больше 0
    variation_id: Optional[int] = None

class OrderCreateWooCommerce(BaseModel):
    payment_method: str = "cod" # Используем "cod" (Cash on delivery) как плейсхолдер
    payment_method_title: str = "Согласование с менеджером (Telegram)"
    set_paid: bool = False
    status: str = "on-hold" # Статус "На удержании"
    billing: Optional[BillingAddress] = None # Пока опционально
    shipping: Optional[ShippingAddress] = None # Пока опционально
    line_items: List[LineItemCreate]
    customer_note: Optional[str] = None
    customer_id: int = 0 # Гостевой заказ, не привязываем к WP пользователю
    meta_data: List[MetaData] = [] # Сюда добавим данные из Telegram

# Модель для ответа от WooCommerce ПОСЛЕ создания/получения заказа (упрощенная)
class OrderWooCommerce(BaseModel):
    id: int
    parent_id: int
    status: str
    currency: str
    total: str
    customer_id: int
    order_key: str
    billing: Optional[BillingAddress] = None
    shipping: Optional[ShippingAddress] = None
    payment_method: str
    payment_method_title: str
    transaction_id: Optional[str] = None
    customer_note: Optional[str] = None
    date_created: str # Дата приходит как строка
    line_items: List[Dict] # Ответ по line_items сложнее, пока оставим как Dict
    meta_data: List[MetaData] = []
    # ... другие поля по необходимости