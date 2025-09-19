# HyppoBot

A multilingual Telegram bot that provides information about housing and university topics in Salerno, powered by Groq AI.

## Features

- **Multilingual Support**: English and Spanish
- **Topic-based Information**: Housing and University information for Salerno
- **AI-powered Responses**: Uses Groq AI for intelligent responses
- **Interactive Interface**: Inline keyboards for easy navigation

## Project Structure

```
HyppoBot/
├── run_bot.py              # Main entry point
├── bot/                    # Bot modules
│   ├── __init__.py
│   ├── utils.py           # Constants and utilities
│   ├── commands.py        # Command handlers (/start, /help)
│   ├── callbacks.py       # Callback query handlers
│   └── message_handlers.py # Text message handlers
├── llm/                   # AI model integration
│   └── Groq_client.py     # Groq AI client
└── .env                   # Environment variables
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HyppoBot
   ```

2. **Install dependencies**
   ```bash
   pip install python-telegram-bot python-dotenv groq
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the bot**
   ```bash
   python run_bot.py
   ```

## Usage

1. Start a conversation with the bot using `/start`
2. Select your preferred language (English/Spanish)
3. Choose a topic (Housing/University)
4. Ask questions and receive AI-powered responses

## Commands

- `/start` - Initialize the bot and select language
- `/help` - Show help information

## Environment Variables

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from @BotFather
- `GROQ_API_KEY` - Your Groq API key for AI responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request