<template>
    <div class="cart-item">
      <!-- Изображение товара -->
      <router-link :to="{ name: 'Product', params: { id: item.product_id } }" class="cart-item__image-link">
        <img :src="imageUrl" :alt="item.name" class="cart-item__image" @error="onImageError">
      </router-link>
  
      <!-- Информация о товаре -->
      <div class="cart-item__details">
        <router-link :to="{ name: 'Product', params: { id: item.product_id } }" class="cart-item__name-link">
          <span class="cart-item__name">{{ item.name }}</span>
           <!-- Можно добавить ID вариации, если нужно -->
          <!-- <span v-if="item.variation_id" class="cart-item__variation"> (Var: {{ item.variation_id }})</span> -->
        </router-link>
        <span class="cart-item__price-per-unit">{{ formatPrice(item.price) }} ₽ / шт.</span>
  
        <!-- Управление количеством -->
        <div class="cart-item__quantity-controls">
          <button @click="decreaseQuantity" :disabled="localQuantity <= 1" class="quantity-btn">-</button>
          <input
             type="number"
             v-model.number="localQuantity"
             @change="updateQuantityHandler"
             @blur="validateQuantityOnBlur"
             min="1"
             class="quantity-input"
          >
          <button @click="increaseQuantity" class="quantity-btn">+</button>
        </div>
      </div>
  
      <!-- Общая стоимость и кнопка удаления -->
      <div class="cart-item__actions">
        <span class="cart-item__total-price">{{ formatPrice(itemTotalPrice) }} ₽</span>
        <button @click="removeItem" class="remove-btn" title="Удалить товар">
          × <!-- Крестик -->
        </button>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, watch } from 'vue';
  import { useCartStore } from '@/store/cart';
  
  const props = defineProps({
    item: {
      type: Object,
      required: true,
    },
  });
  
  const cartStore = useCartStore();
  
  // Локальное состояние для количества, чтобы избежать прямого изменения стора из input
  const localQuantity = ref(props.item.quantity);
  
  // Наблюдаем за изменением количества в сторе (если оно изменится извне)
  watch(() => props.item.quantity, (newQuantity) => {
    if (newQuantity !== localQuantity.value) {
      localQuantity.value = newQuantity;
    }
  });
  
  // Placeholder изображение
  const placeholderImage = '/placeholder.png';
  
  const imageUrl = computed(() => {
    return props.item.image || placeholderImage;
  });
  
  const onImageError = (event) => {
    event.target.src = placeholderImage;
  };
  
  // Форматирование цены
  const formatPrice = (price) => {
    const number = parseFloat(price);
    return isNaN(number) ? '?' : number.toLocaleString('ru-RU');
  };
  
  // Общая стоимость для этой позиции
  const itemTotalPrice = computed(() => {
    const price = parseFloat(props.item.price) || 0;
    return (price * localQuantity.value).toFixed(2);
  });
  
  // --- Управление количеством ---
  const decreaseQuantity = () => {
    if (localQuantity.value > 1) {
      localQuantity.value--;
      updateQuantityHandler();
    }
  };
  
  const increaseQuantity = () => {
    localQuantity.value++;
    updateQuantityHandler();
  };
  
  // Валидация и обновление количества в сторе
  const updateQuantityHandler = () => {
     validateQuantity(); // Сначала валидируем
     if (localQuantity.value !== props.item.quantity) {
          cartStore.updateQuantity(props.item.product_id, localQuantity.value, props.item.variation_id);
     }
  };
  
  // Дополнительная валидация при потере фокуса input'ом
  const validateQuantityOnBlur = () => {
      validateQuantity();
      updateQuantityHandler(); // Принудительно обновить, если значение было некорректным и исправилось
  };
  
  const validateQuantity = () => {
      if (localQuantity.value < 1 || !Number.isInteger(localQuantity.value) || isNaN(localQuantity.value)) {
          localQuantity.value = 1; // Возвращаем к минимуму
      }
      // Можно добавить проверку на максимальное количество, если оно есть
  };
  
  // Удаление товара
  const removeItem = () => {
    cartStore.removeFromCart(props.item.product_id, props.item.variation_id);
    // Можно добавить уведомление об удалении
  };
  </script>
  
  <style scoped>
  .cart-item {
    display: flex;
    align-items: flex-start; /* Выровнять по верху */
    padding: 1rem 0;
    border-bottom: 1px solid var(--tg-theme-secondary-bg-color, #eee);
    gap: 1rem; /* Отступ между блоками */
  }
  .cart-item:last-child {
      border-bottom: none;
  }
  
  .cart-item__image-link {
    flex-shrink: 0; /* Не сжимать блок с картинкой */
  }
  
  .cart-item__image {
    display: block;
    width: 70px;
    height: 70px;
    object-fit: cover;
    border-radius: 8px;
    background-color: var(--tg-theme-secondary-bg-color, #f1f1f1);
  }
  
  .cart-item__details {
    flex-grow: 1; /* Занимать основное пространство */
    display: flex;
    flex-direction: column;
    gap: 0.3rem; /* Небольшой отступ между элементами */
  }
  
  .cart-item__name-link {
      text-decoration: none;
      color: var(--tg-theme-text-color);
  }
  .cart-item__name-link:hover .cart-item__name {
      color: var(--tg-theme-link-color);
  }
  
  .cart-item__name {
    font-weight: 600;
    font-size: 1em;
    /* Ограничение имени в 2 строки */
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: color 0.2s;
  }
  .cart-item__variation {
      font-size: 0.8em;
      color: var(--tg-theme-hint-color);
      margin-left: 5px;
  }
  
  .cart-item__price-per-unit {
    font-size: 0.9em;
    color: var(--tg-theme-hint-color, #888);
  }
  
  .cart-item__quantity-controls {
    display: flex;
    align-items: center;
    margin-top: 0.5rem;
  }
  
  .quantity-btn {
    width: 28px;
    height: 28px;
    padding: 0;
    font-size: 1.2em;
    line-height: 1;
    border-radius: 50%;
    background-color: var(--tg-theme-secondary-bg-color, #eee);
    border: 1px solid var(--tg-theme-hint-color, #ddd);
    color: var(--tg-theme-text-color);
    cursor: pointer;
  }
  .quantity-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
  }
  
  .quantity-input {
    width: 40px;
    height: 28px;
    text-align: center;
    border: 1px solid var(--tg-theme-hint-color, #ddd);
    border-radius: 4px;
    margin: 0 8px;
    font-size: 1em;
    background-color: var(--tg-theme-bg-color);
    color: var(--tg-theme-text-color);
    -moz-appearance: textfield;
  }
  .quantity-input::-webkit-outer-spin-button,
  .quantity-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }
  
  .cart-item__actions {
    display: flex;
    flex-direction: column;
    align-items: flex-end; /* Выровнять по правому краю */
    gap: 0.5rem;
    margin-left: auto; /* Отодвинуть вправо */
    padding-left: 1rem; /* Отступ от середины */
    flex-shrink: 0;
  }
  
  .cart-item__total-price {
    font-weight: bold;
    font-size: 1.1em;
    white-space: nowrap; /* Не переносить цену */
  }
  
  .remove-btn {
    background: none;
    border: none;
    color: var(--tg-theme-hint-color, #aaa);
    font-size: 1.8em;
    line-height: 1;
    padding: 0 5px;
    cursor: pointer;
    transition: color 0.2s;
  }
  
  .remove-btn:hover {
    color: #dc3545; /* Красный при наведении */
  }
  </style>