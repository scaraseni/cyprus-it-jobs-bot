import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я помогу найти IT-вакансии на Кипре 🚀"
    )


app = Application.builder().token(os.getenv("BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
print("Бот запущен")
app.run_polling()