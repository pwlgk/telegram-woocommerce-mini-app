// frontend/src/store/cart.js
import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

// Ключ для localStorage
const CART_STORAGE_KEY = 'my_woocommerce_cart';

// Функция для загрузки корзины из localStorage
const loadCartFromStorage = () => {
  const storedCart = localStorage.getItem(CART_STORAGE_KEY);
  if (storedCart) {
    try {
      return JSON.parse(storedCart);
    } catch (e) {
      console.error("Failed to parse cart from localStorage", e);
      localStorage.removeItem(CART_STORAGE_KEY); // Очистить некорректные данные
      return [];
    }
  }
  return [];
};

export const useCartStore = defineStore('cart', () => {
  // --- State ---
  // Загружаем начальное состояние из localStorage
  const items = ref(loadCartFromStorage()); // Array of { product_id, name, price, quantity, image, variation_id? }

  // --- Getters ---
  const totalItems = computed(() => {
    return items.value.reduce((sum, item) => sum + item.quantity, 0);
  });

  const totalPrice = computed(() => {
    return items.value.reduce((sum, item) => {
         // Убедимся, что цена - число
         const price = parseFloat(item.price) || 0;
         return sum + price * item.quantity;
    }, 0).toFixed(2); // Округляем до 2 знаков после запятой
  });

  const isEmpty = computed(() => items.value.length === 0);

  // --- Actions ---
  const findItemIndex = (productId, variationId = null) => {
    return items.value.findIndex(item =>
      item.product_id === productId && item.variation_id === variationId
    );
  };

  const addToCart = (product, quantity = 1) => {
    if (!product || !product.id || quantity <= 0) return;

    const productData = {
      product_id: product.id,
      name: product.name || 'Unknown Product',
      price: product.sale_price || product.price || '0', // Приоритет sale_price
      image: product.images?.[0]?.src || null, // Берем первое изображение
      variation_id: product.variation_id || null, // Если это вариация
    };

    const itemIndex = findItemIndex(productData.product_id, productData.variation_id);

    if (itemIndex > -1) {
      // Товар уже в корзине, увеличиваем количество
      items.value[itemIndex].quantity += quantity;
    } else {
      // Добавляем новый товар
      items.value.push({ ...productData, quantity });
    }
    console.log('Cart updated:', items.value);
  };

  const updateQuantity = (productId, quantity, variationId = null) => {
    if (quantity <= 0) {
      // Если количество 0 или меньше, удаляем товар
      removeFromCart(productId, variationId);
      return;
    }

    const itemIndex = findItemIndex(productId, variationId);
    if (itemIndex > -1) {
      items.value[itemIndex].quantity = quantity;
    }
  };

  const removeFromCart = (productId, variationId = null) => {
    const itemIndex = findItemIndex(productId, variationId);
    if (itemIndex > -1) {
      items.value.splice(itemIndex, 1);
    }
  };

  const clearCart = () => {
    items.value = [];
  };

  // --- Persistence ---
  // Сохраняем корзину в localStorage при любом изменении
  watch(items, (newCartItems) => {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(newCartItems));
  }, { deep: true }); // deep: true нужно для отслеживания изменений внутри объектов массива


  return {
    items,
    totalItems,
    totalPrice,
    isEmpty,
    addToCart,
    updateQuantity,
    removeFromCart,
    clearCart,
  };
});