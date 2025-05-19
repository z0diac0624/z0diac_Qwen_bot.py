import requests
import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import easyocr

# Настройки
API_BASE_URL = "" #Укажите свой host, можно найти при запуске freeqwenapi в терминале.
TELEGRAM_BOT_TOKEN = "" #Укажите токен телеграмм бота в .env *botFather как пример*

# Доступные модели с описаниями
AVAILABLE_MODELS = {
    "qwen-max-latest": "| Языковая | Самая мощная. Сложные задачи, рассуждения.",
    "qwen-plus-2025-01-25": "| Языковая | Компромисс между ценой и качеством.",
    "qwen2.5-coder-32b-instruct": "| Кодогенерация | Программирование.",
    "qwen2.5-omni-7b": "| Аудио+текст | Голосовые интерфейсы.",
    "qwen2.5-vl-32b": "| Текст+изображение | Анализ изображений."
}

# Инициализация EasyOCR
reader = easyocr.Reader(['ru', 'en'], gpu=True)

# Команды бота

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    default_model = "qwen2.5-omni-7b"
    user_data["model"] = default_model
    await update.message.reply_text(
        f"Привет! Я помогу тебе общаться с моделью через API.\n"
        f"По умолчанию выбрана модель: `{default_model}`\n"
        "Используй /help, чтобы узнать доступные команды."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — начать работу\n"
        "/help — показать список команд\n"
        "/models — посмотреть доступные модели\n"
        "/model [модель] — выбрать модель\n"
        "/newchat — начать новый диалог\n"
        "/clear — удалить текущий диалог\n"
        "Просто пиши мне сообщения, и я буду отправлять их модели."
    )

async def list_models(update: Update, context: ContextTypes.DEFAULT_TYPE):
    models_list = "\n".join([f"- `{model}` — {description}" for model, description in AVAILABLE_MODELS.items()])
    await update.message.reply_text(f"Доступные модели:\n{models_list}")

async def set_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    if not context.args:
        await update.message.reply_text("Укажите название модели после команды /model")
        return

    selected_model = context.args[0]
    if selected_model not in AVAILABLE_MODELS:
        await update.message.reply_text(
            f"Модель '{selected_model}' не найдена.\nДоступные модели: /models"
        )
        return

    # Сохраняем состояние пользователя
    user_data["model"] = selected_model
    await update.message.reply_text(f"Модель изменена на: `{selected_model}`")

# Начать новый диалог
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data

    try:
        response = requests.post(f"{API_BASE_URL}/api/chats")
        data = response.json()
        chat_id = data.get("chatId")

        if chat_id:
            user_data["chatId"] = chat_id
            default_model = "qwen2.5-omni-7b"
            user_data["model"] = default_model
            await update.message.reply_text(f"Новый диалог создан. ID: {chat_id} | Модель: {default_model}")
        else:
            await update.message.reply_text("Не удалось создать новый диалог.")

    except Exception as e:
        await update.message.reply_text(f"Ошибка при создании диалога: {e}")

# Получить историю текущего диалога
async def get_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    chat_id = user_data.get("chatId")

    if not chat_id:
        await update.message.reply_text("У вас нет активного диалога.")
        return

    try:
        response = requests.get(f"{API_BASE_URL}/api/chats/{chat_id}")
        history = response.json()

        if isinstance(history, list) and len(history) > 0:
            msg = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
            await update.message.reply_text(f"Последние сообщения:\n{msg}")
        else:
            await update.message.reply_text("История диалога пуста.")

    except Exception as e:
        await update.message.reply_text(f"Ошибка при получении истории: {e}")

# Удалить текущий диалог
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    chat_id = user_data.get("chatId")

    if not chat_id:
        await update.message.reply_text("У вас нет активного диалога.")
        return

    try:
        response = requests.delete(f"{API_BASE_URL}/api/chats/{chat_id}")
        if response.status_code == 200:
            user_data.clear()
            await update.message.reply_text("Диалог успешно удален.")
        else:
            await update.message.reply_text("Не удалось удалить диалог.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при удалении диалога: {e}")

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    user_message = update.message.text
    model = user_data.get("model", "qwen2.5-omni-7b")  # модель по умолчанию
    chat_id = user_data.get("chatId")

    payload = {
        "message": user_message,
        "model": model
    }

    if chat_id:
        payload["chatId"] = chat_id

    try:
        response = requests.post(f"{API_BASE_URL}/api/chat", json=payload)
        data = response.json()

        if not chat_id and "chatId" in data:
            user_data["chatId"] = data["chatId"]

        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа.")

        # Проверка длины ответа
        if len(answer) <= 1999:
            await update.message.reply_text(answer)
        else:
            # Сохраняем в файл
            file_path = "response.txt"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(answer)

            # Отправляем файл
            with open(file_path, "rb") as f:
                await update.message.reply_document(document=InputFile(f), filename="response.txt")

            # Удаляем файл
            os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при обращении к API: {e}")

# Обработка входящих фотографий
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"{user.id}_photo.jpg"
    await photo_file.download_to_drive(file_path)

    try:
        result = reader.readtext(file_path, detail=0)
        recognized_text = "\n".join(result)

        if recognized_text:
            await update.message.reply_text(f"Распознанный текст:\n{recognized_text}")
        else:
            await update.message.reply_text("Текст на изображении не найден.")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при распознавании текста: {e}")
    finally:
        os.remove(file_path)

# Запуск бота
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("models", list_models))
    app.add_handler(CommandHandler("model", set_model))
    app.add_handler(CommandHandler("newchat", new_chat))
    app.add_handler(CommandHandler("history", get_history))
    app.add_handler(CommandHandler("clear", clear_chat))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()