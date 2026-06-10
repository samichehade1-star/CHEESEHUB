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
    {"q": "What country produces the most cheese in the world?", "a": "united states", "hint": "🇺🇸 Think big and western...", "fact": "The US produces over 6 million metric tons of cheese per year!"},
    {"q": "What type of milk is Roquefort cheese traditionally made from?", "a": "sheep", "hint": "🐑 Not cow, not goat...", "fact": "Roquefort is one of the world's oldest cheeses, aged in the caves of Combalou."},
    {"q": "In what country did Gouda cheese originate?", "a": "netherlands", "hint": "🌷 Famous for windmills and tulips...", "fact": "Gouda has been traded at the Gouda market since the 14th century!"},
    {"q": "What gives blue cheese its distinctive colour?", "a": "mold", "hint": "🔵 It's a living organism...", "fact": "Penicillium roqueforti is the mould used — related to the antibiotic penicillin!"},
    {"q": "How many litres of milk does it take to make 1kg of hard cheese (approx)?", "a": "10", "hint": "🥛 It's a double-digit number...", "fact": "The exact amount varies by cheese type, but hard cheeses need the most milk."},
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
    "Mini Nigga", "Banana Enthusiast", "Lvl 3 Monkey", "Jungle Warrior", "Kool-Aid Drinker",
    "Manager at KFC", "Low Battery Smoke Alarm", "Gigga Nigga", "Bannana Muncher",
    "Welfare King", "Section 8 Swinger", "40oz Apostle", "Gorilla",
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

LOOP_FAILS = [
    "Ran into a wall while looking behind like a dumb monkey.",
    "You are license banned, dumbass.",
    "Classic skill issue, smooth brain.",
    "Downloaded Milkyway Malware mid-nut.",
    "Accidentally cornered yourself like a retard.",
    "Stopped to twerk and got clapped.",
    "Forgot where the door was.",
    "Tried to heal mid argument.",
    "Hid in a locker like a pussy.",
    "Got stuck on a tree like a real monkey.",
    "Led the whole crew straight to the cops.",
    "Used all your swag and still died.",
    "Forgot you were injured and bled out.",
    "Ran straight into a dead end.",
    "Mistook the opps for your homies.",
]

LOOP_WINS = [
    "Ran circles around them for 30 minutes straight.",
    "Made them rage quit life.",
    "ALT + F4'd their entire ego.",
    "Escaped with perfect timing.",
    "Made them lose track like a blind nigga.",
    "Moved like a crackhead on a mission.",
    "Made them question their whole bloodline.",
    "Ran so hard they became friendly.",
    "Successfully wasted their entire day.",
    "Got accused of cheating by everyone.",
    "Ran until they disconnected in tears.",
    "Created a viral montage of the L.",
    "Turned them into a spectator.",
    "Unlocked Ultra Instinct and disrespected their ancestors.",
]

LOOP_REWARDS = [
    "Reward: Got your ass beat in the alley.",
    "Reward: Jumped by the whole hood.",
    "Reward: Received unsolicited femboy pics from SYAZ.",
    "Reward: They left you for dead anyway.",
    "Reward: 4 poorly fed slaves and a warm banana.",
    "Reward: They uninstalled... after robbing you first.",
    "Reward: Tiddy Pics (from a man).",
    "Reward: Earned bragging rights and 12 assault charges.",
    "NO MORE FREE KEYS. AND THATS THAT.",
    "Reward: Chlamydia from the trap house.",
    "Reward: Anal rape by Shaquille O'Neal in the basement.",
    "Reward: Got hate mail calling you a n***** monkey.",
    "Reward: Your mom walked in during the worst moment.",
    "Reward: Permanent broke nigga status.",
    "Reward: The whole block called you retarded.",
    "Reward: Free trip to the hospital with no insurance.",
]

SKILL_CHECKS = [
    "Great Skill Check! +300 points, you lucky monkey.",
    "Nigga turn on auto skill check, you slow as fuck.",
    "Missed the Skill Check, typical.",
    "Exploded everything like a monkey with dynamite.",
    "Accidentally alerted the whole block with your monkey noises.",
    "Missed because you're black.",
    "Missed so badly you lost 20% of your dignity.",
    "Skill Issue... as expected.",
    "Closed their eyes and somehow hit Great. Monkey magic.",
    "Broke the laws of probability... and still got clapped.",
    "Failed so hard your ancestors felt it.",
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
    "1 brain cell detected... and it's struggling.",
    "2 brain cells fighting for third place.",
    "Loading brain cells... still loading...",
    "Brain cells not found. 404 Error.",
    "999 IQ detected (in your dreams, nigga).",
    "Brain operating at 300%... of a goldfish.",
    "Single brain cell currently overheating.",
    "Brain privileges revoked.",
    "Somalian Brain detected.",
    "You are actually RETARDED.",
    "Brain smooth as a bowling ball.",
    "You are RETARDED",
]

