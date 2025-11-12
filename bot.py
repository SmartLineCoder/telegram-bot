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
        # Note: query.message is used to reply to the message containing the button
        await query.message.reply_text(
            "تمام جدًا! في البداية خليني أتعرف عليك قبل ما نبدأ."
        )
        await query.message.reply_text("اتشرف باسمك، يا ريت يكون ثنائي أفضل 🙏")
        
    elif query.data == "call":
        await query.message.reply_text("تقدر تتواصل معايا على الرقم: +20 114 328 5703 ابعتلي رسالة علي الواتساب أو التليجرام بأسمك وأنا هتواصل معاك.")

    # --- NEW: Handle the form filled confirmation ---
    elif query.data == "form_filled":
        # Check if user is at the correct step
        if user_data.get(user_id, {}).get("step") == "awaiting_form_confirmation":
            CHANNEL_LINK = "https://t.me/+eAJ8mUKydElhYTY0"
            await query.message.reply_text(
                f"ممتاز جدًا! شكرًا ليك 🙏\n\n"
                f"تقدر دلوقتي تدخل على قناة الكورس من هنا 👇\n{CHANNEL_LINK}\n\n"
                "اعمل **انضمام** (Join) وتابع القناة، وهيوصلك عليها لينك الكورس المجاني 🎓\n"
                "ومتنساش تعمل متابعة على كل السوشيال ميديا 😉❤️",
                parse_mode="Markdown"
            )
            # End the conversation
            user_data.pop(user_id, None)
        else:
            await query.message.reply_text("لو سمحت ابدأ المحادثة من الأول بكتابة /start 😊")


# ---- Message handler ----
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_data or user_data[user_id].get("step") is None:
        await update.message.reply_text("ابدأ المحادثة بكتابة /start 😊")
        return

    text = update.message.text
    step = user_data[user_id]["step"]
    
    # Store the user's name to use in later messages
    name = user_data[user_id].get("name")

    if step == "ask_name":
        # Capitalize the first letter of each part of the name for a cleaner look
        user_name = text.title()
        user_data[user_id]["name"] = user_name
        user_data[user_id]["step"] = "ask_phone"
        await update.message.reply_text(f"عاش يا {user_name}! اتشرفت بيك جدًا ✨\n\nممكن أعرف رقم تليفونك الشخصي 📱؟")

    elif step == "ask_phone":
        user_data[user_id]["phone"] = text
        user_data[user_id]["step"] = "ask_governorate"
        await update.message.reply_text(f"تمام, آخر حاجة يا {name}. أنت من محافظة إيه؟ 🌍")

    elif step == "ask_governorate":
        user_data[user_id]["governorate"] = text
        data = user_data[user_id]
        
        # Update the Google Sheet with all collected data
        update_sheet(user_id, data["name"], data["phone"], data["governorate"])
        
        FORM_LINK = "https://forms.gle/grkZJ94QsVXbDEab7"
        
        # --- MODIFIED: Ask for confirmation instead of sending channel link ---
        await update.message.reply_text(
            f"حلو جدًا يا {data['name']}! شكرًا على وقتك. املى الفورم ده علشان تأكد تسجيلك وهيجيلك لينك قناة الكورس المجاني:\n\n{FORM_LINK}"
        )

        # Create the confirmation button
        keyboard = [[InlineKeyboardButton("✅ مليت الفورم", callback_data="form_filled")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "بعد ما تخلص الفورم، دوس على الزرار اللي تحت ده علشان تاخد لينك القناة 👇",
            reply_markup=reply_markup
        )
        
        # Set the next step to wait for the button click
        user_data[user_id]["step"] = "awaiting_form_confirmation"


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