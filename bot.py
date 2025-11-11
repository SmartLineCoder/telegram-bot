import os
import logging
import json
from datetime import datetime

# Import gspread for Google Sheets integration
import gspread

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from telegram.error import BadRequest

# ---- Basic logging setup ----
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---- Load Environment Variables ----
TOKEN = os.environ.get("TOKEN")

# ---- Validate Token ----
if not TOKEN:
    raise ValueError("Error: No TOKEN environment variable found. Please set it in Railway.")

# ---- User data storage ----
user_data = {}

# ---- Helper: Update Google Sheet ----
def update_sheet(user_id, name, phone, governorate):
    """
    Connects to Google Sheets using service account credentials
    and appends a new row with the user's data.
    """
    try:
        # Load credentials from environment variable
        creds_json_str = os.environ.get('GSPREAD_SERVICE_ACCOUNT_CREDS')
        if not creds_json_str:
            logging.error("GSPREAD_SERVICE_ACCOUNT_CREDS environment variable not found.")
            return
            
        creds_dict = json.loads(creds_json_str)
        
        # Authorize and connect to Google Sheets
        gc = gspread.service_account_from_dict(creds_dict)
        
        # Open the spreadsheet by its name
        spreadsheet_name = "Zyad Telegram Bot Responses"
        sh = gc.open(spreadsheet_name)
        
        # Select the first worksheet
        worksheet = sh.sheet1
        
        # Prepare the data row
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        row_to_insert = [str(user_id), name, phone, governorate, timestamp]
        
        # Append the new row to the sheet
        worksheet.append_row(row_to_insert, value_input_option='USER_ENTERED')
        
        logging.info(f"Successfully wrote data for user {name} to Google Sheet.")
        
    except gspread.exceptions.SpreadsheetNotFound:
        logging.error(f"Error: Spreadsheet '{spreadsheet_name}' not found. "
                      "Please check the name and ensure the service account has editor access.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while updating the Google Sheet: {e}")


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
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# ---- Button callback ----
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except BadRequest as e:
        if "Query is too old" in str(e):
            logging.warning("CallbackQuery 'is too old' to be answered. Continuing...")
        else:
            raise e

    user_id = query.from_user.id
    if query.data == "form":
        user_data[user_id] = {"step": "ask_name"}
        await query.message.reply_text("سؤال 1️⃣: اتشرف باسمك الثنائي 🙏")
    elif query.data == "call":
        await query.message.reply_text("📞 تقدر تتواصل معايا على الرقم: 097554433")

# ---- Message handler ----
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") is None:
        await update.message.reply_text("ابدأ المحادثة بكتابة /start 😊")
        return

    text = update.message.text
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
        
        # --- NEW: Call the function to update the Google Sheet ---
        update_sheet(user_id, data["name"], data["phone"], data["governorate"])
        
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
        
        user_data.pop(user_id, None)

# ---- Main execution block ----
def main():
    """Start the bot."""
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logging.info("Starting bot...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()