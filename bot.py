from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Say Hi", callback_data="hi")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Hello!", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"You clicked: {query.data}")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You wrote: {update.message.text}")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app.run_polling()
