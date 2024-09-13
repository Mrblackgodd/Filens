import os
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load your bot token directly
TOKEN = '7388471602:AAE7jQNyFJ9vfMulivEZGYPfURjHMNBxilk'

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
    try:
        # Check if the message is forwarded
        message = update.message
        if message.forward_date:
            logger.info("Received a forwarded message.")
            # Forwarded messages might contain files in different ways, extract it
            file = message.document or message.audio or message.video or (message.photo[-1] if message.photo else None)
        else:
            logger.info("Received a normal message.")
            # Non-forwarded messages
            file = message.document or message.audio or message.video or (message.photo[-1] if message.photo else None)

        if file:
            file_id = file.file_id
            logger.info(f"Received file with ID: {file_id}")

            # Fetch the file metadata from Telegram
            new_file = context.bot.get_file(file_id)
            file_path = new_file.file_path

            if file_path:
                logger.info(f"File path retrieved: {file_path}")
                # Construct the file download URL
                telegram_file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
                update.message.reply_text(f"Here is your direct download link: {telegram_file_url}")
            else:
                logger.error("File path not found in the API response.")
                update.message.reply_text("Sorry, I couldn't retrieve the file path. Please try again.")
        
        else:
            logger.warning("No valid file was found in the update message.")
            update.message.reply_text("Please send a valid file!")

    except Exception as e:
        logger.error(f"Error occurred while handling the file: {e}", exc_info=True)
        update.message.reply_text("An error occurred while processing the file. Please try again later.")

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
