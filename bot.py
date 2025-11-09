from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

TOKEN = "8518319663:AAGvH7qTbS8pqUKcwLFDLNkMyKu8wg9-n28"
FORM_LINK = "https://forms.gle/WsyecUZ1kotdNTwv5"

user_data = {}  # لتخزين بيانات المستخدم مؤقتاً

# الخطوة 1: Start + Buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Form", callback_data="form")],
        [InlineKeyboardButton("Call me", callback_data="call")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحباً! اختر أحد الخيارات:", reply_markup=reply_markup)

# الخطوة 2: التعامل مع أزرار المستخدم
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "form":
        await query.message.reply_text("أولاً، ما اسمك؟")
        user_data[query.from_user.id] = {"step": "ask_name"}
    elif query.data == "call":
        await query.message.reply_text("سوف نتواصل معك قريباً. فضلاً اترك رقمك هنا.")
        user_data[query.from_user.id] = {"step": "ask_phone"}

# الخطوة 3: استقبال الردود
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_data:
        step = user_data[user_id].get("step")
        
        if step == "ask_name":
            user_data[user_id]["name"] = update.message.text
            await update.message.reply_text(f"شكراً {update.message.text}! فضلاً املأ هذا الفورم: {FORM_LINK}")
            user_data[user_id]["step"] = "filled_form"
            
        elif step == "ask_phone":
            user_data[user_id]["phone"] = update.message.text
            await update.message.reply_text(f"شكرًا! سنتواصل معك قريباً على الرقم: {update.message.text}")
            user_data[user_id]["step"] = "done"

# إنشاء التطبيق
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app.run_polling()