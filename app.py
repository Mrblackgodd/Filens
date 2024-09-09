from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio

app = Flask(__name__)

TOKEN = "6437645148:AAFDCW7nnMOO3Ha1jif_WdBSSsOAt4U-N5A"
WEBHOOK_URL = "https://filens.onrender.com"

# Create an instance of the Telegram bot
bot = Bot(token=TOKEN)

# Initialize the application
application = None

# Handler for processing files
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.document or update.message.video or update.message.photo:
        file = update.message.document or update.message.video or update.message.photo
        file_id = file.file_id
        file_path = (await bot.get_file(file_id)).file_path
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"

        # Reply with the file URL
        await update.message.reply_text(f"File received: {file_url}")

# Flask route to handle webhook requests
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, bot)
    application.update_queue.put(update)
    return "ok"

# Set the webhook for the Telegram bot
async def set_webhook():
    await bot.set_webhook(url=WEBHOOK_URL + f"/{TOKEN}")

# Main function to start the bot application
async def main():
    global application
    application = Application.builder().token(TOKEN).build()

    # Add handlers for different types of messages
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Video.ALL | filters.Photo.ALL, handle_file))
    
    await set_webhook()
    await application.start()
    await application.idle()

# Run the Flask app and start the Telegram bot application
if __name__ == "__main__":
    import asyncio
    # Run the bot application in the background
    asyncio.run(main())
    # Run the Flask web server
    app.run(host="0.0.0.0", port=10000)
