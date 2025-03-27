<template>
  <div class="cart-view">
    <!-- Кнопка Назад -->
    <BackButtonHandler @back="goBack" />

    <h1>Корзина</h1>

    <div v-if="cartStore.isEmpty" class="empty-cart">
      <p>Ваша корзина пуста.</p>
      <router-link to="/" class="go-to-catalog-btn"
        >Перейти в каталог</router-link
      >
    </div>

    <div v-else class="cart-content">
      <!-- Список товаров -->
      <div class="cart-items-list">
        <CartItem
          v-for="item in cartStore.items"
          :key="`${item.product_id}-${item.variation_id || 'no-var'}`"
          :item="item"
        />
      </div>

      <!-- Итоговая информация -->
      <div class="cart-summary">
        <div class="summary-row">
          <span>Товаров:</span>
          <span>{{ cartStore.totalItems }} шт.</span>
        </div>
        <div class="summary-row total">
          <span>Итого:</span>
          <span>{{ cartStore.totalPrice }} ₽</span>
        </div>

        <!-- Кнопка Оформить Заказ (через MainButton Telegram) -->
        <!-- Сама кнопка будет управляться через showMainButton -->

        <!-- Или обычная кнопка, если не хотим использовать MainButton -->
        <button @click="proceedToCheckout" class="checkout-button" :disabled="isProcessing">
              <span v-if="isProcessing">Оформление...</span>
              <span v-else>Оформить заказ</span>
           </button> 
        <div v-if="checkoutError" class="checkout-error">
          Ошибка оформления: {{ checkoutError }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import { useCartStore } from "@/store/cart";
import CartItem from "@/components/CartItem.vue";
import BackButtonHandler from "@/components/BackButtonHandler.vue";
import {
  showMainButton,
  hideMainButton,
  showConfirm,
  getInitData,
} from "@/utils/telegram";
import { createOrder } from "@/services"; // API функция
import { useToast } from "vue-toastification";

const router = useRouter();
const cartStore = useCartStore();
const toast = useToast();

const isProcessing = ref(false); // Флаг процесса оформления
const checkoutError = ref(null); // Ошибка оформления

// --- Оформление заказа ---
const proceedToCheckout = async () => {
  if (cartStore.isEmpty || isProcessing.value) return;

  isProcessing.value = true;
  checkoutError.value = null;
  // Показываем прогресс на MainButton
  showMainButton("Оформление...", () => {}, true, true);

  try {
    const initData = getInitData();
    if (!initData) {
      throw new Error(
        "Не удалось получить данные пользователя Telegram (initData)."
      );
    }

    // Формируем payload для API
    const payload = {
      line_items: cartStore.items.map((item) => ({
        product_id: item.product_id,
        quantity: item.quantity,
        variation_id: item.variation_id, // Будет null, если нет
      })),
      // customer_note: 'Какой-то комментарий' // Если нужно поле для комментария
    };

    // Отправляем запрос на создание заказа
    const createdOrder = await createOrder(payload, initData);

    console.log("Order created:", createdOrder);

    toast.success(`Заказ №${createdOrder.id || "?"} успешно создан!`);
    cartStore.clearCart();
    router.push({ name: "CheckoutSuccess" });

    // showAlert(
    //     `Ваш заказ №${createdOrder.id || '?'} успешно создан! Менеджер скоро свяжется с вами.`,
    //     () => {
    //         cartStore.clearCart();
    //         router.push({ name: 'CheckoutSuccess' });
    //     }
    // ); // <<< УБРАТЬ
  } catch (err) {
    console.error("Checkout error:", err);
    checkoutError.value =
      err.detail || err.message || "Не удалось оформить заказ.";
    // Показываем ошибку пользователю через toast
    toast.error(`Ошибка оформления заказа: ${checkoutError.value}`);
    // showAlert(`Ошибка оформления заказа: ${checkoutError.value}`); // <<< УБРАТЬ
  } finally {
    isProcessing.value = false;
    // Возвращаем кнопку в нормальное состояние (если она не скрыта после успеха)
    // (В данном случае она будет скрыта при переходе на другую страницу)
    // showMainButton('Оформить заказ', proceedToCheckout, cartStore.isEmpty);
  }
};

// --- Управление MainButton ---
const updateMainButton = () => {
  if (!cartStore.isEmpty) {
    showMainButton(
      `Оформить заказ (${cartStore.totalPrice} ₽)`,
      proceedToCheckout, // Колбэк при нажатии
      isProcessing.value, // Отключить во время обработки
      isProcessing.value // Показать прогресс во время обработки
    );
  } else {
    hideMainButton(); // Скрываем кнопку, если корзина пуста
  }
};

// --- Навигация ---
const goBack = () => {
  router.push({ name: "Catalog" }); // Всегда возвращаемся в каталог из корзины
};

// --- Жизненный цикл ---
onMounted(() => {
  updateMainButton(); // Показываем/обновляем MainButton при входе
  // Следим за изменениями в корзине, чтобы обновлять кнопку
  watch(() => cartStore.items, updateMainButton, { deep: true });
  // Также следим за общей суммой, т.к. она может измениться без изменения items (редко)
  watch(() => cartStore.totalPrice, updateMainButton);
});

onUnmounted(() => {
  hideMainButton(); // Скрываем MainButton при уходе со страницы
});
</script>

<style scoped>
.cart-view {
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
  padding-bottom: 100px; /* Отступ снизу для summary или фиксированной кнопки */
}

h1 {
  margin-bottom: 1.5rem;
}

.empty-cart {
  text-align: center;
  padding: 3rem 1rem;
  color: var(--tg-theme-hint-color);
}

.go-to-catalog-btn {
  display: inline-block;
  margin-top: 1.5rem;
  padding: 10px 20px;
  background-color: var(--tg-theme-button-color);
  color: var(--tg-theme-button-text-color);
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
}

.cart-items-list {
  margin-bottom: 2rem;
}

.cart-summary {
  border-top: 2px solid var(--tg-theme-secondary-bg-color, #eee);
  padding-top: 1.5rem;
  background-color: var(
    --tg-theme-bg-color
  ); /* Фон для возможного фикс. позиционирования */
  /* Стили для фиксации внизу экрана (если нужно) */
  /* position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    background-color: var(--tg-theme-bg-color);
    box-shadow: 0 -2px 10px rgba(0,0,0,0.08);
    z-index: 10; */
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  font-size: 1.1em;
  color: var(--tg-theme-text-color);
}
.summary-row span:first-child {
  color: var(--tg-theme-hint-color);
}

.summary-row.total {
  font-weight: bold;
  font-size: 1.3em;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--tg-theme-hint-color, #ddd);
}
.summary-row.total span:first-child {
  color: var(--tg-theme-text-color); /* Итого - основной цвет */
}

.checkout-button {
  width: 100%;
  padding: 15px;
  font-size: 1.2em;
  font-weight: 600;
  margin-top: 1.5rem;
}
.checkout-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.checkout-error {
  margin-top: 1rem;
  color: #dc3545;
  text-align: center;
  font-size: 0.9em;
}
</style>
