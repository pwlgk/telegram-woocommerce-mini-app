<template>
    <div class="checkout-success-view">
      <h1>Заказ успешно оформлен!</h1>
      <p>Спасибо за ваш заказ. Наш менеджер скоро свяжется с вами в Telegram для уточнения деталей.</p>
      <button @click="goHome">Вернуться в каталог</button>
      <!-- Можно добавить кнопку закрытия Mini App -->
      <!-- <button @click="closeApp">Закрыть</button> -->
    </div>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router';
  // import { closeApp } from '@/utils/telegram'; // Если нужна кнопка закрытия
  
  const router = useRouter();
  
  const goHome = () => {
    router.push('/');
  };
  </script>
  
  <style scoped>
  .checkout-success-view {
    padding: 2rem;
    text-align: center;
  }
  h1 {
    color: var(--tg-theme-button-color, #28a745); /* Можно использовать цвет успеха */
    margin-bottom: 1rem;
  }
  button {
    margin-top: 1.5rem;
  }
  </style>