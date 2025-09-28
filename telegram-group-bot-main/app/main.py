from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram import Update
from telegram.ext import Application, CommandHandler
import os, logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Telegram Bot setup ---
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL")

telegram_app = Application.builder().token(BOT_TOKEN).build()

# Example handler
async def start(update: Update, context):
    await update.message.reply_text("✅ Bot is running on Render!")

telegram_app.add_handler(CommandHandler("start", start))

# --- Routes ---
@app.get("/")
async def home():
    return {"status": "ok", "msg": "Bot running"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.process_update(update)
        return JSONResponse({"ok": True})
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# --- Startup: Set webhook ---
@app.on_event("startup")
async def startup():
    if BOT_TOKEN and WEBHOOK_BASE_URL:
        url = f"{WEBHOOK_BASE_URL}/webhook"
        await telegram_app.bot.set_webhook(url)
        logger.info(f"🚀 Webhook set to {url}")
