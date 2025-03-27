<template>
    <div class="not-found-view">
      <h1>404 - Страница не найдена</h1>
      <p>К сожалению, страница, которую вы ищете, не существует.</p>
      <router-link to="/">Вернуться в каталог</router-link>
    </div>
  </template>
  
  <script setup>
  // Пока нет скриптов
  </script>
  
  <style scoped>
  .not-found-view {
    padding: 2rem;
    text-align: center;
  }
  h1 {
    color: var(--tg-theme-text-color, #dc3545); /* Можно использовать цвет ошибки */
    margin-bottom: 1rem;
  }
  </style>