import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

load_dotenv()

from pipeline.rag import RAGEngine

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

rag = RAGEngine()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text

    await update.message.reply_text("Thinking...")

    answer = rag.answer(query)

    await update.message.reply_text(answer)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram RAG bot started")
    app.run_polling()


if __name__ == "__main__":
    main()
