// frontend/src/router/index.js
import { createRouter, createWebHashHistory, createWebHistory } from 'vue-router';

// Импортируем компоненты View (пока можно создать пустые заглушки)
import CatalogView from '../views/CatalogView.vue';
import ProductView from '../views/ProductView.vue';
import CartView from '../views/CartView.vue';
import CheckoutSuccessView from '../views/CheckoutSuccessView.vue';
import NotFoundView from '../views/NotFoundView.vue'; // Компонент для 404

const routes = [
  {
    path: '/',
    name: 'Catalog',
    component: CatalogView,
    meta: { title: 'Каталог' } // Для заголовка страницы или хлебных крошек
  },
  {
    // Динамический сегмент :id
    path: '/product/:id',
    name: 'Product',
    component: ProductView,
    props: true, // Передавать :id как prop в компонент ProductView
    meta: { title: 'Товар' } // Заголовок будет обновлен в компоненте
  },
  {
    path: '/cart',
    name: 'Cart',
    component: CartView,
    meta: { title: 'Корзина' }
  },
  {
    path: '/checkout-success',
    name: 'CheckoutSuccess',
    component: CheckoutSuccessView,
    meta: { title: 'Заказ оформлен' }
  },
  // Обработка ненайденных маршрутов (404)
  {
    path: '/:pathMatch(.*)*', // Регулярное выражение для всех остальных путей
    name: 'NotFound',
    component: NotFoundView,
    meta: { title: 'Страница не найдена' }
  }
];

const router = createRouter({
  // Используем Hash History для Mini Apps, т.к. это проще для статических хостингов
  // и не требует настройки сервера.
  history: createWebHashHistory(import.meta.env.BASE_URL), // BASE_URL обычно '/'
  // history: createWebHistory(import.meta.env.BASE_URL), // Если сервер настроен на SPA
  routes, // short for `routes: routes`
  // Прокрутка к верху страницы при переходе
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  },
});

// (Опционально) Глобальный хук для обновления заголовка страницы
// router.beforeEach((to, from, next) => {
//   document.title = `${to.meta.title || 'Магазин'} | My Shop`;
//   next();
// });

export default router;