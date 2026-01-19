import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

CALENDAR_LINK = "https://bookwithmisscandynow.as.me/"

# Simple in-memory state (fast + clean)
user_state = {}

# ---------- START ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    user_state[uid] = {}

    await update.message.reply_text(
        "💎 Welcome.\n\n"
        "You’ve reached Miss Candy’s private booking assistant — "
        "this is the only place to access me directly.\n\n"
        "I’m selective by design. Not everyone gets through, "
        "but those who do are always glad they continued.\n\n"
        "This assistant will guide you through a short screening, "
        "then allow you to request time with me, explore exclusive content, "
        "or secure a more personal experience.\n\n"
        "Everything here is discreet, intentional, and handled properly.\n\n"
        "Let’s begin.\n\n"
        "How old are you? (18+ only)"
    )

# ---------- TEXT HANDLER ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text.strip()
    data = user_state.setdefault(uid, {})

    if "age" not in data:
        if not text.isdigit() or int(text) < 18:
            await update.message.reply_text("You must be 18+ to continue.")
            return
        data["age"] = text
        await update.message.reply_text("Height?")
        return

    if "height" not in data:
        data["height"] = text
        await update.message.reply_text("Ethnicity?")
        return

    if "ethnicity" not in data:
        data["ethnicity"] = text
        await update.message.reply_text("Gender?")
        return

    if "gender" not in data:
        data["gender"] = text
        await update.message.reply_text("Please send a clear selfie.")
        return

    # Booking info AFTER selfie
    if "selfie" in data:
        if "date" not in data:
            data["date"] = text
            await update.message.reply_text("Desired date? (YYYY-MM-DD)")
            return

        if "time" not in data:
            data["time"] = text
            await update.message.reply_text("Desired time?")
            return

        if "duration" not in data:
            data["duration"] = text
            await update.message.reply_text("Duration?")
            return

        if "location" not in data:
            data["location"] = text
            await send_to_admin(update, context)
            await update.message.reply_text(
                "Thank you.\n\n"
                "📅 Please select a time slot here:\n"
                f"{CALENDAR_LINK}\n\n"
                "Your request is pending approval."
            )
            return

# ---------- PHOTO HANDLER ----------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    data = user_state.setdefault(uid, {})
    data["selfie"] = update.message.photo[-1].file_id
    await update.message.reply_text("Desired date? (YYYY-MM-DD)")

# ---------- ADMIN KEYBOARD ----------
def admin_keyboard(uid):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}"),
            InlineKeyboardButton("❌ Deny", callback_data=f"deny_{uid}")
        ]
    ])

# ---------- SEND TO ADMIN ----------
async def send_to_admin(update, context):
    uid = update.effective_user.id
    d = user_state[uid]

    summary = (
        "📥 NEW REQUEST\n\n"
        f"Age: {d['age']}\n"
        f"Height: {d['height']}\n"
        f"Ethnicity: {d['ethnicity']}\n"
        f"Gender: {d['gender']}\n\n"
        f"Date: {d['date']}\n"
        f"Time: {d['time']}\n"
        f"Duration: {d['duration']}\n"
        f"Location: {d['location']}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=summary,
        reply_markup=admin_keyboard(uid)
    )

# ---------- APPROVE / DENY ----------
async def admin_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, uid = query.data.split("_")
    uid = int(uid)

    if action == "approve":
        await context.bot.send_message(
            chat_id=uid,
            text=(
                "💋 You’re approved.\n\n"
                "Finalize your booking here:\n"
                f"{CALENDAR_LINK}\n\n"
                "Payment details will be provided after confirmation."
            )
        )
        await query.edit_message_text("✅ Approved & calendar sent.")
    else:
        await context.bot.send_message(
            chat_id=uid,
            text="Not a match at this time."
        )
        await query.edit_message_text("❌ Denied.")

# ---------- CONTENT MENU ----------
async def content_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 MISS CANDY — PRIVATE MENU 🔥\n\n"
        "💎 Premium Photo Sets — $40–$75\n"
        "🎥 Custom Short Videos — from $60\n"
        "📱 Flirty Voice Notes — $25\n"
        "💬 Priority Chat Access — $100/day\n"
        "📞 Scheduled FaceTime — $150 / 10 min\n\n"
        "💸 Payment Methods:\n"
        "Cash App: $obeymisscandy\n"
        "Venmo: spoilmisscandyrotten\n"
        "Crypto: available via Telegram\n\n"
        "Reply with what you’d like 💋"
    )

# ---------- MAIN ----------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", content_menu))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(CallbackQueryHandler(admin_decision))

    app.run_polling()

if __name__ == "__main__":
    main()
