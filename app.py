import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.constants import ParseMode

app = Flask(__name__)

TOKEN = 'YOUR_BOT_TOKEN'  # Replace with your bot token
WEBHOOK_URL = 'https://your-webhook-url'  # Replace with your Render service URL

async def handle_file(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    file = update.message.document or update.message.video or update.message.photo
    if file:
        file_id = file.file_id
        file_info = await context.bot.get_file(file_id)
        file_url = file_info.file_path
        # Send the file URL back to the user
        await context.bot.send_message(chat_id, f"Here is your download link: {file_url}")

async def set_webhook() -> None:
    bot = Bot(token=TOKEN)
    await bot.set_webhook(url=WEBHOOK_URL)

async def main() -> None:
    # Initialize the application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(MessageHandler(filters.Document.ALL | filters.Photo.ALL | filters.Video.ALL, handle_file))

    # Set webhook
    await set_webhook()

    # Start the application
    await application.run_polling()

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook() -> str:
    json_str = request.get_data(as_text=True)
    update = Update.de_json(json_str, Bot(token=TOKEN))
    application = Application.builder().token(TOKEN).build()
    application.process_update(update)
    return 'ok'

if __name__ == '__main__':
    # Run the Flask server
    app.run(port=8443, debug=True, host='0.0.0.0')
