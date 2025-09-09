import discord
import logging
import os

from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
handler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
