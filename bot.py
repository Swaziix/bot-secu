import discord
from discord.ext import commands
import time
import re
import os

TOKEN = os.getenv("KEY")
GUILD_ID = 1450503984778317918
LOG_CHANNEL_ID = 1466896972475531447
ADMIN_ROLE = "god"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

anti_link = True
anti_raid = True
allow_bots = False

join_times = []
spam_cache = {}

LINK_REGEX = re.compile(r"(https?://|www\.)")

@bot.event
async def on_ready():
    print(f"[✓] Bot connecté : {bot.user}")

@bot.event
async def on_member_join(member):
    global join_times

    if member.bot and not allow_bots:
        await member.ban(reason="Bot non autorisé")
        return

    now = time.time()
    join_times.append(now)
    join_times = [t for t in join_times if now - t < 10]

    if anti_raid and len(join_times) >= 5:
        await member.guild.ban(member, reason="Raid détecté")
        log = bot.get_channel(LOG_CHANNEL_ID)
        await log.send("🚨 **Anti-raid activé**")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    uid = message.author.id
    now = time.time()

    spam_cache.setdefault(uid, [])
    spam_cache[uid].append(now)
    spam_cache[uid] = [t for t in spam_cache[uid] if now - t < 5]

    if len(spam_cache[uid]) > 5:
        await message.delete()
        return

    if anti_link and LINK_REGEX.search(message.content):
        if not any(r.name == ADMIN_ROLE for r in message.author.roles):
            await message.delete()
            await message.channel.send("🔗 Liens interdits.", delete_after=5)

    await bot.process_commands(message)

# ===== COMMANDES =====

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def ban(ctx, member: discord.Member, *, reason=""):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 {member} banni")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def mute(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    await member.add_roles(role)
    await ctx.send(f"🔇 {member} mute")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def timeout(ctx, member: discord.Member, minutes: int):
    await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=minutes))
    await ctx.send(f"⏳ {member} timeout {minutes} min")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount)
    await ctx.send(f"🧹 {amount} messages supprimés", delete_after=5)

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def allowbot(ctx, value: str):
    global allow_bots
    allow_bots = value.lower() == "on"
    await ctx.send(f"🤖 Bots autorisés : {allow_bots}")

bot.run(TOKEN)
