// frontend/src/main.js
import { createApp } from 'vue'

import App from './App.vue'
import router from './router'
import pinia from './store'
import { ready as telegramReady, applyThemeStyles } from './utils/telegram'

// >>>>> ИМПОРТЫ ДЛЯ VUE-TOASTIFICATION <<<<<
import Toast, { POSITION } from "vue-toastification";
// Импортируем CSS стили (можно выбрать другие темы)
import "vue-toastification/dist/index.css";
// >>>>> КОНЕЦ ИМПОРТОВ <<<<<

// import './assets/main.css'

const app = createApp(App)

// >>>>> НАСТРОЙКА VUE-TOASTIFICATION <<<<<
const toastOptions = {
    // Указываем позицию уведомлений
    position: POSITION.BOTTOM_CENTER,
    // Время отображения в миллисекундах
    timeout: 3000,
    // Скрывать при клике
    closeOnClick: true,
    // Показывать/скрывать полосу прогресса
    pauseOnFocusLoss: true,
    pauseOnHover: true,
    draggable: true,
    draggablePercent: 0.6,
    // Показать кнопку закрытия
    showCloseButtonOnHover: false,
    // Иконки (можно отключить: false)
    hideProgressBar: false,
    closeButton: "button", // 'button' или false
    icon: true,
    rtl: false,
    // Настройки переходов
    transition: "Vue-Toastification__fade",
    maxToasts: 5,
    newestOnTop: true
};
app.use(Toast, toastOptions);
// >>>>> КОНЕЦ НАСТРОЙКИ <<<<<

app.use(pinia)
app.use(router)

app.mount('#app')

telegramReady();
applyThemeStyles();
window.Telegram?.WebApp?.onEvent('themeChanged', applyThemeStyles);