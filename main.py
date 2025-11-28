import random
import os
from telegram import Update, InputFile, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ConversationHandler

# =================================
TOKEN = "8501671598:AAEg_F6W1C1edXVFa7gXv9KcX9RtElseL9c"
ADMIN_ID = 8355775836  # Ganti dengan ID Telegram kamu
# =================================

EMAIL, JUMLAH, BROADCAST_WAIT = range(3)
USER_FILE = "users.txt"


def save_user(user_id):
    """Menyimpan user ke database txt"""
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            pass

    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")


def random_capital(email):
    return "".join(
        char.upper() if char.isalpha() and random.choice([True, False]) else char
        for char in email
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_user(update.effective_user.id)

    await update.message.reply_text(
        "🍉 *Welcome To Random Email*\n"
        "BY *SEMANGKA TG*\n\n"
        "Silakan masukkan email yang ingin diacak\n"
        "Contoh : `xxxxxxx@gmail.com`",
        parse_mode="Markdown"
    )
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("📌 Berapa banyak hasil yang ingin dibuat?")
    return JUMLAH


async def get_jumlah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jumlah = int(update.message.text)
    email = context.user_data["email"]
    filename = "hasil_email.txt"

    await update.message.reply_text("⏳ Sedang membuat file...")

    with open(filename, "w") as f:
        for _ in range(jumlah):
            f.write(random_capital(email) + "\n")

    await update.message.reply_document(InputFile(filename), caption="✔️ Selesai!")
    return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("🚫 Kamu bukan admin!")

    keyboard = [
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("📋 Total User", callback_data="total_user")],
    ]

    await update.message.reply_text("⚙️ Admin Panel:", reply_markup=InlineKeyboardMarkup(keyboard))


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return await query.edit_message_text("❌ Kamu tidak punya akses.")

    if query.data == "broadcast":
        await query.edit_message_text("📝 Ketik pesan broadcast:")
        return BROADCAST_WAIT

    elif query.data == "total_user":
        with open(USER_FILE, "r") as f:
            total = len(f.read().splitlines())
        await query.edit_message_text(f"👤 Total user saat ini: *{total}*", parse_mode="Markdown")


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text

    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()

    sent, failed = 0, 0

    for user in users:
        try:
            await context.bot.send_message(chat_id=user, text=f"📢 *Broadcast:*\n\n{message}", parse_mode="Markdown")
            sent += 1
        except:
            failed += 1

    await update.message.reply_text(f"✔️ Broadcast selesai!\n\nTerkirim: {sent}\nGagal: {failed}")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Proses dibatalkan.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
            JUMLAH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_jumlah)],
            BROADCAST_WAIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(admin_callback))

    print("BOT SEDANG BERJALAN...")
    app.run_polling()


if __name__ == "__main__":
    main()
