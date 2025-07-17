import os
import aiohttp
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters
)
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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
            resp.raise_for_status()
            resp_json = await resp.json()
            return resp_json["choices"][0]["message"]["content"].strip()

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hii, I'm alive on Vercel 😋")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    await update.message.chat.send_action("typing")
    await asyncio.sleep(2)
    reply = await get_shizuka_reply(update.message.text)
    await update.message.reply_text(reply)

# Entrypoint for Vercel
async def webhook(request):
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    body = await request.json()
    update = Update.de_json(body, app.bot)

    await app.initialize()
    await app.process_update(update)

    return {
        "statusCode": 200,
        "body": "ok"
    }
