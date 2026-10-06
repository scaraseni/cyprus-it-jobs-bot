# Cyprus IT Jobs Helper

   ![Tests](https://github.com/scaraseni/cyprus-it-jobs-bot/actions/workflows/tests.yml/badge.svg)
A Telegram bot that helps junior developers and QA engineers track fresh IT vacancies in Cyprus.

> **Status:** work in progress. The bot currently runs locally; a hosted version is planned.

## Features

   - `/subscribe` alerts about new vacancies (checked every 3 hours while the bot is running)
- Search for current IT vacancies with the `/search` command or the **Search jobs** button
- Filters by IT/QA job titles and Cyprus locations, and hides senior-level roles
- Marks vacancies with a junior-level title with 🟢
- Clean inline-button interface: screens update in place instead of flooding the chat

## How it works

The bot reads the **public job board endpoints** of the Lever and Ashby platforms (no scraping of job sites). Companies covered at the moment: XM, Welltech, HyperHug.

Filtering is done by job title and location, so always open the vacancy and read the actual requirements.

## Tech stack

- Python 3
- [python-telegram-bot](https://python-telegram-bot.org/)
- httpx (async HTTP requests)
- python-dotenv

## Run locally

pip install -r requirements-dev.txt
pytest
1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Clone the repository and create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the project folder:

```
BOT_TOKEN=your_token_here
```

4. Start the bot:

```bash
python bot.py
```

To check the job fetching without Telegram, run `python jobs.py`.

## Project structure

- `bot.py` - Telegram bot: commands, buttons, message formatting
- `jobs.py` - fetching and filtering vacancies
- `requirements.txt` - dependencies

## Roadmap

   - [x] Notifications about new vacancies (runs while the bot is online)
   - [ ] Hosting so the bot runs 24/7
   - [x] Automated tests (Pytest) and CI with GitHub Actions
   - [ ] More companies and sources
- [ ] Notifications about new vacancies only
- [ ] Hosting so the bot runs 24/7
- [ ] Automated tests (Pytest) and CI with GitHub Actions
- [ ] More companies and sources