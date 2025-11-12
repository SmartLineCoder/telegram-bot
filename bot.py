import os
import logging
import json
from datetime import datetime
from threading import Thread # 🔹 استيراد Thread

# 🔹 Import Flask for the web server
from flask import Flask

# Import gspread for Google Sheets integration
import gspread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

# ---- Flask Web Server Setup for UptimeRobot ----
# 🔹 هذا هو الخادم الصغير الذي سيبقي البوت نشطًا
flask_app = Flask(__name__)

@flask_app.route('/health')
def health_check():
    """هذه هي الصفحة التي سيزورها UptimeRobot."""
    return "OK, bot is running.", 200

def run_flask():
    """دالة لتشغيل خادم Flask."""
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --------------------------------------------------

# ---- Logging ----
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---- Environment Variables ----
TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("Error: No TOKEN environment variable found. Please set it in Railway.")

# ---- User Data ----
user_data = {}

# ---- Google Sheets Integration ----
def update_sheet(user_id, name, phone, governorate):
    try:
        creds_json_str = os.environ.get('GSPREAD_SERVICE_ACCOUNT_CREDS')
        if not creds_json_str:
            logging.error("GSPREAD_SERVICE_ACCOUNT_CREDS environment variable not found.")
            return

        creds_dict = json.loads(creds_json_str)
        gc = gspread.service_account_from_dict(creds_dict)

        spreadsheet_name = "Zyad Telegram Bot Responses"
        sh = gc.open(spreadsheet_name)
        worksheet = sh.sheet1

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row_to_insert = [str(user_id), name, phone, governorate, timestamp]
        worksheet.append_row(row_to_insert, value_input_option='USER_ENTERED')

        logging.info(f"Successfully wrote data for user {name} to Google Sheet.")

    except gspread.exceptions.SpreadsheetNotFound:
        logging.error(f"Spreadsheet '{spreadsheet_name}' not found or access denied.")
    except Exception as e:
        logging.error(f"Error updating Google Sheet: {e}")

# ---- Start ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("املى الفورم", callback_data="form"),
            InlineKeyboardButton("تواصل معايا", callback_data="call")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "👋 عامل ايه! معاك **زياد حاتم** من Limitless Org 💪\n\n"
        "هنتابع مع بعض الكورس والمحاضرات الفترة الجاية ❤️"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# ---- Button Handler ----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        if "Query is too old" in str(e):
            logging.warning("CallbackQuery 'is too old' to be answered.")
        else:
            raise e

    user_id = query.from_user.id

    if query.data == "form":
        user_data[user_id] = {"step": "ask_name"}
        await query.message.reply_text("تمام جدًا! في البداية خليني أتعرف عليك قبل ما نبدأ.")
        await query.message.reply_text("اتشرف باسمك، يا ريت يكون ثنائي أفضل 🙏")

    elif query.data == "call":
        await query.message.reply_text("تقدر تتواصل معايا على الرقم: +201143285703 ابعتلي رسالة علي الواتساب أو التليجرام بأسمك وأنا هتواصل معاك.")

    elif query.data == "form_filled":
        if user_data.get(user_id, {}).get("step") == "awaiting_form_confirmation":
            CHANNEL_LINK = "https://t.me/+eAJ8mUKydElhYTY0"
            first_name = user_data[user_id].get("first_name", "") # نحصل على الاسم الأول
            await query.message.reply_text(
                f"ممتاز جدًا يا {first_name}! شكرًا ليك 🙏\n\n"
                f"تقدر دلوقتي تدخل على قناة الكورس من هنا 👇\n{CHANNEL_LINK}\n\n"
                "اعمل **انضمام** (Join) وتابع القناة، وهيوصلك عليها لينك الكورس المجاني 🎓\n"
                "ومتنساش تعمل متابعة على كل السوشيال ميديا 😉❤️",
                parse_mode="Markdown"
            )
            user_data.pop(user_id, None)
        else:
            await query.message.reply_text("لو سمحت ابدأ المحادثة من الأول بكتابة /start 😊")

# ---- Message Handler ----
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") is None:
        await update.message.reply_text("ابدأ المحادثة بكتابة /start 😊")
        return

    text = update.message.text.strip()
    step = user_data[user_id]["step"]

    if step == "ask_name":
        full_name = text.title()
        first_name = full_name.split()[0] if len(full_name.split()) > 0 else full_name
        user_data[user_id]["name"] = full_name
        user_data[user_id]["first_name"] = first_name
        user_data[user_id]["step"] = "ask_phone"
        await update.message.reply_text(f"أهلاً بيك يا {first_name}! اتشرفت بيك ✨\n\nممكن أعرف رقم تليفونك الشخصي 📱؟")

    elif step == "ask_phone":
        user_data[user_id]["phone"] = text
        first_name = user_data[user_id]["first_name"]
        user_data[user_id]["step"] = "ask_governorate"
        await update.message.reply_text(f"تمام, آخر حاجة يا {first_name}. أنت من محافظة إيه؟ 🌍")

    elif step == "ask_governorate":
        user_data[user_id]["governorate"] = text
        data = user_data[user_id]

        update_sheet(user_id, data["name"], data["phone"], data["governorate"])

        FORM_LINK = "https://forms.gle/grkZJ94QsVXbDEab7"
        first_name = data["first_name"]

        await update.message.reply_text(
            f"حلو جدًا يا {first_name}! شكرًا على وقتك 🙏\n"
            f"املى الفورم ده علشان تأكد تسجيلك وهيجيلك لينك قناة الكورس المجاني:\n\n{FORM_LINK}"
        )

        keyboard = [[InlineKeyboardButton("✅ مليت الفورم", callback_data="form_filled")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "بعد ما تخلص الفورم، دوس على الزرار اللي تحت ده علشان تاخد لينك القناة 👇",
            reply_markup=reply_markup
        )

        user_data[user_id]["step"] = "awaiting_form_confirmation"

# ---- Main ----
def main():
    # 🔹 تشغيل خادم Flask في خيط منفصل
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    logging.info("Flask web server started in a background thread.")

    # إنشاء تطبيق تيليجرام
    app = ApplicationBuilder().token(TOKEN).build()
    
    # إضافة المعالجات (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # بدء تشغيل البوت
    logging.info("Starting Telegram bot polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()