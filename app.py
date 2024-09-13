import os
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize the bot
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
        # Retrieve the file ID from the message
        file_id = file.file_id

        try:
            # Fetch the file object from Telegram API
            new_file = context.bot.get_file(file_id)

            # Generate the Telegram direct file download URL
            telegram_file_url = f"https://api.telegram.org/file/bot{TOKEN}/{new_file.file_path}"

            # Send the direct download URL to the user
            update.message.reply_text(f"Here is your direct download link: {telegram_file_url}")
        
        except Exception as e:
            # Log the error and inform the user if there's an issue
            logger.error(f"Error retrieving file: {e}")
            update.message.reply_text("Sorry, I couldn't retrieve the file. Please try again.")
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

    # Handle all file types (documents, audio, video, photos)
    dp.add_handler(MessageHandler(Filters.document | Filters.audio | Filters.video | Filters.photo, handle_files))

    # Log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    run_bot()
