import discord
from discord.ext import commands
import random
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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

# ── DBD & Fun Data ─────────────────────────────────────────────────────────────
MONKEY_ABILITIES = [
    "Throws bananas with deadly accuracy.",
    "Can smell bananas from 3 miles away.",
    "Climbs walls during arguments.",
    "Communicates only through monkey noises.",
    "Stole the killer's flashlight.",
    "Has permanent Bloodlust III.",
    "Can instantly identify ripe bananas.",
    "Escapes responsibilities by swinging away.",
    "Immune to skill checks.",
    "Invented banana technology.",
    "Can open any locker in under 2 seconds.",
    "Has a PhD in monkey business.",
    "Can hear a banana peel from across the map.",
    "Runs at 110% movement speed.",
    "Can summon emergency bananas.",
    "Has been banned from 12 zoos.",
    "Can swing from invisible vines.",
    "Knows where all the bananas are hidden.",
    "Can dodge accountability with ease.",
    "Has mastered advanced ape combat.",
]

MONKEY_RANKS = [
    "Mini Nigga",
    "Banana Enthusiast",
    "Lvl 3 Monkey",
    "Jungle Warrior",
    "Kool Aid enthusiast",
    "KFC lover",
    "Low battery smoke alarm",
    "Gigga Nigga",
]

MONKEY_STATUS = [
    "Threat Level: Low",
    "Threat Level: Moderate",
    "Threat Level: High",
    "Threat Level: Critical",
    "Threat Level: Evacuate the Server",
    "Threat Level: Government Notified",
    "Threat Level: Banana Emergency",
    "Threat Level: Containment Failed",
]

LOOP_FAILS = [
    "Ran into a wall while looking behind.",
    "You are license banned",
    "Thought the pallet was still there.",
    "Downloaded Milkyway Malware",
    "Accidentally cornered themselves.",
    "Stopped to teabag and got hit.",
    "Forgot where the exit gate was.",
    "Tried to heal mid chase.",
    "Entered a locker instead of vaulting.",
    "Got stuck on a tree.",
    "Accidentally led the killer to the entire team.",
    "Used Fury and died",
    "Forgot they were injured.",
    "Ran straight into a dead zone.",
    "Mistook the killer for a teammate.",
]

LOOP_WINS = [
    "Looped the killer for 5 generators.",
    "Made the killer rage quit.",
    "ALT + F4",
    "Escaped with a perfectly timed Dead Hard.",
    "Made the killer lose track three times.",
    "Used Shack like a professional.",
    "Made the killer question their life choices.",
    "Looped so hard the killer became friendly.",
    "Successfully wasted the killer's entire match.",
    "Got accused of cheating.",
    "Got VAC Banned",
    "Looped until the killer disconnected.",
    "Created a YouTube montage mid chase.",
    "Turned the killer into a spectator.",
    "Unlocked Ultra Instinct.",
]

LOOP_REWARDS = [
    "Reward: Facecamped.",
    "Reward: Tunneled immediately.",
    "Reward: Received Femboy Pics from SYAZ",
    "Reward: Killer disconnected.",
    "Reward: 4 Slaves, poorly fed.",
    "Reward: Killer uninstalled.",
    "Reward: Tiddy Pics",
    "Reward: Earned bragging rights.",
    "NO MORE FREE KEYS. AND THATS THAT",
    "Reward: Chlamydia",
]

SKILL_CHECKS = [
    "Great Skill Check! +300 points.",
    "Nigga turn on auto skill check monkey.",
    "Missed the Skill Check.",
    "Exploded the generator.",
    "Accidentally alerted the killer.",
    "Missed because you're black",
    "Missed so badly the gen lost 20%.",
    "Skill Issue...",
    "Closed their eyes and somehow hit Great.",
    "Broke the laws of probability.",
]

LOCKER_EVENTS = [
    "Tried to Sabo the hook with Remote interaction and looked like an idiot",
    "Found Dwight already inside.",
    "Entered Narnia.",
    "Immediately got grabbed.",
    "Found a banana.",
    "Discovered a secret basement.",
    "Instant Escaped",
    "Came out gay",
    "Stayed in the locker for the entire game.",
    "Achieved maximum cowardice.",
]

BRAIN_RESULTS = [
    "1 brain cell detected.",
    "2 brain cells fighting for third place.",
    "Loading brain cells...",
    "Brain cells not found.",
    "999 IQ detected.",
    "Brain operating at 300%.",
    "Single brain cell currently overheating.",
    "Brain privileges revoked.",
    "Somalian Brain",
    "You are RETARDED",
]

SOCIAL_EVENTS = [
    "-1500 for being black.",
    "-50 for pinging everyone.",
    "-100 for donating to Africa.",
    "-100 for missing skill checks.",
    "+10 for being funny.",
    "+75 for saying 'gg ez monkey'.",
    "+50 for clutching endgame.",
    "-150 for sandbagging.",
    "+30 for touching grass.",
    "-200 for being online at 4 AM.",
]