SOCIAL_EVENTS = [
    "-1500 for being black.",
    "-50 for pinging everyone like a spastic.",
    "-100 for donating to Africa (they spent it on guns).",
    "-100 for fucking up again.",
    "+10 for being funny (rare as hell).",
    "+75 for saying 'gg ez monkey'.",
    "+50 for clutching like a real one.",
    "-150 for snitching on the crew.",
    "+30 for touching grass (first time in years).",
    "-200 for being online at 4 AM instead of getting a job.",
    "-300 for saying the N-word with the hard R.",
    "+25 for bringing banana offerings.",
]

LOOT_ITEMS = [
    "Legendary Banana",
    "Broken Keyboard (from raging)",
    "RTX 9090 (Cardboard Edition)",
    "Half-Eaten Banana",
    "Invisible Glock",
    "Golden Chains (stolen)",
    "Bloodstained Coupon",
    "Dwight's Missing Brain Cell",
    "Unlimited Sprint (lasts 2 seconds)",
    "Common Rock",
    "CEO of Niggas title",
    "Temporary Admin Powers (will be revoked)",
    "Expired Medkit covered in blood",
    "2 Black Slaves (low quality)",
    "Shaquille O'Neal's Used Condom",
    "Welfare Check",
    "Government Cheese Block",
    "Bag of Wet Fries",
]

ESEX_GIFS = [
    "https://media.tenor.com/26027474/ahegao-delfine-bell.gif",
    "https://media.tenor.com/15863036/sexy-girl-twerk-sexy-girl-twerk-twerking-gif.gif",
    "https://media.tenor.com/19020455/twerk-sexy-girl-sexy-girl-ass-gif.gif",
    "https://media.tenor.com/15496026/twerk-girl-sexy-twerking-ass-gif.gif",
    "https://media.tenor.com/20848429/hot-dance-thicc-pw-ionna-gif.gif",
    "https://media.tenor.com/23106330/ahegao-sexy-ahegao-girl-egirl-realneko-gif.gif",
    "https://media.tenor.com/18514385/ahegao-blonde-girl-hot-gif.gif",
    "https://media.tenor.com/21124784/bee-girl-twerk-gif.gif",
    "https://media.tenor.com/12952373064437539905/twerk-twerking-girl-twerk-girl-twerking-girl-booty-gif.gif",
    "https://media.tenor.com/12761440296533616720/bunger-twerk-anime-girl-woman-weezer-gif.gif",
]

def get_random_esex():
    if not ESEX_GIFS:
        return None
    return random.choice(ESEX_GIFS)

# ── Keep-alive task (defined before on_ready) ──────────────────────────────────
@tasks.loop(minutes=5)
async def keep_alive():
    try:
        async with aiohttp.ClientSession() as session:
            await session.get("https://cheesehub.onrender.com")
    except Exception:
        pass

# ── Events ─────────────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    print(f"✅ Cheesehub is online as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="?help | Serving cheese 🧀"))
    keep_alive.start()

# ── Commands ───────────────────────────────────────────────────────────────────
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="🧀 Cheesehub — Command Menu", description="Your friendly neighbourhood cheese bot!", color=0xF5C542)
    embed.add_field(name="🧀 Cheese", value="`?cheese`\n`?joke`\n`?trivia`\n`?hint`\n`?skip`", inline=False)
    embed.add_field(name="🎮 Fun", value="`?8ball`\n`?gay`\n`?dick`\n`?roast`\n`?monkey`\n`?loop`\n`?skillcheck`\n`?locker`\n`?braincell`\n`?socialcredit`\n`?lootbox`\n`?esex`", inline=False)
    embed.add_field(name="ℹ️ Info", value="`?help`\n`?ping`", inline=False)
    embed.set_footer(text="Made with 🧀 | Cheesehub v1.0")
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

@bot.command(name="cheese")
async def cheese_fact(ctx):
    embed = discord.Embed(title="🧀 Cheese Fact!", description=random.choice(CHEESE_FACTS), color=0xF5C542)
    await ctx.send(embed=embed)

@bot.command(name="joke")
async def cheese_joke(ctx):
    setup, punchline = random.choice(CHEESE_JOKES)
    embed = discord.Embed(title="😄 Cheesy Joke", color=0xF5C542)
    embed.add_field(name="❓", value=setup, inline=False)
    embed.add_field(name="💬", value=f"||{punchline}||", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="trivia")
async def trivia(ctx):
    if ctx.channel.id in active_trivia:
        await ctx.send(f"⚠️ A trivia is already active!")
        return
    question = random.choice(TRIVIA_QUESTIONS)
    active_trivia[ctx.channel.id] = question
    embed = discord.Embed(title="🧀 Cheese Trivia!", description=question["q"], color=0xF5A600)
    await ctx.send(embed=embed)

@bot.command(name="hint")
async def hint(ctx):
    if ctx.channel.id not in active_trivia:
        await ctx.send("❌ No active trivia!")
        return
    await ctx.send(f"💡 **Hint:** {active_trivia[ctx.channel.id]['hint']}")

