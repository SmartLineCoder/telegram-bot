from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ---- بيانات Google Service Account مباشرة داخل الكود ----
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "zyad-telegram-bot-responses",
  "private_key_id": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCjiaQC/AG7hXo3\n6LujjKOHT8Xxc0n93xXUu2cp2XlWdzUK5hyG3yPw/CMZo+lSzFr6YbCvJvYwVC/A\nxH5Pg/Gg/OQGCzSn5blEp+GzkYIQfyPUSgXhFNcDDmIcXrMdfJyaVV49Oni+gLTQ\nBWMfMuQsGlyPv7wduAztecmX3fEl+8Ja/ZCqhVqTCNMpIDcbauOYy+rFD/11jpfM\nmLyctpN6XyTW/koMOthG4SCHd3h4zmWAXcd9tYOHoWGSpL9aSH3mb6B6zZH5Ah5j\nuGqlUp50Xh5aLdrYG2gySPBDCSLJcQRMmSF4bJ6ctnNxGoey64u+iI27VJ9OOY8X\nbeiYwHbfAgMBAAECggEAAU1Dp0toouf9QE1U6Pl4rceHuEZf+UONIXACJxQuMbpf\n7Uc8EmjHmPbcyAAqoOBZZeBRscBDezkGxTCvAOrw3AwMBMEfFNds56DIGgXOkr+I\n+YKJTOpWn1HAuipIgdlMfw3R6mT1Uojb9+2PcU9rwzt8fT2XKuTi2razDW0mL/Ae\nBliGWcYROyktdWC7eKM6kHC0QOBj30TSViedvos8pE6KS8UJpzu5jQxv9dgfbTNr\nfmfurQRcqb31OyoAdgKnhvZUwW1TAG0GcJkaX/gnI7p9vk/F5hk7XSXI/jYBEfAe\npMYO1EU3WllpUbfwIQfwc9Wva1eQ5ojsEiLQqAjZ/QKBgQDO0pw1oStbxoMigfFB\nSv21E1cKPQ2NrC5ujSsiEvT/lkJPH1ffvd50gYRK3FNu8ybmHEEVcCc7KDS4dKPD\nrAZldQqU3j6YkrAp1S5UJZo87WpT2g8FfkE7z+OTxtuqys67BhcVVPz23/4Tqirm\n3YIdnAQgddOGZeOWSSc0YHni5QKBgQDKbEA+B5ydGUkmQFIBHbwooHoy9Zo9zj2T\nvO2UIOOF+w7D/IgdptMy2FjhbDtUD7lj0GgyBcDWlCUcwiWEl3XtrgS7I4k1EjGp\n07ox/bjdyEqt4Zl6pckArKGcWxvy/4R1FlgFscCsC2C74TPB5j//Y6RARtCy7PlS\nGbG3rPbCcwKBgBsyYsxCl1sILbJZ+Amn/NjU5Ds6cA/TNn/fHG7soz8A2VNiQcHw\nS9JyPZ1Cf841N0ZHLN/O0bnbvaML44UVl/m7fFq7JuwVTgkSOXdjQncEmVjRcew9\nAAMHgVuraLN629iIInzxohostlKLq/yT4EpYe8pw9BHWUCkxEXC3xw9pAoGBAKO6\nVWgW3g2P00P2SJ4QgA3YZ57qWxzcwZ/K89uZko7fV70ceLiLJE7/AT0sPvyqT0i1\n3GGBl824PCB7xL7vh3p9A+SeRK/BjJwR3ovq7mmtRQJJ9MtoZyF9gKaoZv3wwSG3\ntfC9Ktu9xDuTVzrh0yfuX3+CB/KBjNRkZgPsCheTAoGAc1w7PNeOiwKhTxPv+Gm/\nM/DPP5M/9exJAZiOz6xFKAez7fIRwVhoD3AMWB7o0L+E/TF0UX1pIX3Lbqt332wU\n3R1jGU9G/Nb/n76PXS83DZn1+omyYSU6dtqaNpeKQ6jgr3fZtlYOSep7Gg5w6Qaa\nGiDJU0gC1ZfjOTz0DrEos0k=\n-----END PRIVATE KEY-----\n",
  "client_email": "zeyadapi@zyad-telegram-bot-responses.iam.gserviceaccount.com",
  "client_id": "102176397830018730236",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/zeyadapi%40zyad-telegram-bot-responses.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPE)

# ---- Google Sheet setup ----
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
