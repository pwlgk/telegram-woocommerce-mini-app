<template>
    <div class="catalog-view">
      <h1>Каталог</h1>
  
      <!-- Фильтр по категориям (опционально) -->
      <div class="category-filter" v-if="categories.length > 0">
        <button
          @click="selectCategory(null)"
          :class="{ active: selectedCategoryId === null }"
        >
          Все товары
        </button>
        <button
          v-for="category in categories"
          :key="category.id"
          @click="selectCategory(category.id)"
          :class="{ active: selectedCategoryId === category.id }"
        >
          {{ category.name }}
        </button>
      </div>
  
      <!-- Индикатор загрузки -->
      <div v-if="isLoading" class="loading-indicator">
        <p>Загрузка товаров...</p>
        <!-- Сюда можно добавить красивый спиннер/анимацию -->
      </div>
  
      <!-- Сообщение об ошибке -->
      <div v-if="error" class="error-message">
        <p>Не удалось загрузить товары: {{ error }}</p>
        <button @click="loadData">Попробовать снова</button>
      </div>
  
      <!-- Сетка с товарами -->
      <div v-if="!isLoading && !error && products.length > 0" class="products-grid">
        <ProductCard
          v-for="product in products"
          :key="product.id"
          :product="product"
        />
      </div>
  
      <!-- Сообщение, если товары не найдены -->
      <div v-if="!isLoading && !error && products.length === 0" class="no-products">
        <p>Товары не найдены.</p>
        <p v-if="selectedCategoryId">Попробуйте выбрать другую категорию.</p>
      </div>
  
       <!-- Пагинация (простая) -->
      <div v-if="!isLoading && !error && products.length > 0" class="pagination">
         <button @click="prevPage" :disabled="currentPage <= 1">Назад</button>
         <span>Страница {{ currentPage }}</span>
         <button @click="nextPage" :disabled="isLastPage">Вперед</button>
         <!-- `isLastPage` нужно будет определить на основе ответа API (заголовки или общее кол-во) -->
      </div>
  
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, watch } from 'vue';
  import { fetchProducts, fetchCategories } from '@/services'; // Импорт функций API
  import ProductCard from '@/components/ProductCard.vue'; // Импорт карточки товара
  
  // Состояние компонента
  const products = ref([]);
  const categories = ref([]);
  const isLoading = ref(false);
  const error = ref(null);
  const selectedCategoryId = ref(null); // ID выбранной категории (null - все)
  const currentPage = ref(1);
  const productsPerPage = ref(10); // Сколько товаров загружать за раз
  const isLastPage = ref(false); // Флаг, что это последняя страница (упрощенно)
  
  // Функция для загрузки данных (товары и категории)
  const loadData = async () => {
    isLoading.value = true;
    error.value = null;
    isLastPage.value = false; // Сбрасываем флаг последней страницы
  
    try {
      // Загружаем категории только один раз при монтировании (или если нужно обновить)
      if (categories.value.length === 0) {
         const fetchedCategories = await fetchCategories({ per_page: 100, hide_empty: true }); // Загружаем до 100 категорий
         categories.value = fetchedCategories || [];
      }
  
      // Загружаем товары
      const params = {
        page: currentPage.value,
        per_page: productsPerPage.value,
        status: 'publish', // Только опубликованные
      };
      if (selectedCategoryId.value !== null) {
        params.category = selectedCategoryId.value; // Добавляем фильтр по категории
      }
  
      const fetchedProducts = await fetchProducts(params);
  
      // Простая проверка на последнюю страницу (если вернулось меньше, чем запрашивали)
      if (!fetchedProducts || fetchedProducts.length < productsPerPage.value) {
          isLastPage.value = true;
      }
  
      products.value = fetchedProducts || []; // Заменяем товары текущей страницы
  
    } catch (err) {
      console.error("Error loading catalog data:", err);
      error.value = err.detail || err.message || 'Неизвестная ошибка';
      products.value = []; // Очищаем товары при ошибке
      categories.value = []; // Можно очистить и категории
    } finally {
      isLoading.value = false;
    }
  };
  
  // Функция выбора категории
  const selectCategory = (categoryId) => {
    if (selectedCategoryId.value === categoryId) return; // Не перезагружать, если категория та же
    selectedCategoryId.value = categoryId;
    currentPage.value = 1; // Сбрасываем на первую страницу при смене категории
    // loadData(); // Загрузка будет вызвана через watch
  };
  
  // Функции пагинации
  const nextPage = () => {
    if (isLastPage.value) return;
    currentPage.value++;
    // loadData(); // Загрузка будет вызвана через watch
  };
  
  const prevPage = () => {
    if (currentPage.value <= 1) return;
    currentPage.value--;
    // loadData(); // Загрузка будет вызвана через watch
  };
  
  console.log('Current API Base URL from env:', import.meta.env.VITE_API_BASE_URL);
  // Загружаем данные при монтировании компонента
  onMounted(() => {
    loadData();
  });
  
  // Перезагружаем данные при изменении страницы или выбранной категории
  watch([currentPage, selectedCategoryId], () => {
      loadData();
      // Прокрутка вверх при смене страницы/категории
      window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  
  </script>
  
  <style scoped>
  .catalog-view {
    padding: 1rem;
    max-width: 1000px; /* Ограничение ширины для больших экранов */
    margin: 0 auto;
  }
  
  h1 {
    margin-bottom: 1.5rem;
    color: var(--tg-theme-text-color);
  }
  
  .category-filter {
    margin-bottom: 1.5rem;
    display: flex;
    flex-wrap: wrap; /* Перенос кнопок на новую строку */
    gap: 10px; /* Отступы между кнопками */
  }
  
  .category-filter button {
    background-color: var(--tg-theme-secondary-bg-color, #f0f0f0);
    color: var(--tg-theme-text-color, #333);
    border: 1px solid var(--tg-theme-hint-color, #ddd);
    padding: 8px 12px;
    border-radius: 16px; /* Скругленные кнопки */
    cursor: pointer;
    transition: background-color 0.2s, color 0.2s;
    font-size: 0.9em;
  }
  
  .category-filter button:hover {
    background-color: var(--tg-theme-hint-color, #ddd);
  }
  
  .category-filter button.active {
    background-color: var(--tg-theme-button-color, #5288c1);
    color: var(--tg-theme-button-text-color, #fff);
    border-color: var(--tg-theme-button-color, #5288c1);
  }
  
  .loading-indicator,
  .error-message,
  .no-products {
    text-align: center;
    padding: 2rem;
    color: var(--tg-theme-hint-color, #888);
  }
  .error-message {
      color: #dc3545; /* Красный для ошибок */
  }
  .error-message button {
      margin-top: 1rem;
  }
  
  .products-grid {
    display: grid;
    /* Адаптивная сетка: минимум 150px, максимум 1fr */
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 1rem; /* Отступы между карточками */
    margin-bottom: 2rem;
  }
  
  /* Стили для мобильных устройств (если нужно переопределить сетку) */
  @media (max-width: 400px) {
    .products-grid {
      grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
      gap: 0.8rem;
    }
  }
  
  .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1rem;
      margin-top: 2rem;
  }
  
  .pagination button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
  }
  </style>