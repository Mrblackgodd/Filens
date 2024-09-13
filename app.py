import os
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask, request
from threading import Thread

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the Flask app
app = Flask(__name__)
bot = Bot(token=TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message when the command /start is issued."""
    update.message.reply_text('Hi! Send or forward me any file, and I will give you a direct download link.')

def handle_files(update: Update, context: CallbackContext) -> None:
    """Handle files sent or forwarded by users."""
    file = update.message.document or update.message.audio or update.message.video or update.message.photo[-1] if update.message.photo else None

    if file:
        file_id = file.file_id
        
        # Fetch the file path using the file ID
        new_file = context.bot.get_file(file_id)
        telegram_file_url = f"https://api.telegram.org/file/bot{TOKEN}/{new_file.file_path}"

        # Respond with the Telegram file URL
        update.message.reply_text(f"Here is your direct download link: {telegram_file_url}")
    else:
        update.message.reply_text("Please send a valid file!")

def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))

    # Handle all file types
    dp.add_handler(MessageHandler(Filters.document | Filters.audio | Filters.video | Filters.photo, handle_files))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle updates from Telegram webhook."""
    update = Update.de_json(request.get_json(), bot)
    updater.dispatcher.process_update(update)
    return 'ok', 200

def run_flask():
    """Run the Flask app to serve webhook."""
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    # Run both bot and Flask app in parallel
    Thread(target=run_bot).start()
    Thread(target=run_flask).start()
