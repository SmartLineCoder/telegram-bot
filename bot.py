from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import os

# إعداد Google Sheets
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
import json
CREDS = Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_CREDS"]), scopes=SCOPE)

client = gspread.authorize(CREDS)
sheet = client.open("Zyad Telegram Bot Responses").sheet1  # <-- اسم الشيت بالضبط

TOKEN = os.environ.get("TOKEN") or "ضع_التوكن_هنا"
FORM_LINK = "https://forms.gle/grkZJ94QsVXbDEab7"
CHANNEL_LINK = "https://t.me/+eAJ8mUKydElhYTY0"

user_data = {}

# دالة لتسجيل البيانات في Google Sheet
def log_to_sheet(user_id, name, phone, governorate):
    sheet.append_row([
        user_id,
        name,
        phone,
        governorate,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

# أول رسالة ترحيبية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 عامل ايه! معاك **زياد حاتم** من Limitless Org 💪\n\n"
        "هنتابع مع بعض الكورس والمحاضرات الفترة الجاية ❤️\n\n"
        "يلا نبدأ 💬"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")
    await update.message.reply_text("سؤال 1️⃣: اتشرف باسمك الثنائي 🙏")
    user_data[update.message.from_user.id] = {"step": "ask_name"}

# استقبال الردود
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("ابدأ المحادثة بكتابة /start 😊")
        return

    step = user_data[user_id].get("step")

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

        # تسجيل البيانات في Google Sheet
        log_to_sheet(
            user_id,
            user_data[user_id]["name"],
            user_data[user_id]["phone"],
            user_data[user_id]["governorate"]
        )

        # إرسال الفورم
        await update.message.reply_text(
            f"حلو جدًا 😍 املى الفورم ده وهيجيلك لينك قناة الكورس المجاني:\n\n{FORM_LINK}"
        )

        # بعد الفورم
        await update.message.reply_text(
            f"بعد ما تملأ الفورم ✍️، ادخل هنا 👇\n{CHANNEL_LINK}\n\n"
            "اعمل **انضمام** وتابع القناة، وهيوصلك عليها لينك الكورس المجاني 🎓\n\n"
            "ومتنساش تعمل متابعة على كل السوشيال ميديا 😉❤️",
            parse_mode="Markdown"
        )

        # نعتبره خلص
        user_data[user_id]["step"] = "done"

# إنشاء التطبيق
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

app.run_polling()
