from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import feedparser

import os
TOKEN = os.getenv("TOKEN")

FEEDS = [
    "https://competitions.archi/feed/",
    "https://www.archdaily.com/search/news/categories/competitions/rss",
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏛 Architecture Competition Scout\n\n"
        "/find — найти конкурсы\n"
        "/student — конкурсы для студентов\n"
        "/help — помощь"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/find — последние архитектурные конкурсы\n"
        "/student — только студенческие конкурсы\n"
        "/start — главное меню"
    )

def get_competitions(student_only=False):
    results = []

    keywords = ["competition", "architecture", "design", "urban", "open call", "award"]
    student_keywords = ["student", "students", "young architects", "university"]

    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")

            text = f"{title} {summary}".lower()

            if not any(k in text for k in keywords):
                continue

            if student_only and not any(k in text for k in student_keywords):
                continue

            results.append({
                "title": title,
                "link": link
            })

    return results[:7]

async def find(update: Update, context: ContextTypes.DEFAULT_TYPE):
    competitions = get_competitions()

    if not competitions:
        await update.message.reply_text("Пока не нашла новых конкурсов.")
        return

    message = "🏛 Найденные архитектурные конкурсы:\n\n"

    for item in competitions:
        message += f"• {item['title']}\n{item['link']}\n\n"

    await update.message.reply_text(message)

async def student(update: Update, context: ContextTypes.DEFAULT_TYPE):
    competitions = get_competitions(student_only=True)

    if not competitions:
        await update.message.reply_text("Пока не нашла студенческих конкурсов.")
        return

    message = "🎓 Конкурсы для студентов:\n\n"

    for item in competitions:
        message += f"• {item['title']}\n{item['link']}\n\n"

    await update.message.reply_text(message)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("find", find))
app.add_handler(CommandHandler("student", student))

app.run_polling()
