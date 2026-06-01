# polyduckai

A Telegram bot called **Poly** that gives free access to multiple AI models via [OpenRouter](https://openrouter.ai).

## How it works

1. Each Telegram user gets an isolated conversation session
2. Messages are forwarded to OpenRouter's OpenAI-compatible chat API
3. The response is returned through the Telegram bot

OpenRouter exposes a generous selection of **free** models behind a single API
key — no per-token cost on the `:free` tier, just rate limits.

## Available models

All free on OpenRouter:

- Gemini 2.0 Flash
- DeepSeek V3
- Llama 3.3 70B
- Qwen 2.5 72B
- Mistral Small

> Model IDs occasionally change. The current free catalogue is at
> [openrouter.ai/models?max_price=0](https://openrouter.ai/models?max_price=0) —
> update `polyduckai/ai_client.py` if one is retired.

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
# fill in TELEGRAM_BOT_TOKEN and OPENROUTER_API_KEY in .env
python main.py
```

You need two things:

- A bot token from [@BotFather](https://t.me/BotFather) on Telegram
- A free API key from [openrouter.ai/keys](https://openrouter.ai/keys)
  (sign in with Google/GitHub, click **Create Key**)

---

## Deploy on Railway (recommended)

[Railway](https://railway.app) is the easiest way to host this for free.

### 1. Get your credentials

- **Telegram bot token:** message [@BotFather](https://t.me/BotFather), send
  `/newbot`, follow the prompts, copy the token (looks like `7123456789:AAF...`)
- **OpenRouter API key:** go to [openrouter.ai/keys](https://openrouter.ai/keys),
  sign in, click **Create Key**, copy it (looks like `sk-or-v1-...`)

### 2. Deploy to Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project → Deploy from GitHub repo**
3. Select `SeloTapeTM/polyduckai`
4. Railway will detect the `Procfile` automatically — no extra config needed

### 3. Add your environment variables

1. In your Railway project, go to **Variables**
2. Add two variables:
   - `TELEGRAM_BOT_TOKEN` → your token from BotFather
   - `OPENROUTER_API_KEY` → your key from OpenRouter
3. Railway will redeploy automatically

### 4. Verify

Go to **Deployments → View Logs**. You should see:
```
INFO  Application - Started polling
```

Your bot is now live 24/7. No credit card required for the free tier.

---

## Notes

- The OpenRouter free tier has no token cost — only per-minute/per-day rate limits
- Each Telegram user gets their own isolated conversation session
- Conversation history resets with `/new` or when switching models
