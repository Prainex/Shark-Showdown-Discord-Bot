import discord 
from discord.ext import commands, tasks
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio

class Signups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_count = 0
        self.check_signups.start()

        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open("Shark Showdown - Admin Sheet").sheet1