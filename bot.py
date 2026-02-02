from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

import copy as c
from config import BOT_TOKEN, ADMIN_CHAT_ID, TIMEZONE, DEPOSIT_PER_HOUR, INCALL_DEPOSIT_THRESHOLD_HOURS
from rules import parse_dt, requires_deposit, deposit_amount
from admin import is_admin

# Conversation states
S_BOOKING_TYPE, S_DATETIME, S_DURATION, S_SCREENING, S_DEPOSIT_WAIT = range(5)

# In-memory storage (OK for v1; later move to DB)
SESS = {}  # key: chat_id -> dict

def _get(chat_id):
    if chat_id not in SESS:
        SESS[chat_id] = {}
    return SESS[chat_id]

def start(update, context):
    update.message.reply_text(c.WELCOME + "\n" + c.DISCLAIMER)

def myid(update, context):
    update.message.reply_text(f"Your chat/user id is: {update.effective_user.id}")

def book(update, context):
    chat_id = update.effective_chat.id
    sess = _get(chat_id)
    sess.clear()
    update.message.reply_text(c.BOOK_INTRO)
    update.message.reply_text(c.ASK_BOOKING_TYPE)
    return S_BOOKING_TYPE

def handle_booking_type(update, context):
    chat_id = update.effective_chat.id
    sess = _get(chat_id)

    t = update.message.text.strip().lower()
    if t in ["1", "incall"]:
        sess["booking_type"] = "incall"
    elif t in ["2", "outcall"]:
        sess["booking_type"] = "outcall"
    else:
        update.message.reply_text("Reply with: incall or outcall (or 1 / 2).")
        return S_BOOKING_TYPE

    update.message.reply_text(c.ASK_DATETIME)
    return S_DATETIME

def handle_datetime(update, context):
    chat_id = update.effective_chat.id
    sess = _get(chat_id)

    try:
        dt = parse_dt(update.message.text, TIMEZONE)
    except Exception:
        update.message.reply_text("Couldn’t read that. Try: 2026-02-02 09:30 or 02/02 9:30am")
        return S_DATETIME

    sess["datetime"] = dt
    update.message.reply_text(c.ASK_DURATION)
    return S_DURATION

def handle_duration(update, context):
    chat_id = update.effective_chat.id
    sess = _get(chat_id)

    raw = update.message.text.strip().lower().replace("hours", "").replace("hour", "")
    try:
        dur = float(raw)
        if dur <= 0:
            raise ValueError()
    except Exception:
        update.message.reply_text("Reply with a number like 1, 1.5, 2, 3")
        return S_DURATION

    sess["duration"] = dur
    update.message.reply_text(c.ASK_SCREENING)
    return S_SCREENING

def handle_screening(update, context):
    chat_id = update.effective_chat.id
    sess = _get(chat_id)

    sess["screening"] = update.message.text.strip()

    # Evaluate deposit requirement
    booking_type = sess["booking_type"]
    dt = sess["datetime"]
    dur = sess["duration"]

    need = requires_deposit(booking_type, dt, INCALL_DEPOSIT_THRESHOLD_HOURS)

    update.message.reply_text(c.DEPOSIT_POLICY)

    if need:
        amt = deposit_amount(dur, DEPOSIT_PER_HOUR)
        sess["deposit_required"] = True
        sess["deposit_amount"] = amt
        update.message.reply_text(c.DEPOSIT_REQUIRED.format(amount=amt))
        update.message.reply_text(c.DEPOSIT_INSTRUCTIONS + "\n\nReply: sent")
        return S_DEPOSIT_WAIT
    else:
        sess["deposit_required"] = False
        update.message.reply_text(c.NO_DEPOSIT)
        update.message.reply_text(c.CONFIRMED + "\n" + c.DISCLAIMER)
        return ConversationHandler.END

def handle_deposit_wait(update, context):
    chat_id = update.effective_chat.id
    sess = _get(chat_id)

    msg = update.message.text.strip().lower()

    if msg == "sent":
        # In v1 this is manual confirmation. Admin can verify in messages.
        update.message.reply_text(c.CONFIRMED + "\n" + c.DISCLAIMER)
        return ConversationHandler.END

    update.message.reply_text("Reply “sent” after you’ve sent the deposit.")
    return S_DEPOSIT_WAIT

def cancel(update, context):
    update.message.reply_text("Canceled. Start again anytime with /book", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Admin commands
def admin_set(update, context):
    # This just reminds you to set ADMIN_CHAT_ID in config.py.
    update.message.reply_text("Set ADMIN_CHAT_ID in config.py (use /myid to get your id).")

def admin_last_slot(update, context):
    if not is_admin(update.effective_user.id, ADMIN_CHAT_ID):
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text=c.LAST_SLOT)

def admin_morning(update, context):
    if not is_admin(update.effective_user.id, ADMIN_CHAT_ID):
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text=c.MORNING_PUSH)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("myid", myid))
    dp.add_handler(CommandHandler("admin", admin_set))
    dp.add_handler(CommandHandler("lastslot", admin_last_slot))
    dp.add_handler(CommandHandler("morning", admin_morning))

    conv = ConversationHandler(
        entry_points=[CommandHandler("book", book)],
        states={
            S_BOOKING_TYPE: [MessageHandler(Filters.text & ~Filters.command, handle_booking_type)],
            S_DATETIME: [MessageHandler(Filters.text & ~Filters.command, handle_datetime)],
            S_DURATION: [MessageHandler(Filters.text & ~Filters.command, handle_duration)],
            S_SCREENING: [MessageHandler(Filters.text & ~Filters.command, handle_screening)],
            S_DEPOSIT_WAIT: [MessageHandler(Filters.text & ~Filters.command, handle_deposit_wait)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    dp.add_handler(conv)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()