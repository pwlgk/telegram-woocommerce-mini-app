<template>
  <div id="app-container">
    <!-- >>>>> ДОБАВЛЯЕМ ШАПКУ <<<<< -->
    <TheHeader />

    <!-- Отображение компонента для текущего маршрута -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Можно добавить футер, если нужно -->
    <!-- <TheFooter /> -->
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
// >>>>> ИМПОРТИРУЕМ ШАПКУ <<<<<
import TheHeader from './components/TheHeader.vue';
import { getThemeParams, getColorScheme } from './utils/telegram';

onMounted(() => {
  console.log('Telegram Theme Params:', getThemeParams());
  console.log('Telegram Color Scheme:', getColorScheme());
});
</script>

<style>
/* Глобальные стили или импорт */
@import './assets/base.css';

/* Обертка для основного контента, чтобы шапка не перекрывала */
.main-content {
  /* Можно добавить padding-top, если шапка фиксированная */
}

/* ... остальные стили (переходы и т.д.) ... */
#app-container {
  background-color: var(--tg-theme-bg-color, #ffffff);
  color: var(--tg-theme-text-color, #000000);
  min-height: 100vh;
  transition: background-color 0.3s ease, color 0.3s ease;
  display: flex; /* Чтобы управлять .main-content */
  flex-direction: column;
}
.main-content {
   flex-grow: 1; /* Занимает все доступное пространство */
}


.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

a {
  color: var(--tg-theme-link-color, #2481cc);
}

button {
  background-color: var(--tg-theme-button-color, #5288c1);
  color: var(--tg-theme-button-text-color, #ffffff);
  border: none;
  padding: 10px 15px;
  border-radius: 8px;
  cursor: pointer;
  transition: opacity 0.2s;
}

button:hover {
  opacity: 0.9;
}
button:disabled {
    opacity: 0.6 !important; /* !important, чтобы перебить hover */
    cursor: not-allowed;
}
</style>