<template>
  <div class="product-view">
    <!-- Кнопка "Назад" Telegram -->
    <BackButtonHandler @back="goBack" />

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="loading-indicator">
      <p>Загрузка информации о товаре...</p>
      <!-- Спиннер -->
    </div>

    <!-- Сообщение об ошибке -->
    <div v-if="error" class="error-message">
      <p>Не удалось загрузить товар: {{ error }}</p>
      <button @click="loadProduct">Попробовать снова</button>
      <button @click="goBack" style="margin-left: 10px">Назад</button>
    </div>

    <!-- Информация о товаре -->
    <div v-if="product && !isLoading && !error" class="product-details">
      <!-- Галерея изображений (упрощенная - пока только первое изображение) -->
      <div class="product-image-wrapper">
        <img
          v-if="product.images && product.images.length > 0"
          :src="product.images[0].src"
          :alt="product.name"
          class="product-image"
          loading="lazy"
        />
        <img
          v-else
          src="/placeholder.png"
          alt="Изображение отсутствует"
          class="product-image placeholder"
        />
        <span v-if="product.on_sale" class="product-sale-badge">Скидка!</span>
      </div>

      <h1 class="product-name">{{ product.name }}</h1>

      <!-- Цена -->
      <div class="product-price">
        <span v-if="product.on_sale && product.sale_price" class="sale-price">
          {{ formatPrice(product.sale_price) }} ₽
        </span>
        <span
          :class="{
            'regular-price--crossed': product.on_sale && product.sale_price,
          }"
          class="regular-price"
        >
          {{ formatPrice(product.regular_price) }} ₽
        </span>
      </div>

      <!-- Статус наличия -->
      <div class="product-stock-status" :class="stockStatusClass">
        {{ stockStatusText }}
      </div>

      <!-- Краткое описание -->
      <div
        v-if="product.short_description"
        class="product-short-description"
        v-html="product.short_description"
      ></div>

      <!-- Кнопка Добавить в корзину -->
      <div class="add-to-cart-section">
        <!-- Селектор количества (опционально) -->
        <div class="quantity-selector">
          <button @click="decreaseQuantity" :disabled="quantity <= 1">-</button>
          <input
            type="number"
            v-model.number="quantity"
            min="1"
            @input="validateQuantity"
          />
          <button @click="increaseQuantity">+</button>
        </div>
        <button
          @click="handleAddToCart"
          class="add-to-cart-button"
          :disabled="!isAvailable"
        >
          <span v-if="isAvailable">Добавить в корзину</span>
          <span v-else>Нет в наличии</span>
        </button>
      </div>

      <!-- Полное описание (если есть) -->
      <div v-if="product.description" class="product-description">
        <h2>Описание</h2>
        <div v-html="product.description"></div>
      </div>

      <!-- Можно добавить SKU, категории, атрибуты -->
      <div v-if="product.sku" class="product-meta">
        <span>Артикул: {{ product.sku }}</span>
      </div>
      <div
        v-if="product.categories && product.categories.length > 0"
        class="product-meta"
      >
        <span
          >Категории:
          {{ product.categories.map((c) => c.name).join(", ") }}</span
        >
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchProductById } from "@/services"; // API функция
import { useCartStore } from "@/store/cart"; // Стор корзины
//import { showAlert } from '@/utils/telegram';
//import { showBackButton, hideBackButton, showAlert } from '@/utils/telegram'; // Утилиты TG
//import BackButtonHandler from '@/components/BackButtonHandler.vue'; // Компонент для кнопки Назад
import { useToast } from "vue-toastification";

const route = useRoute();
const router = useRouter();
const cartStore = useCartStore();
const toast = useToast();

// Получаем ID товара из параметров маршрута
const productId = computed(() => route.params.id);

// Состояние компонента
const product = ref(null);
const isLoading = ref(false);
const error = ref(null);
const quantity = ref(1); // Количество для добавления в корзину

// Функция загрузки данных о товаре
const loadProduct = async () => {
  if (!productId.value) return;
  isLoading.value = true;
  error.value = null;
  product.value = null; // Сброс перед загрузкой

  try {
    const fetchedProduct = await fetchProductById(productId.value);
    product.value = fetchedProduct;
    // Устанавливаем заголовок страницы
    if (fetchedProduct?.name) {
      document.title = `${fetchedProduct.name} | Магазин`;
    }
  } catch (err) {
    console.error(`Error loading product ${productId.value}:`, err);
    error.value = err.detail || err.message || "Неизвестная ошибка";
    document.title = `Ошибка | Магазин`;
  } finally {
    isLoading.value = false;
  }
};

