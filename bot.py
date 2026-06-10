import discord
from discord.ext import commands, tasks
import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import aiohttp

# ── Bot Setup ──────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="?", intents=intents, help_command=None)

# ── Data ───────────────────────────────────────────────────────────────────────
CHEESE_FACTS = [
    "There are over 1,800 distinct varieties of cheese in the world! 🧀",
    "Cheddar is the world's most popular cheese, accounting for over 50% of all cheese sold in the UK.",
    "It takes about 10 pounds of milk to make just 1 pound of cheese.",
    "The holes in Swiss cheese are called 'eyes'. Cheese without holes is called 'blind cheese'.",
    "Mozzarella is the most consumed cheese in the United States, largely thanks to pizza.",
    "Pule, made from Balkan donkey milk, is the world's most expensive cheese at ~$600/lb.",
    "Ancient Romans used cheese as currency to pay their soldiers.",
    "Brie is nicknamed 'The Queen of Cheeses' and was a favorite of Charlemagne.",
    "Cheese contains tryptophan, the same compound in turkey that makes you sleepy.",
    "The oldest known cheese (3,200 years old!) was found in an Egyptian tomb.",
]

CHEESE_JOKES = [
    ("Why did the cheese go to therapy?", "Because it had too many holes in its life! 🕳️"),
    ("What did the cheese say when it looked in the mirror?", "Halloumi! 🪞"),
    ("Why don't cheese makers ever get lost?", "Because gouda always find their whey! 🧭"),
    ("What do you call cheese that isn't yours?", "Nacho cheese! 🧀"),
    ("Why is cheese so noisy?", "Because it's always making a racket-te (raclette)! 📢"),
    ("What did the cheese say to the crackers?", "I'm crackers about you! 🫙"),
    ("Why did the cheese factory burn down?", "Because the da gouda was too sharp! 🔥"),
    ("What's a cheese's favourite type of music?", "R'n'Brie! 🎵"),
]

TRIVIA_QUESTIONS = [
    {
        "q": "What country produces the most cheese in the world?",
        "a": "united states",
        "hint": "🇺🇸 Think big and western...",
        "fact": "The US produces over 6 million metric tons of cheese per year!",
    },
    {
        "q": "What type of milk is Roquefort cheese traditionally made from?",
        "a": "sheep",
        "hint": "🐑 Not cow, not goat...",
        "fact": "Roquefort is one of the world's oldest cheeses, aged in the caves of Combalou.",
    },
    {
        "q": "In what country did Gouda cheese originate?",
        "a": "netherlands",
        "hint": "🌷 Famous for windmills and tulips...",
        "fact": "Gouda has been traded at the Gouda market since the 14th century!",
    },
    {
        "q": "What gives blue cheese its distinctive colour?",
        "a": "mold",
        "hint": "🔵 It's a living organism...",
        "fact": "Penicillium roqueforti is the mould used — related to the antibiotic penicillin!",
    },
    {
        "q": "How many litres of milk does it take to make 1kg of hard cheese (approx)?",
        "a": "10",
        "hint": "🥛 It's a double-digit number...",
        "fact": "The exact amount varies by cheese type, but hard cheeses need the most milk.",
    },
]

active_trivia: dict[int, dict] = {}

EIGHTBALL_RESPONSES = [
    ("🟢", "It is certain."),
    ("🟢", "It is decidedly so."),
    ("🟢", "Without a doubt."),
    ("🟢", "Yes, definitely."),
    ("🟢", "You may rely on it."),
    ("🟢", "As I see it, yes."),
    ("🟢", "Most likely."),
    ("🟢", "Outlook good."),
    ("🟢", "Yes."),
    ("🟢", "Signs point to yes."),
    ("🟡", "Reply hazy, try again."),
    ("🟡", "Ask again later."),
    ("🟡", "Better not tell you now."),
    ("🟡", "Cannot predict now."),
    ("🟡", "Concentrate and ask again."),
    ("🔴", "Don't count on it."),
    ("🔴", "My reply is no."),
    ("🔴", "My sources say no."),
    ("🔴", "Outlook not so good."),
    ("🔴", "Very doubtful."),
]

GAY_MESSAGES = [
    (range(0, 11), "Straighter than a ruler. Certified heterosexual."),
    (range(11, 26), "Curious? Maybe just cheese-curious."),
    (range(26, 41), "A little fruity... like watermelon on a hot day."),
    (range(41, 56), "Right in the middle — a true enigma."),
    (range(56, 71), "Leaning into it. The rainbow is calling."),
    (range(71, 86), "Absolutely fabulous, twink in training."),
    (range(86, 100), "Off the charts! You ARE the rainbow."),
    (range(100, 101), "100%! Certified gay icon. Pack it up, Elton John."),
]

