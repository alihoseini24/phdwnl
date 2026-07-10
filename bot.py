import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Enable logging
logging.basicConfig(level=logging.INFO)

TOKEN = "8963079163:AAGyZyJQpVWxlvF6X-n8c9zfJ4ZLnLzN0cc"

def search_and_extract(query: str, limit=3):
    """Uses yt-dlp to search Pornhub directly and extract matching download links."""
    # Use 'phsearch' prefix to tell yt-dlp to search Pornhub directly
    search_url = f"phsearch{limit}:{query}"
    
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'extract_flat': False, # Tells it to actually extract individual video data
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://www.pornhub.com'
        }
    }
    
    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_url, download=False)
            
            # Check if we got a playlist/list of search entries back
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'title': entry.get('title'),
                            'url': entry.get('url')
                        })
    except Exception as e:
        logging.error(f"Search/Extraction failed: {e}")
    
    return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a keyword, phrase, or model name, and I'll find download links.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    await update.message.reply_text(f"Searching for '{query}'...")
    
    videos = search_and_extract(query)
    
    if not videos:
        await update.message.reply_text("❌ No results found. Try changing your search term or model name.")
        return

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