// Вычисляемые свойства для статуса наличия
const isAvailable = computed(() => {
  // 'instock' - в наличии
  // 'onbackorder' - предзаказ (считаем доступным для добавления)
  // 'outofstock' - нет в наличии
  return (
    product.value?.status === "publish" &&
    (product.value?.stock_status === "instock" ||
      product.value?.stock_status === "onbackorder")
  );
});

const stockStatusText = computed(() => {
  if (!product.value) return "";
  switch (product.value.stock_status) {
    case "instock":
      return "В наличии";
    case "onbackorder":
      return "Доступен для предзаказа";
    case "outofstock":
      return "Нет в наличии";
    default:
      return "";
  }
});

const stockStatusClass = computed(() => {
  if (!product.value) return "";
  return `stock-${product.value.stock_status || "unknown"}`;
});

// Функция форматирования цены
const formatPrice = (price) => {
  const number = parseFloat(price);
  return isNaN(number) ? "?" : number.toLocaleString("ru-RU");
};

// --- Управление количеством ---
const decreaseQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--;
  }
};
const increaseQuantity = () => {
  quantity.value++;
};
// Валидация ввода количества
const validateQuantity = () => {
  if (quantity.value < 1 || !Number.isInteger(quantity.value)) {
    quantity.value = 1;
  }
};

// --- Добавление в корзину ---
const handleAddToCart = () => {
  if (!product.value || !isAvailable.value) return;
  validateQuantity();
  cartStore.addToCart(product.value, quantity.value);

  // Показываем уведомление через vue-toastification
  toast.success(
    `"${product.value.name}" (${quantity.value} шт.) добавлен(о) в корзину!`
  ); // <<< ИСПОЛЬЗОВАНИЕ

  // showAlert(`"${product.value.name}" (${quantity.value} шт.) добавлен(о) в корзину!`); // <<< УБРАТЬ
};

// --- Навигация ---
const goBack = () => {
  // Проверяем, есть ли предыдущая страница в истории роутера
  if (router.options.history.state.back) {
    router.go(-1); // Возвращаемся на предыдущую страницу Vue Router
  } else {
    router.push({ name: "Catalog" }); // Если нет, идем в каталог
  }
};

// --- Жизненный цикл ---
onMounted(() => {
  loadProduct(); // Загружаем товар при монтировании
  // Показываем кнопку Назад Telegram при входе на страницу
  // showBackButton(goBack); // Используем компонент BackButtonHandler
});

