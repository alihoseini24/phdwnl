import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Enable logging
logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# --- DUMMY WEB SERVER FOR RENDER FREE TIER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_health_server():
    # Render automatically provides a PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logging.info(f"Health check server running on port {port}")
    server.serve_forever()
# ---------------------------------------------

def search_and_extract(query: str, limit=3):
    search_url = f"phsearch{limit}:{query}"
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.pornhub.com'
        }
    }
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        results.append({'title': entry.get('title'), 'url': entry.get('url')})
    except Exception as e:
        logging.error(f"Search/Extraction failed: {e}")
    return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a keyword or model name, and I'll find download links.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"Searching for '{query}'...")
    videos = search_and_extract(query)
    
    if not videos:
        await update.message.reply_text("❌ No results found.")
        return

    for video in videos:
        title = video.get('title')
        dl_link = video.get('url')
        if dl_link:
            caption = f"🎬 **{title}**\n\n[🔗 Click Here to Download/Watch Direct MP4]({dl_link})"
            await update.message.reply_text(caption, parse_mode="Markdown")

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

    # Start the dummy server in a separate thread before launching the bot loop
    threading.Thread(target=run_health_server, daemon=True).start()

    # Launch Telegram Bot Polling
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()        return

    for video in videos:
        title = video.get('title')
        dl_link = video.get('url')
        
        if dl_link:
            caption = f"🎬 **{title}**\n\n[🔗 Click Here to Download/Watch Direct MP4]({dl_link})"
            await update.message.reply_text(caption, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
