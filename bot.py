import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "7949012398:AAHck6r-9zmx1ZDuP0SbhEaWNRRRfow4798"
CHANNEL_ID = -1002814237158
MESSAGE_IDS = [2, 3]

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        {"text": "📹 ارسال ویدیوها", "callback_data": "send_videos"}
    ]]
    await update.message.reply_text(
        "سلام! روی دکمه زیر کلیک کن تا ویدیوها برات ارسال بشن.",
        reply_markup={"inline_keyboard": keyboard}
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    for mid in MESSAGE_IDS:
        await bot.forward_message(
            chat_id=update.effective_chat.id,
            from_chat_id=CHANNEL_ID,
            message_id=mid
        )
        await asyncio.sleep(2)

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))

async def lifespan(app: FastAPI):
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/"
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook set to: {webhook_url}")
    yield
    print("🛑 App shutting down...")

app = FastAPI(lifespan=lifespan)

@app.post("/")
async def telegram_webhook(request: Request):
    json_data = await request.json()
    update = Update.de_json(json_data, bot)
    await application.update_queue.put(update)
    return {"status": "ok"}
