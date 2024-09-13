import os
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load your bot token from environment variables
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the bot and logging
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
    file = update.message.document or update.message.audio or update.message.video or (update.message.photo[-1] if update.message.photo else None)

    if file:
        file_id = file.file_id
        logger.info(f"Received file with ID: {file_id}")

        try:
            # Get file details from Telegram servers
            new_file = context.bot.get_file(file_id)
            logger.info(f"File path retrieved: {new_file.file_path}")

            # Construct the Telegram file download URL
            telegram_file_url = f"https://api.telegram.org/file/bot{TOKEN}/{new_file.file_path}"
            update.message.reply_text(f"Here is your direct download link: {telegram_file_url}")

        except Exception as e:
            # Log and send error message if file retrieval fails
            logger.error(f"Error retrieving file: {e}")
            update.message.reply_text("Sorry, there was an error retrieving the file. Please try again.")
    else:
        update.message.reply_text("Please send a valid file!")

def error(update: Update, context: CallbackContext) -> None:
    """Log errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")

def run_bot():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command to start the bot
    dp.add_handler(CommandHandler("start", start))

    # Handle all file types: document, audio, video, photo
    dp.add_handler(MessageHandler(Filters.document | Filters.audio | Filters.video | Filters.photo, handle_files))

    # Log errors
    dp.add_error_handler(error)

    # Start polling updates from Telegram
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    run_bot()
