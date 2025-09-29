import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# فعال‌سازی لاگ‌ها
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن توکن
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing.")

# ساخت اپلیکیشن تلگرام بدون polling
application = Application.builder().token(TOKEN).updater(None).build()
bot = Bot(token=TOKEN)

# هندلر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام حنا! بات آماده ارسال ویدیو از کانال پرایوت هست 🚀")

application.add_handler(CommandHandler("start", start))

# هندلر تست (دلخواه) برای بررسی آنلاین بودن
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("بات آنلاین و آماده‌ست ✅")
application.add_handler(CommandHandler("ping", ping))

# FastAPI اپلیکیشن
app = FastAPI()

# ثبت و حذف Webhook در lifecycle
@app.on_event("startup")
async def startup_event():
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not render_host:
        raise ValueError("RENDER_EXTERNAL_HOSTNAME missing in environment.")

    webhook_url = f"https://{render_host}/"
    logger.info(f"Setting webhook to {webhook_url}")
    await bot.set_webhook(webhook_url)
    logger.info("Webhook set successfully.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutdown: removing webhook.")
    await bot.delete_webhook()

# مسیر وبهوک
@app.post("/")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return {"status": "ok"}

# در Render از این استفاده میشه:
# Procfile: web: uvicorn bot:app --host 0.0.0.0 --port $PORT
# requirements.txt: python-telegram-bot==20.5, fastapi, uvicorn
