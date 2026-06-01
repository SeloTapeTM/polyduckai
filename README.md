# polyduckai

A Telegram bot called **Poly** that gives free access to multiple AI models via [duck.ai](https://duck.ai).

## How it works

1. Fetches a session token from `duck.ai` (`/duckchat/v1/status`)
2. Forwards your messages to `/duckchat/v1/chat` as a streamed request
3. Returns the response through the Telegram bot

## Available models

- GPT-4o Mini
- Claude 3 Haiku
- Llama 3.1 70B
- Mistral Small
- o3-mini

## Bot commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/new` | Reset conversation history |
| `/model` | Switch AI model |
| `/help` | Show help |

---

## Local setup

```bash
git clone https://github.com/SeloTapeTM/polyduckai.git
cd polyduckai
pip install -r requirements.txt
cp .env.example .env
# fill in your token in .env
python main.py
```

Get a bot token from [@BotFather](https://t.me/BotFather) on Telegram.

---

## Deploy on Railway (recommended)

[Railway](https://railway.app) is the easiest way to host this for free.

### 1. Get a Telegram bot token

1. Open Telegram → message [@BotFather](https://t.me/BotFather)
2. Send `/newbot`, follow the prompts
3. Copy the token it gives you (looks like `7123456789:AAF...`)

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project → Deploy from GitHub repo**
3. Select `SeloTapeTM/polyduckai`
4. Railway will detect the `Procfile` automatically — no extra config needed

### 3. Add your bot token

1. In your Railway project, go to **Variables**
2. Add a new variable:
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: your token from BotFather
3. Railway will redeploy automatically

### 4. Verify

Go to **Deployments → View Logs**. You should see:
```
INFO  Application - Started polling
```

Your bot is now live 24/7. No credit card required for the free tier.

---

## Notes

- No API keys needed — duck.ai is free and anonymous
- Each Telegram user gets their own isolated conversation session
- Conversation history resets with `/new` or when switching models
