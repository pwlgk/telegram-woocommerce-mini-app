// frontend/src/services/index.js
import apiClient from './api';

/**
 * Получает список товаров.
 * @param {object} params Параметры запроса (page, per_page, category, search, etc.)
 * @returns {Promise<Array>} Массив товаров
 */
export const fetchProducts = (params = {}) => {
  return apiClient.get('/products', { params });
};

/**
 * Получает детальную информацию о товаре по ID.
 * @param {number|string} productId ID товара
 * @returns {Promise<object>} Объект товара
 */
export const fetchProductById = (productId) => {
  if (!productId) return Promise.reject(new Error("Product ID is required"));
  return apiClient.get(`/products/${productId}`);
};

/**
 * Получает список категорий.
 * @param {object} params Параметры запроса (parent, hide_empty, etc.)
 * @returns {Promise<Array>} Массив категорий
 */
export const fetchCategories = (params = {}) => {
  return apiClient.get('/categories', { params });
};

/**
 * Создает новый заказ.
 * @param {object} payload Данные заказа { line_items: [...], customer_note?: '...' }
 * @param {string} initData Строка Telegram initData
 * @returns {Promise<object>} Объект созданного заказа
 */
export const createOrder = (payload, initData) => {
  if (!payload || !payload.line_items || payload.line_items.length === 0) {
      return Promise.reject(new Error("Order payload with line_items is required"));
  }
  if (!initData) {
      return Promise.reject(new Error("Telegram initData is required for creating order"));
  }

  // Добавляем заголовок X-Telegram-Init-Data именно здесь
  const config = {
    headers: {
      'X-Telegram-Init-Data': initData,
    },
  };

  return apiClient.post('/orders', payload, config);
};