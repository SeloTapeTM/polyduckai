# polyduckai

A Telegram bot called **Poly** that gives free access to multiple AI models via [duck.ai](https://duck.ai).

## How it works

1. Fetches a session token from `duck.ai` (`/duckchat/v1/status`)
2. Forwards your messages to `/duckchat/v1/chat` as a streamed request
3. Returns the response through the Telegram bot

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your Telegram bot token
python main.py
```

Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram.

## Bot commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/new` | Reset conversation history |
| `/model` | Switch AI model |
| `/help` | Show help |

## Available models

- GPT-4o Mini
- Claude 3 Haiku
- Llama 3.1 70B
- Mistral Small
- o3-mini
