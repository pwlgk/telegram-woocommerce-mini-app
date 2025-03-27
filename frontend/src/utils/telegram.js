// frontend/src/utils/telegram.js

/**
 * Проверяет, доступен ли объект Telegram WebApp.
 * @returns {boolean}
 */
const isTelegramWebAppAvailable = () => {
    return typeof window !== 'undefined' && typeof window.Telegram?.WebApp !== 'undefined';
  };
  
  /**
   * Безопасно получает объект Telegram WebApp.
   * @returns {object|null} WebApp object or null.
   */
  const getWebApp = () => {
    return isTelegramWebAppAvailable() ? window.Telegram.WebApp : null;
  };
  
  /**
   * Вызывает WebApp.ready(), если доступно.
   */
  export const ready = () => {
    getWebApp()?.ready();
    console.log('Telegram WebApp ready() called.');
  };
  
  /**
   * Безопасно получает initData.
   * @returns {string} initData string or empty string.
   */
  export const getInitData = () => {
    return getWebApp()?.initData || '';
  };
  
  /**
   * Безопасно получает initDataUnsafe.
   * @returns {object} initDataUnsafe object or empty object.
   */
  export const getInitDataUnsafe = () => {
    return getWebApp()?.initDataUnsafe || {};
  };
  
  /**
   * Безопасно получает данные пользователя из initDataUnsafe.
   * @returns {object|null} User object or null.
   */
  export const getUserData = () => {
    return getInitDataUnsafe()?.user || null;
  };
  
  /**
   * Закрывает Mini App.
   */
  export const closeApp = () => {
    console.log('Closing Telegram Mini App...');
    getWebApp()?.close();
  };
  
  /**
   * Разворачивает Mini App на весь экран.
   */
  export const expandApp = () => {
    getWebApp()?.expand();
  };
  
  /**
 * Показывает всплывающее уведомление (заменено на console.log из-за проблем совместимости).
 * @param {string} message Текст уведомления.
 * @param {function} [callback] Функция обратного вызова (будет вызвана сразу).
 */
  export const showAlert = (message, callback) => {
    console.log(`[Simulated Alert] ${message}`); // Выводим в консоль
    // Вызываем колбэк немедленно, если он есть
    if (typeof callback === 'function') {
      try {
         callback();
      } catch (e) {
         console.error("Error in showAlert callback:", e);
      }
    }
    // Оригинальный вызов:
    // getWebApp()?.showAlert(message, callback);
  };
  
/**
 * Показывает диалоговое окно с подтверждением (заменено на console.log и авто-подтверждение).
 * @param {string} message Текст сообщения.
 * @param {function} [callback] Функция обратного вызова, получает boolean (всегда true).
 * @param {string[]} [buttons] Массив текстов кнопок.
 */
export const showConfirm = (message, callback, buttons) => {
    console.log(`[Simulated Confirm] ${message} (Auto-confirmed)`);
    if (typeof callback === 'function') {
       try {
          callback(true); // Всегда вызываем с true для простоты
       } catch (e) {
          console.error("Error in showConfirm callback:", e);
       }
    }
    // Оригинальный вызов:
    // getWebApp()?.showConfirm(message, callback, buttons);
 };
  
  // --- Управление MainButton ---
  const MainButton = getWebApp()?.MainButton;
  
  /**
   * Показывает главную кнопку.
   * @param {string} text Текст кнопки.
   * @param {function} onClick Колбэк при нажатии.
   * @param {boolean} [disable=false] Сделать ли кнопку неактивной.
   * @param {boolean} [progress=false] Показать ли индикатор загрузки.
   */
  export const showMainButton = (text, onClick, disable = false, progress = false) => {
    if (!MainButton) return;
    MainButton.setText(text);
    // Удаляем предыдущий обработчик, чтобы не было дублирования
    MainButton.offClick(MainButton._currentOnClick); // Используем внутреннее свойство для удаления
    MainButton.onClick(onClick);
    MainButton._currentOnClick = onClick; // Сохраняем текущий обработчик
    if (disable) {
      MainButton.disable();
    } else {
      MainButton.enable();
    }
    if (progress) {
      MainButton.showProgress();
    } else {
      MainButton.hideProgress();
    }
    MainButton.show();
  };
  
  /**
   * Скрывает главную кнопку.
   */
  export const hideMainButton = () => {
    if (!MainButton) return;
     // Удаляем обработчик при скрытии
    if (MainButton._currentOnClick) {
       MainButton.offClick(MainButton._currentOnClick);
       MainButton._currentOnClick = null;
    }
    MainButton.hide();
  };
  
  // --- Управление BackButton ---
  const BackButton = getWebApp()?.BackButton;
  
  /**
   * Показывает кнопку "Назад".
   * @param {function} onClick Колбэк при нажатии.
   */
  export const showBackButton = (onClick) => {
    if (!BackButton) return;
    // Удаляем предыдущий обработчик
    BackButton.offClick(BackButton._currentOnClick);
    BackButton.onClick(onClick);
    BackButton._currentOnClick = onClick; // Сохраняем
    BackButton.show();
  };
  
  /**
   * Скрывает кнопку "Назад".
   */
  export const hideBackButton = () => {
     if (!BackButton) return;
     // Удаляем обработчик при скрытии
    if (BackButton._currentOnClick) {
       BackButton.offClick(BackButton._currentOnClick);
       BackButton._currentOnClick = null;
    }
    BackButton.hide();
  };
  
  // --- Другие полезные функции ---
  
  /**
   * Получает цветовую схему Telegram (light или dark).
   * @returns {string} 'light' or 'dark'.
   */
  export const getColorScheme = () => {
    return getWebApp()?.colorScheme || 'light';
  };
  
  /**
   * Получает объект темы Telegram.
   * @returns {object} ThemeParams object.
   */
  export const getThemeParams = () => {
      return getWebApp()?.themeParams || {};
  };
  
  /**
   * Применяет стили темы Telegram к CSS переменным на :root.
   */
  export const applyThemeStyles = () => {
      const themeParams = getThemeParams();
      const root = document.documentElement;
      if (root && themeParams) {
          for (const [key, value] of Object.entries(themeParams)) {
              // Преобразуем camelCase в kebab-case для CSS переменных
              const cssVarName = `--tg-theme-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
              root.style.setProperty(cssVarName, value);
              // console.log(`Set CSS var: ${cssVarName} = ${value}`);
          }
          // Добавляем цветовую схему как класс к body или html
          document.body.classList.remove('theme-light', 'theme-dark');
          document.body.classList.add(`theme-${getColorScheme()}`);
      }
  };