# ── Monkey & Offensive Data ───────────────────────────────────────────────────
MONKEY_ABILITIES = [ ... ]  # (kept as is, not pasting all for brevity)

# ... (All other lists like MONKEY_RANKS, LOOP_FAILS etc. stay the same) ...

# ── ESEX GIFs (Fresh Spicy Lingerie / Twerk / Thicc) ─────────────────────────
ESEX_GIFS = [
    "https://media.giphy.com/media/3o7TKsQ8v0dG6b0z1C/giphy.gif",
    "https://media.giphy.com/media/l2JJyK0Z7X5c7r7fG/giphy.gif",
    "https://media.giphy.com/media/26ufajqx7QJx4VIMo/giphy.gif",
    "https://media.giphy.com/media/5GoVLqeAOo6PK/giphy.gif",
    "https://media.giphy.com/media/l0HlRnAWXxn0MhKLK/giphy.gif",
    "https://media.giphy.com/media/26tOZ42mg6s3T1J7W/giphy.gif",
    "https://media.giphy.com/media/3oEjI5VtIhHvK37WYo/giphy.gif",
    "https://media.giphy.com/media/xT9IgG9v2p2s2jVq4w/giphy.gif",
    "https://media.giphy.com/media/l0MYt9z4pB0z1gJqM/giphy.gif",
    "https://media.giphy.com/media/26BRv0Th6v9g6f1qM/giphy.gif",
    "https://media.giphy.com/media/3o6Zt6KHx9z5z5z5z5/giphy.gif",
    "https://media.giphy.com/media/l41lI3Z8V4z5z5z5/giphy.gif",
    "https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
    "https://media.giphy.com/media/26xBwdIuRJiAIy1l6/giphy.gif",
    "https://media.giphy.com/media/l2JehQ2GitHGdVG9W/giphy.gif",
    "https://media.giphy.com/media/3oEjHA7z5v5z5z5z5/giphy.gif",
    "https://media.giphy.com/media/l0IylOPCNk9n0MhKL/giphy.gif",
    "https://media.giphy.com/media/26BRv0Th6v9g6f1qM/giphy.gif",
    "https://media.giphy.com/media/3o7TKsQ8v0dG6b0z1C/giphy.gif",
    "https://media.giphy.com/media/26tOZ42mg6s3T1J7W/giphy.gif",
]

def get_random_esex():
    if not ESEX_GIFS:
        return None
    return random.choice(ESEX_GIFS)

# ── Events & Commands (rest of the file) ──────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Cheesehub is online as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="?help | Serving cheese 🧀"))
    keep_alive.start()

# (keep_alive task stays the same)

# Help command now includes ?esex
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🧀 Cheesehub — Command Menu",
        description="Your friendly neighbourhood cheese bot!",
        color=0xF5C542,
    )
    embed.add_field(name="🧀 Cheese", value= "...", inline=False)
    embed.add_field(
        name="🎮 Fun",
        value=(
            "`?8ball <question>` — Ask the magic 8-ball\n"
            "`?gay [@user]` — Check someone's gay %\n"
            "`?dick [@user]` — Dick meter\n"
            "`?roast [@user]` — Roast someone\n"
            "`?monkey [@user]` — Monkey rating\n"
            "`?loop [@user]` — DBD loop outcome\n"
            "`?skillcheck [@user]` — DBD skill check\n"
            "`?locker [@user]` — DBD locker event\n"
            "`?braincell [@user]` — Brain cell count\n"
            "`?socialcredit [@user]` — Social credit\n"
            "`?lootbox` — Open a lootbox\n"
            "`?esex [@user]` — Random sexy girl GIF 🔥"
        ),
        inline=False,
    )
    # ... rest of help stays the same
    await ctx.send(embed=embed)

# ... (all other commands stay the same) ...

@bot.command(name="esex")
@commands.cooldown(1, 8, commands.BucketType.user)
async def esex(ctx, member: discord.Member = None):
    target = member or ctx.author
    gif = get_random_esex()
    if not gif:
        await ctx.send("No GIFs loaded yet!")
        return
    await ctx.send(f"🍑 **ESEX ACTIVATED** 🍑\n{target.mention} here's something nice for you~ 🔥")
    await ctx.send(gif)

# (The rest of the file with on_message, triggers, etc. remains unchanged)

# ── Keep-alive & Run ─────────────────────────────────────────────────────────
# (keep the rest exactly as it was)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set!")
    bot.run(token)
