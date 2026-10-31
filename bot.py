import os
import logging
import zipfile
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 👉 PASTE YOUR TELEGRAM BOT TOKEN HERE
BOT_TOKEN = "9276287935:AAEqbRjEHjfYfJ9yKiiwpbDB3r_BJuLWKHU"

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🤖 **Zip & Compress Bot Online!**\n\n"
        "Send me *any* file (like large documents, scripts, or data files), and I will **compress it into a `.zip` archive** to reduce its size and send it right back to you!"
    )
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

# File compression handler
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_name = document.file_name
    
    await update.message.reply_text(
        f"📁 Received: `{file_name}`\n🗜️ Compressing file to reduce size...",
        parse_mode="Markdown"
    )

    try:
        os.makedirs("downloads", exist_ok=True)
        file_path = os.path.join("downloads", file_name)
        
        # Download file from Telegram
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(file_path)
        
        original_size = os.path.getsize(file_path)
        
        # Create a compressed zip file name
        base_name = os.path.splitext(file_name)[0]
        zip_file_name = f"{base_name}_compressed.zip"
        zip_path = os.path.join("downloads", zip_file_name)
        
        # Compress the file using Python's built-in zipfile module
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(file_path, arcname=file_name)
            
        compressed_size = os.path.getsize(zip_path)
        
        # Send the zipped file back to the user
        with open(zip_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=zip_file_name,
                caption=(
                    f"✅ **Compressed Successfully!**\n"
                    f"📦 Original Size: `{original_size / 1024:.2f} KB`\n"
                    f"🗜️ Zipped Size: `{compressed_size / 1024:.2f} KB`"
                ),
                parse_mode="Markdown"
            )
            
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to compress file: `{e}`", parse_mode="Markdown")

def main():
    if BOT_TOKEN == "YOUR_ACTUAL_BOT_TOKEN_HERE":
        print("❌ Error: Please replace '9276287935:AAEqbRjEHjfYfJ9yKiiwpbDB3r_BJuLWKHU' with your real Telegram bot token.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("🚀 Bot is polling for updates...")
    application.run_polling()

if __name__ == "__main__":
    main()
    