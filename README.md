# Telegram Recap Bot (Weekly & On-Demand)

A small Python script that pulls recent messages from a Telegram chat and sends an AI-generated recap either:
- automatically once a week (via cron), or
- on-demand when you run the script manually.

## Features

- Fetches recent messages from a specific Telegram chat using the Telegram Bot API.
- Summarizes them with a Gemini model.
- Supports two modes:
  - `weekly`: intended for an automated weekly recap (e.g., via cron).
  - default (no argument): on-demand recap when you run the script manually.
- Sends the recap back to the same Telegram chat.

## Setup

1. Clone the repo:

   ```bash
   git clone git@github.com:<your-username>/<repo-name>.git
   cd <repo-name>
   ```

2.	Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3.	Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4.	Create a  .env  file:

   ```bash
   TELEGRAM_BOT_TOKEN=your_bot_token
   CLIENT_CHAT_ID=your_chat_id
   MODEL_API_KEY=your_gemini_api_key
   MODEL_NAME=gemini-2.5-flash-lite
   MODEL_API_BASE=https://generativelanguage.googleapis.com/v1beta
   ```

Usage
On-demand recap:

   ```bash
   python test_recap.py
   ```

Weekly-style recap:

   ```bash
   python test_recap.py weekly
   ```

Cron example (weekly)
On macOS/Linux, you can add a cron entry like:

   ```bash
    0 21 * * 0 cd "/Users/yourname/path/to/telegram recap bot" && "/Users/yourname/path/to/telegram recap   bot/venv/bin/python" test_recap.py weekly >> "/Users/yourname/path/to/telegram recap bot/cron.log" 2>&1
   ```

This runs the weekly recap every Sunday at 21:00. 
