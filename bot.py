import html
import os
from dotenv import load_dotenv
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Update,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from jobs import get_relevant_jobs, is_junior

load_dotenv()

NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

WELCOME_TEXT = (
    "👋 <b>Welcome to Cyprus IT Jobs Helper!</b>\n\n"
    "I help junior developers and QA engineers "
    "track fresh IT vacancies in Cyprus.\n\n"
    "Choose an option below to get started 👇"
)

HELP_TEXT = (
    "ℹ️ <b>What I can do</b>\n\n"
    "🔎 /search - find fresh IT vacancies\n"
    "ℹ️ /help - show this message\n"
    "🏠 /start - back to the main menu\n\n"
    "🟢 marks vacancies with a junior-level title."
)


def main_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔎 Search jobs", callback_data="search"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            ]
        ]
    )


def back_menu():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="menu")]]
    )


def results_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="search"),
                InlineKeyboardButton("⬅️ Back", callback_data="menu"),
            ]
        ]
    )


def format_jobs(jobs):
    if not jobs:
        return (
            "🔎 <b>Job search</b>\n\n"
            "No matching vacancies right now. Please check back later."
        )
    lines = [f"🔎 <b>Found {len(jobs)} vacancies</b>\n"]
    for job in jobs[:10]:
        mark = "🟢 " if is_junior(job) else ""
        title = html.escape(job["title"])
        company = html.escape(job["company"])
        location = html.escape(job["location"])
        url = html.escape(job["url"], quote=True)
        lines.append(f'{mark}<a href="{url}">{title}</a>\n{company} · {location}\n')
    lines.append("🟢 = junior-level title")
    return "\n".join(lines)


async def build_results_text():
    try:
        jobs = await get_relevant_jobs()
        return format_jobs(jobs)
    except Exception:
        return "⚠️ Could not load vacancies right now. Please try again later."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME_TEXT, parse_mode=ParseMode.HTML, reply_markup=main_menu()
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode=ParseMode.HTML)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("⏳ Searching for vacancies...")
    text = await build_results_text()
    await message.edit_text(
        text,
        parse_mode=ParseMode.HTML,
        reply_markup=results_menu(),
        link_preview_options=NO_PREVIEW,
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "search":
        await query.edit_message_text("⏳ Searching for vacancies...")
        text = await build_results_text()
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=results_menu(),
            link_preview_options=NO_PREVIEW,
        )
        return

    if query.data == "help":
        text, markup = HELP_TEXT, back_menu()
    else:
        text, markup = WELCOME_TEXT, main_menu()

    await query.edit_message_text(
        text, parse_mode=ParseMode.HTML, reply_markup=markup
    )


async def post_init(application: Application):
    await application.bot.set_my_commands(
        [
            BotCommand("start", "Main menu"),
            BotCommand("search", "Find IT jobs"),
            BotCommand("help", "How to use the bot"),
        ]
    )


app = (
    Application.builder()
    .token(os.getenv("BOT_TOKEN"))
    .post_init(post_init)
    .build()
)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("search", search))
app.add_handler(CallbackQueryHandler(button))
print("Bot is running")
app.run_polling()