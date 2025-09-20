# HyppoBot

A multilingual Telegram bot that provides information about housing and university topics in Salerno, powered by Groq AI and enhanced with RAG (Retrieval-Augmented Generation) capabilities.

## Features

- **Multilingual Support**: English and Spanish
- **Topic-based Information**: Housing, University, ESN, Nightlife, and Restaurant information for Salerno
- **RAG-Enhanced Responses**: Uses Retrieval-Augmented Generation with Qdrant vector database for accurate, context-aware responses
- **AI-powered**: Powered by Groq AI for intelligent natural language processing
- **Interactive Interface**: Inline keyboards for easy navigation
- **Vector Search**: Fast semantic search through curated knowledge base

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
├── rag/                   # RAG (Retrieval-Augmented Generation) system
│   ├── __init__.py
│   ├── embeddings.py      # Text embedding functionality
│   ├── pipeline.py        # RAG pipeline orchestration
│   ├── qdrant_client.py   # Vector database client
│   ├── retrieval.py       # Document retrieval logic
│   └── utils.py           # RAG utilities
├── data/                  # Knowledge base files
│   ├── esn.txt           # ESN Salerno information
│   ├── esn_staff.txt     # ESN staff information
│   ├── housing.txt       # Housing information
│   ├── nightlife.txt     # Nightlife information
│   ├── restaurants.txt   # Restaurant information
│   └── university.txt    # University information
├── requirements.txt       # Python dependencies
└── .env                  # Environment variables
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HyppoBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GROQ_API_KEY=your_groq_api_key_here
   QDRANT_URL=your_qdrant_instance_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

4. **Run the bot**
   ```bash
   python run_bot.py
   ```

## Usage

1. Start a conversation with the bot using `/start`
2. Select your preferred language (English/Spanish)
3. Ask any question about Salerno - the RAG system will automatically find relevant information from the knowledge base
4. Receive AI-powered responses enhanced with contextual information

## Commands

- `/start` - Initialize the bot and select language
- `/help` - Show help information

## Environment Variables

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from @BotFather
- `GROQ_API_KEY` - Your Groq API key for AI responses
- `QDRANT_URL` - URL of your Qdrant vector database instance
- `QDRANT_API_KEY` - API key for your Qdrant instance

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request