<template>
    <header class="app-header">
      <div class="header-content">
        <!-- Можно добавить логотип или название -->
        <router-link to="/" class="header-logo">Магазин</router-link>
  
        <!-- Кнопка/Иконка корзины -->
        <router-link :to="{ name: 'Cart' }" class="cart-button">
          🛒
          <span v-if="cartStore.totalItems > 0" class="cart-badge">
            {{ cartStore.totalItems }}
          </span>
        </router-link>
      </div>
    </header>
  </template>
  
  <script setup>
  import { useCartStore } from '@/store/cart';
  
  const cartStore = useCartStore();
  </script>
  
  <style scoped>
  .app-header {
    /* Стили для шапки */
    background-color: var(--tg-theme-secondary-bg-color, #f8f9fa);
    padding: 0.8rem 1rem;
    /* Можно сделать липкой */
    /* position: sticky;
    top: 0;
    z-index: 100; */
    border-bottom: 1px solid var(--tg-theme-hint-color, #e0e0e0);
  }
  
  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: 1000px; /* Соответствует CatalogView */
    margin: 0 auto;
  }
  
  .header-logo {
    font-size: 1.2em;
    font-weight: bold;
    color: var(--tg-theme-text-color);
    text-decoration: none;
  }
  
  .cart-button {
    position: relative;
    font-size: 1.5em; /* Размер иконки корзины */
    color: var(--tg-theme-text-color);
    text-decoration: none;
    padding: 5px;
  }
  
  .cart-badge {
    position: absolute;
    top: -5px;
    right: -8px;
    background-color: var(--tg-theme-button-color, #dc3545); /* Используем цвет кнопки или красный */
    color: var(--tg-theme-button-text-color, white);
    border-radius: 50%;
    width: 20px;
    height: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 0.6em; /* Маленький шрифт для цифр */
    font-weight: bold;
    border: 1px solid var(--tg-theme-secondary-bg-color); /* Обводка фоном шапки */
  }
  </style>