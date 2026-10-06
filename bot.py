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
from storage import load_json, save_json

load_dotenv()

CHECK_INTERVAL_SECONDS = 3 * 60 * 60
NO_PREVIEW = LinkPreviewOptions(is_disabled=True)

WELCOME_TEXT = (
    "👋 <b>Welcome to Cyprus IT Jobs Helper!</b>\n\n"
    "I help junior developers and QA engineers "
    "track fresh IT vacancies in Cyprus.\n\n"
    "Choose an option below to get started 👇"
)

HELP_TEXT = (
    "ℹ️ <b>What I can do</b>\n\n"
    "🔎 /search - find current IT vacancies\n"
    "🔔 /subscribe - get notified about new vacancies\n"
    "🔕 /unsubscribe - stop notifications\n"
    "ℹ️ /help - show this message\n"
    "🏠 /start - back to the main menu\n\n"
    "🟢 marks vacancies with a junior-level title."
)


def main_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔎 Search jobs", callback_data="search"),
                InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe"),
            ],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
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


def format_jobs(jobs, heading=None):
    if not jobs:
        return (
            "🔎 <b>Job search</b>\n\n"
            "No matching vacancies right now. Please check back later."
        )
    if heading is None:
        heading = f"🔎 <b>Found {len(jobs)} vacancies</b>"
    lines = [heading + "\n"]
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


def subscribe_chat(chat_id):
    subscribers = set(load_json("subscribers.json", []))
    if chat_id in subscribers:
        return "🔔 You are already subscribed to new vacancy alerts."
    subscribers.add(chat_id)
    save_json("subscribers.json", sorted(subscribers))
    return (
        "🔔 <b>Subscribed!</b>\n\n"
        "I'll message you when new matching vacancies appear."
    )


def unsubscribe_chat(chat_id):
    subscribers = set(load_json("subscribers.json", []))
    if chat_id not in subscribers:
        return "🔕 You are not subscribed."
    subscribers.discard(chat_id)
    save_json("subscribers.json", sorted(subscribers))
    return "🔕 Unsubscribed. You will no longer get alerts."


async def check_new_jobs(context: ContextTypes.DEFAULT_TYPE):
    try:
        jobs = await get_relevant_jobs()
    except Exception:
        return

    seen = load_json("seen_jobs.json", None)
    if seen is None:
        if jobs:
            save_json("seen_jobs.json", [job["url"] for job in jobs])
        return

    seen_set = set(seen)
    new_jobs = [job for job in jobs if job["url"] not in seen_set]
    if not new_jobs:
        return

    save_json("seen_jobs.json", sorted(seen_set | {job["url"] for job in jobs}))
    text = format_jobs(new_jobs, heading=f"🆕 <b>{len(new_jobs)} new vacancies</b>")
    for chat_id in load_json("subscribers.json", []):
        try:
            await context.bot.send_message(
                chat_id,
                text,
                parse_mode=ParseMode.HTML,
                link_preview_options=NO_PREVIEW,
            )
        except Exception:
            pass


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


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = subscribe_chat(update.effective_chat.id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = unsubscribe_chat(update.effective_chat.id)
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


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

    if query.data == "subscribe":
        text, markup = subscribe_chat(update.effective_chat.id), back_menu()
    elif query.data == "help":
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
            BotCommand("subscribe", "Get alerts about new jobs"),
            BotCommand("unsubscribe", "Stop alerts"),
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
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CallbackQueryHandler(button))
app.job_queue.run_repeating(
    check_new_jobs, interval=CHECK_INTERVAL_SECONDS, first=30
)
print("Bot is running")
app.run_polling()