// Следим за изменением ID в маршруте (если пользователь переходит с одного товара на другой)
watch(productId, (newId, oldId) => {
  if (newId && newId !== oldId) {
    loadProduct();
    // Прокрутка вверх при смене товара
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

// // Скрываем кнопку Назад Telegram при уходе со страницы
// // Это лучше делать в компоненте BackButtonHandler
// onUnmounted(() => {
//   hideBackButton();
// });
</script>

<style scoped>
.product-view {
  padding: 1rem;
  padding-bottom: 80px; /* Оставляем место для кнопки Добавить в корзину (если она фиксированная) */
  max-width: 700px;
  margin: 0 auto;
}

.loading-indicator,
.error-message {
  text-align: center;
  padding: 2rem;
  color: var(--tg-theme-hint-color, #888);
}
.error-message {
  color: #dc3545;
}
.error-message button {
  margin-top: 1rem;
}

.product-details {
  /* Стили для контейнера с деталями */
}

.product-image-wrapper {
  position: relative;
  width: 100%;
  max-width: 400px; /* Ограничение ширины изображения */
  margin: 0 auto 1.5rem auto;
  border-radius: 12px;
  overflow: hidden;
  background-color: var(--tg-theme-secondary-bg-color, #f1f1f1);
}

.product-image {
  display: block;
  width: 100%;
  height: auto; /* Сохраняем пропорции */
  object-fit: cover;
}
.product-image.placeholder {
  padding: 20%; /* Делаем плейсхолдер меньше */
  opacity: 0.5;
}

.product-sale-badge {
  position: absolute;
  top: 10px;
  left: 10px; /* Слева для детального просмотра */
  background-color: #dc3545;
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.9em;
  font-weight: bold;
}

.product-name {
  font-size: 1.6em;
  font-weight: 600;
  margin-bottom: 0.8rem;
  color: var(--tg-theme-text-color);
}

.product-price {
  font-size: 1.3em;
  margin-bottom: 1rem;
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.sale-price {
  font-weight: bold;
  color: var(--tg-theme-text-color);
}

.regular-price {
  color: var(--tg-theme-hint-color, #888);
}

.regular-price--crossed {
  text-decoration: line-through;
  font-size: 0.9em;
}

.product-stock-status {
  font-size: 0.9em;
  margin-bottom: 1.5rem;
  padding: 5px 10px;
  border-radius: 5px;
  display: inline-block; /* Чтобы фон был только под текстом */
}
.stock-instock {
  color: #198754; /* Зеленый */
  background-color: rgba(25, 135, 84, 0.1);
}
.stock-onbackorder {
  color: #ffc107; /* Желтый */
  background-color: rgba(255, 193, 7, 0.1);
}
.stock-outofstock {
  color: #dc3545; /* Красный */
  background-color: rgba(220, 53, 69, 0.1);
}
.stock-unknown {
  color: var(--tg-theme-hint-color);
  background-color: var(--tg-theme-secondary-bg-color);
}

.product-short-description {
  margin-bottom: 1.5rem;
  color: var(--tg-theme-text-color);
  line-height: 1.5;
  font-size: 1.05em;
}
/* Стили для HTML из описания (осторожно!) */
.product-short-description :deep(p) {
  margin-bottom: 0.5em;
}
.product-short-description :deep(a) {
  color: var(--tg-theme-link-color);
}

.add-to-cart-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  background-color: var(--tg-theme-secondary-bg-color, #f8f9fa);
  padding: 1rem;
  border-radius: 8px;
  /* Можно сделать фиксированным внизу экрана */
  /* position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    background-color: var(--tg-theme-secondary-bg-color);
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 10; */
}

.quantity-selector {
  display: flex;
  align-items: center;
}
.quantity-selector button {
  width: 35px;
  height: 35px;
  padding: 0;
  font-size: 1.2em;
  line-height: 1;
  border-radius: 50%; /* Круглые кнопки */
  background-color: var(--tg-theme-hint-color);
  color: var(--tg-theme-text-color);
}
.quantity-selector input {
  width: 50px;
  height: 35px;
  text-align: center;
  border: 1px solid var(--tg-theme-hint-color);
  border-radius: 6px;
  margin: 0 8px;
  font-size: 1.1em;
  background-color: var(--tg-theme-bg-color);
  color: var(--tg-theme-text-color);
  /* Убираем стрелки у input number */
  -moz-appearance: textfield;
}
.quantity-selector input::-webkit-outer-spin-button,
.quantity-selector input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.add-to-cart-button {
  flex-grow: 1; /* Занимает оставшееся место */
  padding: 12px 20px;
  font-size: 1.1em;
  font-weight: 600;
}
.add-to-cart-button:disabled {
  background-color: var(--tg-theme-hint-color);
  cursor: not-allowed;
}

.product-description {
  margin-top: 2rem;
  border-top: 1px solid var(--tg-theme-hint-color, #eee);
  padding-top: 1.5rem;
}
.product-description h2 {
  margin-bottom: 1rem;
  font-size: 1.3em;
}
/* Стили для HTML из описания */
.product-description :deep(p) {
  margin-bottom: 1em;
  line-height: 1.6;
}
.product-description :deep(ul),
.product-description :deep(ol) {
  margin-left: 1.5em;
  margin-bottom: 1em;
}
.product-description :deep(li) {
  margin-bottom: 0.5em;
}
.product-description :deep(a) {
  color: var(--tg-theme-link-color);
}
.product-description :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 0.5em 0;
}

.product-meta {
  margin-top: 1.5rem;
  font-size: 0.9em;
  color: var(--tg-theme-hint-color);
}
.product-meta span {
  display: block;
  margin-bottom: 0.3em;
}
</style>
