from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8518319663:AAGvH7qTbS8pqUKcwLFDLNkMyKu8wg9-n28"
FORM_LINK = "https://forms.gle/WsyecUZ1kotdNTwv5"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"مرحباً! فضلاً املأ هذا الفورم: {FORM_LINK}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
