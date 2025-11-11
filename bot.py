from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime
import os
import json
from google.oauth2.service_account import Credentials
import gspread

# Load the JSON string from Railway env variable
service_account_json_str = os.environ["SERVICE_ACCOUNT_JSON"]

# Convert it to a Python dict
SERVICE_ACCOUNT_INFO = json.loads(service_account_json_str)
# ---- Google Sheet setup ----
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPE)
client = gspread.authorize(CREDS)
sheet = client.open("Zyad Telegram Bot Responses").sheet1  # غير الاسم لو الشيت مختلف
# ---- Telegram bot setup ----
TOKEN = "ضع_التوكن_هنا"
FORM_LINK = "https://forms.gle/grkZJ94QsVXbDEab7"
CHANNEL_LINK = "https://t.me/+eAJ8mUKydElhYTY0"

user_data = {}

# تسجيل البيانات في Google Sheet
def log_to_sheet(user_id, name, phone, governorate):
    sheet.append_row([
        user_id,
        name,
        phone,
        governorate,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

# ---- أول رسالة ترحيبية ----
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

# ---- التعامل مع اختيار الزر ----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "form":
        user_data[user_id] = {"step": "ask_name"}
        await query.message.reply_text("سؤال 1️⃣: اتشرف باسمك الثنائي 🙏")
    elif query.data == "call":
        await query.message.reply_text("📞 تقدر تتواصل معايا على الرقم: 097554433")

# ---- استقبال الردود ----
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
        # تسجيل البيانات
        log_to_sheet(
            user_id,
            user_data[user_id]["name"],
            user_data[user_id]["phone"],
            user_data[user_id]["governorate"]
        )
        # إرسال الفورم + القناة
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

# ---- إنشاء التطبيق ----
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# ---- تشغيل البوت ----
app.run_polling()
