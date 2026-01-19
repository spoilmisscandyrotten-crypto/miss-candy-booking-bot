import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

NAME, AGE, CITY, BOOKING_TYPE, WINDOW = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Screening required.\n\nWhat is your full name?"
    )
    return NAME

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text("Age (21+ only):")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text.strip()
    await update.message.reply_text("City:")
    return CITY

async def city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()
    keyboard = [["Same-Day Incall"], ["Future Booking"]]
    await update.message.reply_text(
        "Select booking type:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return BOOKING_TYPE

async def booking_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text.strip()
    keyboard = [["Early Afternoon"], ["Late Afternoon"], ["Evening"]]
    await update.message.reply_text(
        "Select a time window:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )
    return WINDOW

async def window(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["window"] = update.message.text.strip()

    summary = (
        "📋 NEW BOOKING REQUEST\n\n"
        f"Name: {context.user_data['name']}\n"
        f"Age: {context.user_data['age']}\n"
        f"City: {context.user_data['city']}\n"
        f"Type: {context.user_data['type']}\n"
        f"Window: {context.user_data['window']}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
    await update.message.reply_text(
        "Request submitted. You’ll be notified if approved."
    )

    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, city)],
            BOOKING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, booking_type)],
            WINDOW: [MessageHandler(filters.TEXT & ~filters.COMMAND, window)],
        },
        fallbacks=[],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
