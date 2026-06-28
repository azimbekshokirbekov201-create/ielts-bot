# Akbar's IELTS Bot 🎓

Telegram bot for IELTS preparation with AI-powered writing feedback.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env file
```bash
cp .env.example .env
```

Edit `.env` file:
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

### 3. Get Bot Token
- Open Telegram → @BotFather
- Send `/newbot`
- Follow instructions
- Copy the token

### 4. Get OpenAI API Key
- Go to platform.openai.com
- API Keys → Create new key
- Copy and paste in .env

### 5. Update admin links
In `handlers/progress.py`, update:
- `https://t.me/your_admin_username` → your Telegram username
- `https://t.me/your_channel` → your channel link

### 6. Run the bot
```bash
python bot.py
```

## Features
- ✍️ AI-powered IELTS Writing Task 2 checker
- 🎯 Daily grammar & vocabulary quiz
- 📚 IELTS tips (Writing, Speaking, Listening, Reading)
- 🏃 Marathon system
- 📊 Progress tracking
- 💎 Premium/Free tier system

## Project Structure
```
ielts_bot/
├── bot.py              # Main bot file
├── config.py           # Configuration
├── database.py         # SQLite database
├── handlers/
│   ├── start.py        # Start & main menu
│   ├── writing.py      # Writing checker
│   ├── quiz.py         # Daily quiz
│   └── progress.py     # Stats & premium
├── ai/
│   └── checker.py      # OpenAI integration
└── requirements.txt
```
