import os, json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from groq_helper import ask_groq

BOT_TOKEN = os.getenv("BOT_TOKEN")
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Shizuka replies to every text message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    if not user_message:
        return

    await update.message.chat.send_action(action="typing")

    try:
        reply = await ask_groq(user_message)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Kuch error aaya re...")

# Add message handler (no command needed)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Vercel handler
async def handler(request):
    body = await request.body()
    update = Update.de_json(json.loads(body), app.bot)
    await app.process_update(update)
    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True})
    }

