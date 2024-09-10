import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize the Flask app
app = Flask(__name__)

# Create the Telegram application
application = Application.builder().token(TOKEN).build()

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to handle files
async def handle_file(update: Update, context):
    try:
        message = update.message
        if message.document:
            file_id = message.document.file_id
        elif message.photo:
            file_id = message.photo[-1].file_id
        elif message.video:
            file_id = message.video.file_id
        else:
            await message.reply_text("Unsupported file format.")
            return

        # Store the file in a private channel
        file = await context.bot.get_file(file_id)
        file_path = file.file_path

        # Reply with the download link
        download_link = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
        await message.reply_text(f"Download Link: {download_link}")
    
    except Exception as e:
        logger.error(f"Error handling file: {e}")
        await message.reply_text("Something went wrong!")

# Webhook route for Telegram updates
@app.route(f"/{TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

# Set webhook
async def set_webhook():
    webhook_url = WEBHOOK_URL + f"/{TOKEN}"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# Main function
async def main():
    # Add file handler
    application.add_handler(MessageHandler(filters.ALL & (filters.Document | filters.Photo | filters.Video), handle_file))

    # Set webhook
    await set_webhook()

    logger.info("Bot started")

if __name__ == "__main__":
    asyncio.run(main())
