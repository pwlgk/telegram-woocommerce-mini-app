// frontend/src/services/api.js
import axios from 'axios';

// Получаем базовый URL из переменных окружения Vite
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

console.log('API Base URL:', API_BASE_URL); // Для отладки

if (!API_BASE_URL) {
  console.error("VITE_API_BASE_URL is not defined. Please check your .env files.");
  // Можно выбросить ошибку или установить URL по умолчанию для предотвращения падения
  // throw new Error("API Base URL is not configured.");
}

// Создаем экземпляр Axios
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    // Можно добавить другие общие заголовки, если нужно
  },
  timeout: 15000, // Таймаут запроса 15 секунд
});

// (Опционально) Перехватчик запросов для добавления заголовков (например, initData)
apiClient.interceptors.request.use(
  (config) => {
    // Пытаемся получить initData перед каждым запросом (кроме GET, возможно)
    // Это не лучший подход для КАЖДОГО запроса, лучше добавлять только там, где нужно (в createOrder)
    // Но можно оставить для примера
    // if (window.Telegram?.WebApp?.initData && config.method !== 'get') {
    //   config.headers['X-Telegram-Init-Data'] = window.Telegram.WebApp.initData;
    // }
    return config;
  },
  (error) => {
    console.error('Axios request error:', error);
    return Promise.reject(error);
  }
);


// (Опционально) Перехватчик ответов для обработки ошибок
apiClient.interceptors.response.use(
  (response) => {
    // Все статусы 2xx попадают сюда
    return response.data; // Возвращаем только данные из ответа
  },
  (error) => {
    // Статусы вне диапазона 2xx попадают сюда
    console.error('Axios response error:', error.response || error.message);

    // Можно централизованно обработать ошибки (например, показать уведомление)
    let errorMessage = 'Произошла ошибка сети или сервера.';
    if (error.response) {
      // Запрос был сделан, и сервер ответил кодом состояния вне 2xx
      console.error('Error data:', error.response.data);
      console.error('Error status:', error.response.status);
      // Попытка извлечь сообщение об ошибке из ответа бэкенда
      errorMessage = error.response.data?.detail || error.response.data?.message || errorMessage;
      if (error.response.status === 401) {
        errorMessage = 'Ошибка авторизации. Попробуйте перезапустить приложение.';
        // Здесь можно добавить логику выхода или обновления токена, если бы он был
      } else if (error.response.status === 404) {
        errorMessage = 'Запрошенный ресурс не найден.';
      }
      // и т.д.
    } else if (error.request) {
      // Запрос был сделан, но ответ не получен (например, нет сети)
      console.error('Error request:', error.request);
      errorMessage = 'Не удалось подключиться к серверу. Проверьте интернет-соединение.';
    } else {
      // Произошло что-то при настройке запроса, вызвавшее ошибку
      console.error('Error message:', error.message);
    }

    // Показываем ошибку пользователю (можно использовать alert или компонент уведомлений)
    // alert(errorMessage); // Не лучший вариант в Mini App

    // Отклоняем промис с ошибкой, чтобы её можно было поймать в вызывающем коде
    // Можно передать только сообщение или весь объект ошибки/ответа
    return Promise.reject(error.response?.data || { detail: errorMessage });
  }
);

export default apiClient;