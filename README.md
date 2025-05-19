# 🤖 Telegram-бот для Qwen AI через прокси

Привет!

Этот проект представляет собой Telegram-бота, позволяющий взаимодействовать с моделью искусственного интеллекта **Qwen** от Alibaba Cloud через локальный API-прокси.  

Автор прокси: [@y13sint](https://github.com/y13sint ) — [FreeQwenApi](https://github.com/y13sint/FreeQwenApi )

---

## 📦 Возможности:

- ✅ Отправка запросов к модели Qwen через локальный API-прокси  
- ✅ Получение ответов в Telegram в удобном формате  
- ✅ Поддержка диалога (сохранение контекста общения)  
- ✅ Простой и понятный интерфейс для пользователей  
- ✅ Возможность выбора модели Qwen (qwen-max-latest, qwen-plus-latest и др.)

---

## 🔧 Как запустить бота у себя?

### 1. Клонируйте репозитории

bash
git clone https://github.com/z0diac0624/z0diac_Qwen_bot.py.git 
git clone https://github.com/y13sint/FreeQwenApi.git 

### 2. Установите зависимости:
bash
pip install -r requirements.txt

Требуемые библиотеки:                   
python-telegram-bot        
requests         
easyocr           

### 3. Заполните конфигурационные данные:
Создай файл .env и добавь туда:
TELEGRAM_BOT_TOKEN=ваш_токен
API_BASE_URL=адрес_прокси_api

### 4. Запустите api и бота:           
npm install       
npm start   
python bot.py    

📌 Важно
Бот работает только через сторонний API, предоставленный неофициально.

💬 Автор
GitHub: [z0diac0624](https://github.com/z0diac0624)

Если есть вопросы, предложения по улучшению или нашли ошибки — создавайте issue в репозитории.

❤️ Поддержка
Если проект вам понравился или оказался полезным — ставьте звёздочку ⭐ и делитесь с друзьями!
