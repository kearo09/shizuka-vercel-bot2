# api/webhook.py

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os, json, aiohttp
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = ApplicationBuilder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌸 Shizuka is online!")

app.add_handler(CommandHandler("start", start))

async def get_shizuka_reply(user_msg):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
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
            result = await resp.json()
            return result["choices"][0]["message"]["content"].strip()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        await update.message.chat.send_action("typing")
        reply = await get_shizuka_reply(update.message.text)
        await update.message.reply_text(reply)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# FastAPI app
fastapi_app = FastAPI()

@fastapi_app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return {"status": "ok"}
