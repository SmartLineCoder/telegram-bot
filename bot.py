import os
import smtplib
import logging
from datetime import datetime
from email.message import EmailMessage

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ---- Basic logging setup ----
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---- Load Environment Variables ----
TOKEN = os.environ.get("TOKEN")
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = "isma3lawy89@gmail.com" # You can also make this an environment variable if you wish

# ---- VALIDATE TOKEN ----
if not TOKEN:
    raise ValueError("Error: No TOKEN environment variable found. Please set it in Railway.")

# ---- User data storage ----
user_data = {}

# ---- Helper: Send email ----
def send_email(user_id, name, phone, governorate):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        logging.error("Email credentials (EMAIL_ADDRESS, EMAIL_PASSWORD) not set. Cannot send email.")
        return

    msg = EmailMessage()
    msg['Subject'] = f"New Telegram Bot Submission: {name}"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg.set_content(
        f"User ID: {user_id}\n"
        f"Name: {name}\n"
        f"Phone: {phone}\n"
        f"Governorate: {governorate}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            logging.info(f"Email sent successfully for user {name}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

# ---- Start command ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("املى الفورم", callback_data="form"),
            InlineKeyboardButton("الاتصال بيا", callback_data="call")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "👋 عامل ايه! معاك **زياد حاتم** من Limitless Org 💪\n\n"
        "هنتابع مع بعض الكورس والمحاضرات الفترة الجاية ❤️\n\n"
        "اختار طريقة المتابعة 👇"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# ---- Button callback ----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "form":
        user_data[user_id] = {"step": "ask_name"}
        await query.message.reply_text("سؤال 1️⃣: اتشرف باسمك الثنائي 🙏")
    elif query.data == "call":
        await query.message.reply_text("📞 تقدر تتواصل معايا على الرقم: 097554433")

# ---- Message handler ----
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data or user_data[user_id].get("step") is None:
        await update.message.reply_text("ابدأ المحادثة بكتابة /start 😊")
        return

    step = user_data[user_id]["step"]

    if step == "ask_name":
        user_data[user_id]["name"] = text
        user_data[user_id]["step"] = "ask_phone"
        await update.message.reply_text("سؤال 2️⃣: رقم تلفونك 📱")
    elif step == "ask_phone":
        user_data[user_id]["phone"] = text
        user_data[user_id]["step"] = "ask_governorate"
        await update.message.reply_text("سؤال 3️⃣: من أي محافظة؟ 🌍")
    elif step == "ask_governorate":
        user_data[user_id]["governorate"] = text
        data = user_data[user_id]
        # Send email after collecting all info
        send_email(user_id, data["name"], data["phone"], data["governorate"])
        # Send links to user
        FORM_LINK = "https://forms.gle/grkZJ94QsVXbDEab7"
        CHANNEL_LINK = "https://t.me/+eAJ8mUKydElhYTY0"
        await update.message.reply_text(
            f"حلو جدًا 😍 املى الفورم ده وهيجيلك لينك قناة الكورس المجاني:\n\n{FORM_LINK}"
        )
        await update.message.reply_text(
            f"بعد ما تملأ الفورم ✍️، ادخل هنا 👇\n{CHANNEL_LINK}\n\n"
            "اعمل **انضمام** وتابع القناة، وهيوصلك عليها لينك الكورس المجاني 🎓\n"
            "ومتنساش تعمل متابعة على كل السوشيال ميديا 😉❤️",
            parse_mode="Markdown"
        )
        user_data[user_id]["step"] = "done"

# ---- Main execution block ----
def main():
    """Start the bot."""
    # Create the Application
    app = ApplicationBuilder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Run the bot
    logging.info("Starting bot polling...")
    app.run_polling()

if __name__ == "__main__":
    main()