@bot.command(name="skip")
async def skip(ctx):
    if ctx.channel.id not in active_trivia:
        await ctx.send("❌ No active trivia!")
        return
    answer = active_trivia.pop(ctx.channel.id)["a"]
    await ctx.send(f"⏭️ Skipped! Answer was **{answer.title()}**.")

@bot.command(name="8ball")
async def eightball(ctx, *, question: str = None):
    if not question:
        await ctx.send("❓ Ask a question!")
        return
    emoji, response = random.choice(EIGHTBALL_RESPONSES)
    embed = discord.Embed(title="🎱 Magic 8-Ball", color=0x2B2D31)
    embed.add_field(name="Question", value=question, inline=False)
    embed.add_field(name=f"{emoji} Answer", value=response, inline=False)
    await ctx.send(embed=embed)

@bot.command(name="gay")
async def gay(ctx, member: discord.Member = None):
    target = member or ctx.author
    value = random.randint(0, 100)
    message = next((msg for r, msg in GAY_MESSAGES if value in r), "100% Gay Icon")
    embed = discord.Embed(title="Gay Meter", description=f"**{target.display_name}**", color=0xFF69B4)
    embed.add_field(name="Result", value=f"**{value}%**", inline=False)
    embed.add_field(name="Verdict", value=message, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="dick")
async def dick(ctx, member: discord.Member = None):
    target = member or ctx.author
    value = random.randint(0, 8)
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
    bar = "()" if value == 0 else "8" + "=" * value + "D"
    embed = discord.Embed(title="Dick Meter", color=0x5865F2)
    embed.add_field(name=target.display_name, value=f"`{bar}` **{value} inches**", inline=False)
    embed.add_field(name="Verdict", value=message, inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="roast")
async def roast(ctx, member: discord.Member = None):
    target = member or ctx.author
    roasts = [
        "You look like you use Furry or Milkygay",
        "I'm sorry your mom never put your artwork on the wall as a kid.",
        "Your logic would lose to a Magic 8 Ball.",
        "You built like a windshield wiper.",
        "You remind me of Sora",
    ]
    embed = discord.Embed(title="🔥 Roasted!", description=f"{target.mention} {random.choice(roasts)}", color=0xE74C3C)
    await ctx.send(embed=embed)

@bot.command(name="monkey")
async def monkey(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title="Monkey Rating", description=f"**{target.display_name}**", color=0x8B4513)
    embed.add_field(name="Rank", value=random.choice(MONKEY_RANKS), inline=False)
    embed.add_field(name="Ability", value=random.choice(MONKEY_ABILITIES), inline=False)
    embed.add_field(name="Status", value=random.choice(MONKEY_STATUS), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="loop")
async def loop(ctx, member: discord.Member = None):
    target = member or ctx.author
    win = random.choice([True, False])
    outcome = random.choice(LOOP_WINS) if win else random.choice(LOOP_FAILS)
    embed = discord.Embed(title="Loop Simulator", description=f"**{target.display_name}**", color=0x2ECC71 if win else 0xE74C3C)
    embed.add_field(name="Outcome", value=outcome, inline=False)
    embed.add_field(name="Reward", value=random.choice(LOOP_REWARDS), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="skillcheck")
async def skillcheck(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title="Skill Check!", description=f"**{target.display_name}**", color=0xF39C12)
    embed.add_field(name="Result", value=random.choice(SKILL_CHECKS), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="locker")
async def locker(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title="Locker Event", description=f"**{target.display_name}**", color=0x3498DB)
    embed.add_field(name="Event", value=random.choice(LOCKER_EVENTS), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="braincell")
async def braincell(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title="Brain Cell Scan", description=f"**{target.display_name}**", color=0x9B59B6)
    embed.add_field(name="Result", value=random.choice(BRAIN_RESULTS), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="socialcredit")
async def socialcredit(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title="Social Credit", description=f"**{target.display_name}**", color=0xE74C3C)
    embed.add_field(name="Update", value=random.choice(SOCIAL_EVENTS), inline=False)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="lootbox")
async def lootbox(ctx):
    items = random.sample(LOOT_ITEMS, 3)
    embed = discord.Embed(title="Lootbox Opened!", description=f"**{ctx.author.display_name}**", color=0xF1C40F)
    embed.add_field(name="You received", value="\n".join(f"• {item}" for item in items), inline=False)
    await ctx.send(embed=embed)

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
        embed.set_image(url="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExOTdndTRiZzJpNXc4YnBwancwZ2hxdmF4dTBkNWtrdWJyZ2wzd2FnMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/IUkDQZP2AJyxU3cXBn/giphy.gif")
        await message.channel.send(embed=embed)
        embed2 = discord.Embed(color=0xFF0000)
        embed2.set_image(url="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExeXRnemhja3NmbXd5aDQ0MnFhcm9lMW1jeGZ5NWlxYnJvazg2bTVpaCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/CWsz3htAnOa4ScUHyE/giphy.gif")
        await message.channel.send(embed=embed2)

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

# ── Keep-alive web server ──────────────────────────────────────────────────────
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
