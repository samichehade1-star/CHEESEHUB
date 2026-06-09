import discord
from discord.ext import commands
import random
import os

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

# Track active trivia sessions per channel
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
    (range(0, 11),   "Straighter than a ruler."),
    (range(11, 26),  "Curious? Maybe just cheese-curious."),
    (range(26, 41),  "A little fruity, nothing wrong with that."),
    (range(41, 56),  "Right in the middle — a true enigma."),
    (range(56, 71),  "Leaning into it. The rainbow is calling."),
    (range(71, 86),  "Absolutely fabulous."),
    (range(86, 100), "Off the charts! You ARE the rainbow."),
    (range(100, 101),"100%! Certified gay icon."),
]

# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Cheesehub is online as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help | Serving cheese 🧀"))


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
        value=(
            "`?cheese` — Random cheese fact\n"
            "`?joke` — Cheesy joke\n"
            "`?trivia` — Start a cheese trivia question\n"
            "`?hint` — Get a hint for the active trivia\n"
            "`?skip` — Skip the current trivia question"
        ),
        inline=False,
    )
    embed.add_field(
        name="🎮 Fun",
        value=(
            "`!8ball <question>` — Ask the magic 8-ball\n"
            "`!gay [@user]` — Check someone's gay % (RNG)\n"
            "`!dick [@user]` — You know what this does 📏\n"
            "`!roast [@user]` — Roast someone 🔥"
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


@bot.command(name="cheese")
async def cheese_fact(ctx):
    fact = random.choice(CHEESE_FACTS)
    embed = discord.Embed(
        title="🧀 Cheese Fact!",
        description=fact,
        color=0xF5C542,
    )
    embed.set_footer(text="Use !cheese for another fact")
    await ctx.send(embed=embed)


@bot.command(name="joke")
async def cheese_joke(ctx):
    setup, punchline = random.choice(CHEESE_JOKES)
    embed = discord.Embed(title="😄 Cheesy Joke", color=0xF5C542)
    embed.add_field(name="❓", value=setup, inline=False)
    embed.add_field(name="💬", value=f"||{punchline}||", inline=False)
    embed.set_footer(text="(Click the spoiler to reveal the punchline!)")
    await ctx.send(embed=embed)


@bot.command(name="trivia")
async def trivia(ctx):
    if ctx.channel.id in active_trivia:
        q = active_trivia[ctx.channel.id]["q"]
        await ctx.send(f"⚠️ A trivia is already active! **{q}**\nUse `?hint` or `?skip`.")
        return

    question = random.choice(TRIVIA_QUESTIONS)
    active_trivia[ctx.channel.id] = question

    embed = discord.Embed(
        title="🧀 Cheese Trivia!",
        description=question["q"],
        color=0xF5A600,
    )
    embed.set_footer(text="Type your answer! | !hint for a clue | !skip to skip")
    await ctx.send(embed=embed)


@bot.command(name="hint")
async def hint(ctx):
    if ctx.channel.id not in active_trivia:
        await ctx.send("❌ No active trivia! Start one with `?trivia`.")
        return
    hint_text = active_trivia[ctx.channel.id]["hint"]
    await ctx.send(f"💡 **Hint:** {hint_text}")


@bot.command(name="skip")
async def skip(ctx):
    if ctx.channel.id not in active_trivia:
        await ctx.send("❌ No active trivia to skip!")
        return
    answer = active_trivia.pop(ctx.channel.id)["a"]
    await ctx.send(f"⏭️ Skipped! The answer was **{answer.title()}**.")


@bot.command(name="8ball")
async def eightball(ctx, *, question: str = None):
    if not question:
        await ctx.send("❓ Ask me a question! e.g. `?8ball Will I ever be rich?`")
        return
    emoji, response = random.choice(EIGHTBALL_RESPONSES)
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x2B2D31)
    embed.add_field(name="❓ Question", value=question, inline=False)
    embed.add_field(name=f"{emoji} Answer", value=response, inline=False)
    embed.set_footer(text=f"Asked by {ctx.author.display_name}")
    await ctx.send(embed=embed)


@bot.command(name="gay")
async def gay(ctx, member: discord.Member = None):
    target = member or ctx.author
    value = random.randint(0, 100)
    message = next(msg for r, msg in GAY_MESSAGES if value in r)
    embed = discord.Embed(
        title="Gay Meter",
        description=f"**{target.display_name}** has been analyzed...",
        color=0xFF69B4,
    )
    embed.add_field(name="Result", value=f"**{value}%**", inline=False)
    embed.add_field(name="Verdict", value=message, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


# ── Scaffold Commands (fill in your own responses!) ───────────────────────────

@bot.command(name="dick")
async def dick(ctx, member: discord.Member = None):
    target = member or ctx.author
    value = random.randint(0, 8)

    # Fill in your own messages for each range below!
    if value == 0:
        message = "Congrats on your sex change operation. It was a success Nigga"
    elif value <= 2:
        message = "Holy smokes its Kim Jong Un"
    elif value <= 4:
        message = "My pinky finger can wrap around it"
    elif value <= 6:
        message = "Show off..."
    elif value <= 7:
        message = "Watermellon person"
    else:
        message = "Tell me you like KFC without telling me you like KFC"

    if value == 0:
        bar = "()"
    else:
        bar = "8" + "=" * value + "D"

    embed = discord.Embed(title="📏 Dick Meter", color=0x5865F2)
    embed.add_field(name=target.display_name, value=f"`{bar}` **{value} inches**", inline=False)
    embed.add_field(name="Verdict", value=message, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    target = member or ctx.author

    # Add your roast lines to this list!
    roasts = [
        "You look like you use Furry or Milkygay",
        "I’m sorry your mom never put your artwork on the wall as a kid.",
        "Your logic would lose to a Magic 8 Ball.",
        "You built like a windshield wiper.",
        "You remind me of Sora",
    ]

    embed = discord.Embed(
        title="🔥 Roasted!",
        description=f"{target.mention} {random.choice(roasts)}",
        color=0xE74C3C,
    )
    embed.set_footer(text=f"Roasted by {ctx.author.display_name}")
    await ctx.send(embed=embed)


# ── Word Trigger (fill in your own response!) ─────────────────────────────────
# To add a trigger: put the word in TRIGGER_WORD and your reply in TRIGGER_RESPONSE
TRIGGER_WORD = "Nigga"
TRIGGER_RESPONSE = "Who you calling a Nigga. I'll show you a real Nigga"


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Word trigger — fires when someone's message contains TRIGGER_WORD
    if TRIGGER_WORD.lower() in message.content.lower():
        await message.channel.send(TRIGGER_RESPONSE)

    # Check trivia answers
    if message.channel.id in active_trivia:
        question = active_trivia[message.channel.id]
        if message.content.strip().lower() == question["a"].lower():
            fact = question["fact"]
            del active_trivia[message.channel.id]
            embed = discord.Embed(
                title="✅ Correct!",
                description=f"Well done, {message.author.mention}! 🎉",
                color=0x57F287,
            )
            embed.add_field(name="📖 Fun fact", value=fact, inline=False)
            await message.channel.send(embed=embed)
            return  # Don't process commands after a correct answer

    await bot.process_commands(message)


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set!")
    bot.run(token)
