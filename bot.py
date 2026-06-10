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
    ("🟢", "It is certain."), ("🟢", "It is decidedly so."), ("🟢", "Without a doubt."),
    ("🟢", "Yes, definitely."), ("🟢", "You may rely on it."), ("🟢", "As I see it, yes."),
    ("🟢", "Most likely."), ("🟢", "Outlook good."), ("🟢", "Yes."), ("🟢", "Signs point to yes."),
    ("🟡", "Reply hazy, try again."), ("🟡", "Ask again later."), ("🟡", "Better not tell you now."),
    ("🟡", "Cannot predict now."), ("🟡", "Concentrate and ask again."),
    ("🔴", "Don't count on it."), ("🔴", "My reply is no."), ("🔴", "My sources say no."),
    ("🔴", "Outlook not so good."), ("🔴", "Very doubtful."),
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
MONKEY_ABILITIES = [
    "Throws bananas with deadly accuracy.",
    "Can smell fried chicken and bananas from 3 miles away.",
    "Climbs walls when the rent is due.",
    "Communicates only in loud monkey noises and 'ayyo my nigga'.",
    "Proeffecient in Air Force Ones theft.",
    "Permanent welfare benefits.",
    "Can instantly identify ripe bananas and government cheese.",
    "Escapes responsibilities by swinging away on Section 8.",
    "Immune to police questioning.",
    "Invented purple drank.",
    "Can pick any lock in under 2 seconds, especially if it's a corner store.",
    "Has a PhD in monkey business and street pharmacy.",
    "Can hear a banana peel drop from across the map... or the sound of cops.",
    "Runs at 110% movement speed when the lights turn off.",
    "Can summon emergency KFC.",
    "Has been banned from 12 zoos and 3 Walmarts.",
    "Can swing from invisible vines and stolen gold chains.",
    "Knows where all the bananas are hidden... and where the lean is.",
    "Has 6 babby mommas but dodges all child support.",
    "Best-friends with Diddy",
]

MONKEY_RANKS = [
    "Mini Nigga", "Banana Enthusiast", "Lvl 3 Monkey", "Jungle Warrior",
    "Kool-Aid Drinker", "Manager at KFC", "Low Battery Smoke Alarm",
    "Gigga Nigga", "Bannana Muncher", "Welfare King", "Section 8 Swinger",
    "40oz Apostle", "Gorilla",
]

MONKEY_STATUS = [
    "Threat Level: Low (just stealing bikes)",
    "Threat Level: Moderate (looting the corner store)",
    "Threat Level: High (swinging through the suburbs)",
    "Threat Level: Critical (full moon monkey mode)",
    "Threat Level: One of those niggas that smells like shit",
    "Threat Level: Government Watch List",
    "Threat Level: Works in the corn feilds",
    "Threat Level: African Drug Lord",
    "Threat Level: Police Called (again)",
    "Threat Level: Listens to cheif keif while brushing his teeth",
    "Threat Level: Uses the hard R",
]

# (LOOP_FAILS, LOOP_WINS, LOOP_REWARDS, SKILL_CHECKS, LOCKER_EVENTS, BRAIN_RESULTS, SOCIAL_EVENTS, LOOT_ITEMS remain unchanged - they are in your original file)

# ── ESEX GIFs (Sexy Girls, E-girls, Lingerie, Twerk, Ahegao) ─────────────────
ESEX_GIFS = [
    "https://media.tenor.com/26027474/ahegao-delfine-bell.gif",
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
    "https://media.giphy.com/media/l41lI3Z8V4z5z5z5/giphy.gif",
    "https://media.giphy.com/media/26ufnwz3wDUli7GU0/giphy.gif",
    "https://media.giphy.com/media/26xBwdIuRJiAIy1l6/giphy.gif",
    "https://media.giphy.com/media/l2JehQ2GitHGdVG9W/giphy.gif",
    "https://media.giphy.com/media/3oEjHA7z5v5z5z5z5/giphy.gif",
    "https://media.giphy.com/media/l0IylOPCNk9n0MhKL/giphy.gif",
    "https://media.giphy.com/media/26BRv0Th6v9g6f1qM/giphy.gif",
    "https://media.giphy.com/media/3o7aDgf2z8z5z5z5z5/giphy.gif",
    "https://media.tenor.com/9f5f5f5f5f5f5f5f/tenor.gif",
    "https://media.giphy.com/media/26ufajqx7QJx4VIMo/giphy.gif",
]

