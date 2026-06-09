# 🧀 Cheesehub — Discord Bot

A fun Discord bot packed with cheese facts, jokes, and trivia!

---

## Commands

| Command   | Description                              |
|-----------|------------------------------------------|
| `!cheese` | Get a random cheese fact                 |
| `!joke`   | Get a cheesy joke (spoiler punchline)    |
| `!trivia` | Start a cheese trivia question           |
| `!hint`   | Get a hint for the active trivia         |
| `!skip`   | Skip the current trivia question         |
| `!ping`   | Check bot latency                        |
| `!help`   | Show the command menu                    |

---

## Setup

### 1. Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click **New Application** → name it `Cheesehub`
3. Go to **Bot** → click **Add Bot**
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Click **Reset Token** and copy your token

### 2. Invite the Bot to Your Server

1. Go to **OAuth2 → URL Generator**
2. Select scopes: `bot`
3. Select permissions: `Send Messages`, `Read Message History`, `Embed Links`
4. Open the generated URL and invite Cheesehub to your server

### 3. Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Set your bot token (Mac/Linux)
export DISCORD_TOKEN=your_token_here

# Set your bot token (Windows)
set DISCORD_TOKEN=your_token_here

# Run the bot
python bot.py
```

You should see:
```
✅ Cheesehub is online as Cheesehub#1234 (ID: ...)
```

---

## Adding More Content

- **Facts** — Add strings to the `CHEESE_FACTS` list in `bot.py`
- **Jokes** — Add `("setup", "punchline")` tuples to `CHEESE_JOKES`
- **Trivia** — Add question dicts to `TRIVIA_QUESTIONS` with keys: `q`, `a`, `hint`, `fact`
