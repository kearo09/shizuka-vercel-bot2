from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os, json, aiohttp, asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("BOT_TOKEN:", "✅" if BOT_TOKEN else "❌ MISSING")
print("GROQ_API_KEY:", "✅" if GROQ_API_KEY else "❌ MISSING")

# Create FastAPI app
app = FastAPI()

# Create Telegram bot application
bot_app = Application.builder().token(BOT_TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌸 Shizuka is online!")

bot_app.add_handler(CommandHandler("start", start))

# Groq reply
async def get_shizuka_reply(user_msg):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": "Reply like a cute Hinglish girl with short messages and emojis."},
            {"role": "user", "content": user_msg}
        ],
        "max_tokens": 100,
        "temperature": 0.8
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as resp:
            resp.raise_for_status()
            result = await resp.json()
            return result["choices"][0]["message"]["content"].strip()

# Message handler
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.chat.send_action("typing")
        reply = await get_shizuka_reply(update.message.text)
        await update.message.reply_text(reply)

bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# FastAPI POST endpoint for Telegram webhook
@app.post("/api/webhook")
async def telegram_webhook(request: Request):
    body = await request.json()
    update = Update.de_json(body, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}


