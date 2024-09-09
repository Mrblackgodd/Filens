import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Flask app
app = Flask(__name__)

# Bot Token and Channel ID configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Initialize the bot application
bot_app = Application.builder().token(TOKEN).build()

# Generate a download link from file_id
async def generate_download_link(context, file_id):
    file = await context.bot.get_file(file_id)
    return file.file_path  # Direct download URL

# Start command handler
async def start(update: Update, context):
    await update.message.reply_text("Send me a file, and I'll store it in a channel and give you a download link!")

# Handle file uploads
async def handle_file(update: Update, context):
    file = update.message.document or update.message.photo[-1] or update.message.video
    if file:
        # Forward file to the private channel
        forwarded_message = await context.bot.forward_message(
            chat_id=CHANNEL_ID,
            from_chat_id=update.message.chat_id,
            message_id=update.message.message_id
        )
        
        # Get file_id of the forwarded message
        file_id = (forwarded_message.document.file_id if forwarded_message.document 
                   else forwarded_message.photo[-1].file_id if forwarded_message.photo 
                   else forwarded_message.video.file_id)
        
        # Generate the download link
        download_url = await generate_download_link(context, file_id)
        
        # Send the download link back to the user
        await update.message.reply_text(f"Your file is stored in the channel. You can download it here: {download_url}")

# Webhook handler for Telegram updates
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    # Parse the incoming Telegram update
    update = Update.de_json(request.get_json(), bot_app.bot)
    bot_app.update_queue.put(update)
    return "ok"

# Automatically set the webhook when the app starts
async def set_webhook():
    webhook_url = f"{WEBHOOK_URL}/{TOKEN}"
    await bot_app.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

# Main function to add handlers and start the bot
async def main():
    # Add command and message handlers
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO | filters.VIDEO, handle_file))

    # Automatically set the webhook
    await set_webhook()
    
    # Start the bot
    await bot_app.initialize()  # Initialize the application
    await bot_app.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
    app.run(host="0.0.0.0", port=8443)