LOOT_ITEMS = [
    "Legendary Banana",
    "Broken Keyboard",
    "RTX 9090 (Cardboard Edition)",
    "Killer Shack Key",
    "Half-Eaten Banana",
    "Invisible Flashlight",
    "Golden Locker",
    "Bloodpoint Coupon",
    "Dwight's Missing Brain Cell",
    "Unlimited Sprint Burst",
    "Common Rock",
    "CEO of Niggas",
    "Admin Powers",
    "Expired Medkit",
    "2 Black Slaves",
]

# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Cheesehub is online as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="?help | Serving cheese 🧀"))


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
            "`?lootbox` — Open a lootbox"
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


@bot.command(name="monkey")
async def monkey(ctx, member: discord.Member = None):
    target = member or ctx.author
    rank = random.choice(MONKEY_RANKS)
    ability = random.choice(MONKEY_ABILITIES)
    status = random.choice(MONKEY_STATUS)
    embed = discord.Embed(title="Monkey Rating", description=f"**{target.display_name}** has been analyzed...", color=0x8B4513)
    embed.add_field(name="Rank", value=rank, inline=False)
    embed.add_field(name="Special Ability", value=ability, inline=False)
    embed.add_field(name="Status", value=status, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="loop")
async def loop(ctx, member: discord.Member = None):
    target = member or ctx.author
    win = random.choice([True, False])
    outcome = random.choice(LOOP_WINS) if win else random.choice(LOOP_FAILS)
    reward = random.choice(LOOP_REWARDS)
    embed = discord.Embed(
        title="DBD Loop Simulator",
        description=f"**{target.display_name}** entered a chase...",
        color=0x2ECC71 if win else 0xE74C3C,
    )
    embed.add_field(name="Outcome", value=outcome, inline=False)
    embed.add_field(name="Result", value=reward, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="skillcheck")
async def skillcheck(ctx, member: discord.Member = None):
    target = member or ctx.author
    result = random.choice(SKILL_CHECKS)
    embed = discord.Embed(title="Skill Check!", description=f"**{target.display_name}** attempted a skill check...", color=0xF39C12)
    embed.add_field(name="Result", value=result, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="locker")
async def locker(ctx, member: discord.Member = None):
    target = member or ctx.author
    event = random.choice(LOCKER_EVENTS)
    embed = discord.Embed(title="Locker Event", description=f"**{target.display_name}** entered a locker...", color=0x3498DB)
    embed.add_field(name="What happened?", value=event, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="braincell")
async def braincell(ctx, member: discord.Member = None):
    target = member or ctx.author
    result = random.choice(BRAIN_RESULTS)
    embed = discord.Embed(title="Brain Cell Scan", description=f"Scanning **{target.display_name}**...", color=0x9B59B6)
    embed.add_field(name="Result", value=result, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="socialcredit")
async def socialcredit(ctx, member: discord.Member = None):
    target = member or ctx.author
    event = random.choice(SOCIAL_EVENTS)
    embed = discord.Embed(title="Social Credit System", description=f"**{target.display_name}**'s social credit has been updated.", color=0xE74C3C)
    embed.add_field(name="Update", value=event, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


@bot.command(name="lootbox")
async def lootbox(ctx):
    items = random.sample(LOOT_ITEMS, 3)
    embed = discord.Embed(title="Lootbox Opened!", description=f"**{ctx.author.display_name}** opened a lootbox...", color=0xF1C40F)
    embed.add_field(name="You received", value="\n".join(f"• {item}" for item in items), inline=False)
    await ctx.send(embed=embed)


# ── Word Trigger (fill in your own response!) ─────────────────────────────────
# To add a trigger: put the word in TRIGGER_WORD and your reply in TRIGGER_RESPONSE
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

    # Word trigger — fires when someone's message contains TRIGGER_WORD
    if any(word in message.content.lower() for word in TRIGGER_WORDS_1):
        await message.channel.send(f"{message.author.mention} {TRIGGER_RESPONSE}")

    if any(word in message.content.lower() for word in TRIGGER_WORDS_2):
        await message.channel.send(f"{message.author.mention} {random.choice([TRIGGER_RESPONSE_2, TRIGGER_RESPONSE_2A])}")

    if any(word in message.content.lower() for word in TRIGGER_WORDS_3):
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        embed = discord.Embed(
            description=f"{message.author.mention} {TRIGGER_RESPONSE_3}",
            color=0xFF0000,
        )
        embed.set_image(url="https://media.tenor.com/sSHMBmOqNgMAAAAd/gorlock-gorlockthedestroyer.gif")
        await message.channel.send(embed=embed)

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


# ── Keep-alive web server for Render ──────────────────────────────────────────
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
