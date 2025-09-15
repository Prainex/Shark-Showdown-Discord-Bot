import discord
import logging
import os
import asyncio

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


# Bot setup
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Logging setup
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# Async cog loader
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            await bot.load_extension(f"cogs.{filename[:-3]}")



@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