def get_random_esex():
    if not ESEX_GIFS:
        return None
    return random.choice(ESEX_GIFS)

# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Cheesehub is online as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="?help | Serving cheese 🧀"))
    keep_alive.start()

@tasks.loop(minutes=5)
async def keep_alive():
    try:
        async with aiohttp.ClientSession() as session:
            await session.get("https://cheesehub.onrender.com")
    except Exception:
        pass

# ── Commands ───────────────────────────────────────────────────────────────────
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🧀 Cheesehub — Command Menu",
        description="Your friendly neighbourhood cheese bot!",
        color=0xF5C542,
    )
    embed.add_field(
        name="🧀 Cheese",
        value="`?cheese` — Random cheese fact\n`?joke` — Cheesy joke\n`?trivia` — Start a cheese trivia question\n`?hint` — Get a hint\n`?skip` — Skip",
        inline=False,
    )
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
            "`?esex [@user]` — Random sexy e-girl GIF 🔥"
        ),
        inline=False,
    )
    embed.add_field(
        name="ℹ️ Info",
        value="`?help` — Show this menu\n`?ping` — Check bot latency",
        inline=False,
    )
    embed.set_footer(text="Made with 🧀 | Cheesehub v1.0")
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

# ... (All other commands like cheese, joke, trivia, 8ball, gay, dick, roast, monkey, loop, skillcheck, locker, braincell, socialcredit, lootbox are unchanged from your original)

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

# ── Word Triggers ─────────────────────────────────────────────────────────────
TRIGGER_WORDS_1 = ["nigga", "nigger"]
TRIGGER_RESPONSE = "Who you calling a Nigga. I'll show you a real Nigga"

TRIGGER_WORDS_2 = ["cheats", "hacks", "cheat", "hack", "explot", "cheater", "hacker", "hackers", "cheaters"]
TRIGGER_RESPONSE_2 = "Its just a game why are you so pressed monkey. Its just reshade powered by the great Visneya.xyz & Nyxia.cc\n\nPS: You Jubtas?"
TRIGGER_RESPONSE_2A = "Its just cheese\n\nPS: You Jubtas?"

TRIGGER_WORDS_3 = ["prophet", "trollingprophet", "godessKay", "godess kay", "kib", "kids in basement", "godess", "kay", "gorlock", "megathron"]
TRIGGER_RESPONSE_3 = "Fake Christian, Schizophrenia Alert 🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨"

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if any(word in message.content.lower() for word in TRIGGER_WORDS_1):
        await message.channel.send(f"{message.author.mention} {TRIGGER_RESPONSE}")

    if any(word in message.content.lower() for word in TRIGGER_WORDS_2):
        await message.channel.send(f"{message.author.mention} {random.choice([TRIGGER_RESPONSE_2, TRIGGER_RESPONSE_2A])}")

    if any(word in message.content.lower() for word in TRIGGER_WORDS_3):
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        embed = discord.Embed(description=f"{message.author.mention} {TRIGGER_RESPONSE_3}", color=0xFF0000)
        await message.channel.send(embed=embed)

    if message.channel.id in active_trivia:
        question = active_trivia[message.channel.id]
        if message.content.strip().lower() == question["a"].lower():
            fact = question["fact"]
            del active_trivia[message.channel.id]
            embed = discord.Embed(title="✅ Correct!", description=f"Well done, {message.author.mention}! 🎉", color=0x57F287)
            embed.add_field(name="📖 Fun fact", value=fact, inline=False)
            await message.channel.send(embed=embed)
            return

    await bot.process_commands(message)

# ── Keep-alive ────────────────────────────────────────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set!")
    bot.run(token)
