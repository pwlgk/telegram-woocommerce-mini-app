<template>
    <!-- Этот компонент ничего не рендерит в DOM -->
    <div v-if="false"></div>
  </template>
  
  <script setup>
  import { onMounted, onUnmounted } from 'vue';
  import { showBackButton, hideBackButton } from '@/utils/telegram';
  
  // Определяем событие 'back', которое будет вызвано при нажатии кнопки
  const emit = defineEmits(['back']);
  
  // Функция, которая будет вызываться при нажатии кнопки Назад в Telegram
  const onBackClick = () => {
    emit('back'); // Генерируем событие 'back'
  };
  
  onMounted(() => {
    // Показываем кнопку Назад при монтировании компонента
    showBackButton(onBackClick);
  });
  
  onUnmounted(() => {
    // Скрываем кнопку Назад при демонтировании компонента
    hideBackButton();
  });
  </script>