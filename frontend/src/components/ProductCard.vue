<template>
    <router-link :to="{ name: 'Product', params: { id: product.id } }" class="product-card">
      <div class="product-card__image-wrapper">
        <img
          :src="imageUrl"
          :alt="product.name"
          class="product-card__image"
          @error="onImageError"
          loading="lazy"
        />
        <!-- Можно добавить лейбл "Скидка", если product.on_sale === true -->
        <span v-if="product.on_sale" class="product-card__sale-badge">Скидка!</span>
      </div>
      <div class="product-card__info">
        <h3 class="product-card__name">{{ product.name }}</h3>
        <div class="product-card__price">
          <!-- Показываем цену со скидкой, если она есть, и перечеркнутую старую -->
          <span v-if="product.on_sale && product.sale_price" class="product-card__sale-price">
            {{ formatPrice(product.sale_price) }} ₽
          </span>
          <span
            :class="{ 'product-card__regular-price--crossed': product.on_sale && product.sale_price }"
            class="product-card__regular-price"
          >
             {{ formatPrice(product.regular_price) }} ₽
          </span>
        </div>
         <!-- Можно добавить кнопку "В корзину" прямо сюда -->
        <!-- <button @click.prevent="addToCartHandler" class="product-card__add-button">
          В корзину
        </button> -->
      </div>
    </router-link>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  // import { useCartStore } from '@/store/cart'; // Если кнопка "В корзину" будет здесь
  
  // Пропсы компонента
  const props = defineProps({
    product: {
      type: Object,
      required: true,
    },
  });
  
  // Placeholder изображение, если у товара нет картинки или она не загрузилась
  const placeholderImage = '/placeholder.png'; // Положите placeholder.png в папку public/
  
  // Вычисляемое свойство для URL изображения с обработкой отсутствия
  const imageUrl = computed(() => {
    return props.product.images && props.product.images.length > 0
      ? props.product.images[0].src
      : placeholderImage;
  });
  
  // Обработчик ошибки загрузки изображения
  const onImageError = (event) => {
    event.target.src = placeholderImage;
  };
  
  // Функция для форматирования цены (простая)
  const formatPrice = (price) => {
    const number = parseFloat(price);
    return isNaN(number) ? '?' : number.toLocaleString('ru-RU'); // Формат для России
  };
  
  // Логика добавления в корзину (если кнопка здесь)
  // const cartStore = useCartStore();
  // const addToCartHandler = () => {
  //   cartStore.addToCart(props.product, 1);
  //   // Можно показать уведомление
  //   console.log(`${props.product.name} добавлен в корзину`);
  // };
  </script>
  
  <style scoped>
  .product-card {
    display: block; /* Чтобы router-link вел себя как блок */
    border: 1px solid var(--tg-theme-secondary-bg-color, #eee);
    border-radius: 8px;
    overflow: hidden;
    background-color: var(--tg-theme-secondary-bg-color, #fff); /* Фон карточки */
    transition: box-shadow 0.2s ease-in-out;
    text-decoration: none; /* Убрать подчеркивание у ссылки */
    color: var(--tg-theme-text-color, #222); /* Цвет текста */
  }
  
  .product-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  .product-card__image-wrapper {
    position: relative; /* Для позиционирования бэйджа */
    width: 100%;
    /* Пропорциональный контейнер для изображения (например, 1:1) */
    padding-top: 100%; /* Соотношение сторон 1:1 */
    background-color: var(--tg-theme-bg-color, #f9f9f9); /* Фон для незагруженных картинок */
  }
  
  .product-card__image {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover; /* Масштабирует изображение, сохраняя пропорции */
    display: block;
  }
  
  .product-card__sale-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    background-color: #dc3545; /* Красный цвет для скидки */
    color: white;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8em;
    font-weight: bold;
  }
  
  .product-card__info {
    padding: 10px 12px;
  }
  
  .product-card__name {
    font-size: 0.95em;
    font-weight: 600;
    margin-bottom: 8px;
    /* Ограничение текста в 2 строки */
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    min-height: 2.4em; /* Примерная высота для 2 строк */
  }
  
  .product-card__price {
    margin-bottom: 8px;
    display: flex;
    align-items: baseline; /* Выровнять цены по базовой линии */
    flex-wrap: wrap; /* Перенос цен, если не влезают */
    gap: 8px; /* Отступ между ценами */
  }
  
  .product-card__sale-price {
    font-size: 1em;
    font-weight: bold;
    color: var(--tg-theme-text-color); /* Основной цвет текста для акцентной цены */
  }
  
  .product-card__regular-price {
    font-size: 0.9em;
    color: var(--tg-theme-hint-color, #888); /* Приглушенный цвет для обычной цены */
  }
  
  .product-card__regular-price--crossed {
    text-decoration: line-through; /* Перечеркнуть старую цену */
  }
  
  .product-card__add-button {
    width: 100%;
    padding: 8px;
    font-size: 0.9em;
    margin-top: auto; /* Прижать кнопку к низу, если карточка flex */
  }
  </style>