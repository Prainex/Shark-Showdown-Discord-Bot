import discord
import gspread
import os

from discord.ext import commands, tasks
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from gspread.utils import rowcol_to_a1

load_dotenv()

class Signups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sheet = None
        self.header = []
        self.n_cols = 0
        self.last_row_idx = 1  # track last processed row (1 = header row)

        self.channel_id = int(os.getenv("JOIN_CHANNEL"))

        # Google Sheets setup
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "credentials.json", scope
            )
            self.client = gspread.authorize(creds)
            self.sheet = self.client.open("Test Sheet").sheet1

            # Get header row + number of columns
            self.header = self.sheet.row_values(1)
            self.n_cols = len(self.header) if self.header else 1

            # Figure out how many rows are already filled (column A = required field)
            self.last_row_idx = len(self.sheet.col_values(1))
            if self.last_row_idx < 1:
                self.last_row_idx = 1

            print(f"✅ Connected to Google Sheet. Last processed row = {self.last_row_idx}\n",
                   "If Last processed row = 1, no teams have signed up yet. It's the header row only.")

        except Exception as e:
            print(f"❌ Failed to connect to Google Sheet: {e}")

        # Start background loop
        self.check_signups.start()

    def cog_unload(self):
        self.check_signups.cancel()

    @tasks.loop(seconds=30)  # Check every 60 seconds
    async def check_signups(self):
        if not self.sheet:
            return

        channel = self.bot.get_channel(self.channel_id)
        if not channel:
            print(f"⚠️ Could not find channel with ID {self.channel_id}")
            return

        try:
            # Count non-empty rows in column A
            current_last = len(self.sheet.col_values(1))
            if current_last <= self.last_row_idx:
                return  # no new signups

            # Build range for all new rows
            start_row = max(self.last_row_idx + 1, 2)  # skip header
            end_row = current_last
            start_a1 = rowcol_to_a1(start_row, 1)
            end_a1 = rowcol_to_a1(end_row, max(self.n_cols, 1))
            rng = f"{start_a1}:{end_a1}"

            new_rows = self.sheet.get(rng) or []

            # Announce each new signup
            def build_signup_embed(self, row_dict: dict) -> discord.Embed:
                team_name = row_dict.get("Team Name", "Unknown Team")
                embed = discord.Embed(
                    title="Shark Attack #2",
                    description=f"**{team_name} joined the hunt!** \n",
                    color=discord.Color.purple()
                )
            
                embed.add_field(
                    name="Players",
                    value=(
                    "Riot: dedmos#emo\n"
                    "Riot: Calamity#6737\n"
                    "Riot: om3y#8008\n"
                    "Riot: scarred#872\n"
                    "Riot: huphh#fcity"
                 ),
                    inline=False
                )
            
                embed.set_author(name="Shark Showdown", icon_url="https://sharkattack.sharkattackgaming.com/shark-attack-twt-pic.png")
                return embed

            # for row in new_rows:
            #     # pad row to match header length
            #     if self.header:
            #         row += [""] * (len(self.header) - len(row))
            #         data = dict(zip(self.header, row))
            #         team_name = data.get("Team Name") or row[0] if row else "Unknown Team"
            #     else:
            #         team_name = row[0] if row else "Unknown Team"

            #     await channel.send(f"🎉 New team signed up: **{team_name}**")

            # Update pointer
            self.last_row_idx = current_last

        except Exception as e:
            print(f"❌ Failed to fetch new signups: {e}")


    @commands.command()
    async def teams(self, ctx):
        """Shows total number of teams signed up."""
        if not self.sheet:
            await ctx.send("❌ Google Sheet not connected.")
            return

        try:
            teams = self.last_row_idx - 1  # exclude header
            if teams < 1:
                teams = "there are no teams signed up yet :("
            await ctx.send(f"📊 Total teams signed up: **{teams}**")
        except Exception as e:
            await ctx.send(f"❌ Failed to fetch records: {e}")

    @commands.command()
    async def asd(self,ctx):
        try:
            records = self.sheet.get_all_records()
        except Exception as e:
            print(f"❌ Failed to fetch records: {e}")
            return
        new_team = records[-1]
        team_name = new_team.get("Team Name", "Unknown Team")

        embed = discord.Embed(
            title="Shark Attack #2",
            description=f"**{team_name} has joined**\n\n[Signup now @](https://funhaver.gg/)",
            color=discord.Color.purple()
        )
    
        embed.add_field(
            name="Players",
            value=(
            "Riot: dedmos#emo\n"
            "Riot: Calamity#6737\n"
            "Riot: om3y#8008\n"
            "Riot: scarred#872\n"
            "Riot: huphh#fcity"
         ),
            inline=False
        )
    
        embed.set_author(name="FunhaverGG", icon_url="https://sharkattack.sharkattackgaming.com/shark-attack-twt-pic.png")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Signups(bot))
