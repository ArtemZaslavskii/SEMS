from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

from config import TELEGRAM_TOKEN
from api_weather import get_current_weather, get_forecast
from scraper import get_weather_news
from logger import log, get_history

# Состояния диалога
WAITING_CITY_WEATHER, WAITING_CITY_FORECAST = range(2)

# Главное меню — кнопки
MAIN_MENU = ReplyKeyboardMarkup(
    [
        [KeyboardButton("🌤 Текущая погода"), KeyboardButton("📅 Прогноз на 5 дней")],
        [KeyboardButton("📰 Новости о погоде"), KeyboardButton("📋 Моя история")],
    ],
    resize_keyboard=True
)


# ─── /start ───────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log(user.id, "START", f"@{user.username}")

    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я погодный бот. Вот что я умею:\n"
        "🌤 Текущая погода — по любому городу\n"
        "📅 Прогноз на 5 дней — по любому городу\n"
        "📰 Новости о погоде — свежие новости\n"
        "📋 Моя история — твои прошлые запросы\n\n"
        "Выбери действие кнопкой ниже 👇",
        reply_markup=MAIN_MENU
    )
    return ConversationHandler.END


# ─── Текущая погода ───────────────────────────────────────────────────────────

async def ask_city_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log(user.id, "MENU", "Текущая погода")

    await update.message.reply_text("🏙 Введи название города:")
    return WAITING_CITY_WEATHER


async def send_current_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    city = update.message.text.strip()

    log(user.id, "WEATHER_REQUEST", city)
    result = get_current_weather(city)
    log(user.id, "WEATHER_RESULT", result[:100])  # пишем первые 100 символов результата

    await update.message.reply_text(result, reply_markup=MAIN_MENU)
    return ConversationHandler.END


# ─── Прогноз на 5 дней ────────────────────────────────────────────────────────

async def ask_city_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log(user.id, "MENU", "Прогноз на 5 дней")

    await update.message.reply_text("🏙 Введи название города:")
    return WAITING_CITY_FORECAST


async def send_forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    city = update.message.text.strip()

    log(user.id, "FORECAST_REQUEST", city)
    result = get_forecast(city)
    log(user.id, "FORECAST_RESULT", result[:100])

    await update.message.reply_text(result, reply_markup=MAIN_MENU)
    return ConversationHandler.END


# ─── Новости ──────────────────────────────────────────────────────────────────

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log(user.id, "NEWS_REQUEST")

    await update.message.reply_text("⏳ Загружаю новости...")
    result = get_weather_news()
    log(user.id, "NEWS_RESULT", result[:100])

    await update.message.reply_text(result, reply_markup=MAIN_MENU)


# ─── История ──────────────────────────────────────────────────────────────────

async def send_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log(user.id, "HISTORY_REQUEST")

    result = get_history(user.id)
    await update.message.reply_text(result, reply_markup=MAIN_MENU)


# ─── Неизвестное сообщение ────────────────────────────────────────────────────

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Не понимаю. Используй кнопки меню 👇",
        reply_markup=MAIN_MENU
    )


# ─── Запуск бота ──────────────────────────────────────────────────────────────

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ConversationHandler обрабатывает диалоги с вводом города
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("🌤 Текущая погода"), ask_city_weather),
            MessageHandler(filters.Regex("📅 Прогноз на 5 дней"), ask_city_forecast),
        ],
        states={
            WAITING_CITY_WEATHER:   [MessageHandler(filters.TEXT & ~filters.COMMAND, send_current_weather)],
            WAITING_CITY_FORECAST:  [MessageHandler(filters.TEXT & ~filters.COMMAND, send_forecast)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.Regex("📰 Новости о погоде"), send_news))
    app.add_handler(MessageHandler(filters.Regex("📋 Моя история"), send_history))
    app.add_handler(MessageHandler(filters.TEXT, unknown))

    print("✅ Бот запущен! Нажми Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()