import os
import zipfile
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Yahan apna Bot Token seedha daal do
BOT_TOKEN = "9276287935:AAEqbRjEHjfYfJ9yKiiwpbDB3r_BJuLWKHU"

# Render ke liye chhota sa dummy web server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Server ko background thread mein chalu karna
threading.Thread(target=run_server, daemon=True).start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Koi bhi file ya document bhejo, main usko turant .zip bana kar bhej dunga.")

async def make_zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc:
        await update.message.reply_text("Bhai, kripya koi document ya file bhejo.")
        return

    file_name = doc.file_name
    await update.message.reply_text("⏳ File zip ho rahi hai, thoda intezaar karo...")

    os.makedirs("downloads", exist_ok=True)
    file_path = os.path.join("downloads", file_name)
    
    file = await context.bot.get_file(doc.file_id)
    await file.download_to_drive(file_path)
    
    zip_name = file_name + ".zip"
    zip_path = os.path.join("downloads", zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, arcname=file_name)
        
    with open(zip_path, 'rb') as f:
        await update.message.reply_document(document=f, filename=zip_name, caption="✅ Lo bhai, zip file taiyar hai!")

    try:
        os.remove(file_path)
        os.remove(zip_path)
    except:
        pass

def main():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, make_zip))
    print("Bot start ho gaya hai...")
    app.run_polling()

if __name__ == "__main__":
    main()
