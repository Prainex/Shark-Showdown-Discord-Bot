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

    #Stop background loop
    def cog_unload(self):
        self.check_signups.cancel()

    def build_signup_embed(self, row_dict: dict) -> discord.Embed:
        team_name = row_dict.get("Team Name", "Unknown Team")

        embed = discord.Embed(
            title="Shark Attack #2",
            description=f"**{team_name} joined the hunt!** \n",
            color=discord.Color.purple()
        )

        embed.set_author(
            name="Shark Showdown",
            icon_url="https://sharkattack.sharkattackgaming.com/shark-attack-twt-pic.png"
        )

        '''Test Sheet Fields'''
        # # Coaches
        # coaches = [row_dict.get(f"Coach") for i in range(1, 2) if row_dict.get(f"Coach")]
        # if coaches:
        #     embed.add_field(name="Coaches", value="\n".join(coaches), inline=False)


        # # Players
        # players = [row_dict.get(f"Player {i}") for i in range(1, 6) if row_dict.get(f"Player {i}")]
        # if players:
        #     embed.add_field(name="Players", value="\n".join([f"Riot: {p}" for p in players]), inline=False)

        # # Subs
        # subs = [row_dict.get(f"Sub {i}") for i in range(1, 3) if row_dict.get(f"Sub {i}")]
        # if subs:
        #     embed.add_field(name="Substitutes", value="\n".join([f"Riot: {s}" for s in subs]), inline=False)

        '''Main Sheet Fields'''
        # Coaches
        coaches = [row_dict.get(f"Coach Riot ID:") for i in range(1, 3) if row_dict.get(f"Coach Riot ID:")]
        if coaches:
            embed.add_field(name="Coaches", value="\n".join(coaches), inline=False)

        # Players
        players = [row_dict.get(f"Player {i} Riot ID:") for i in range(1, 6) if row_dict.get(f"Player {i} Riot ID:")]
        if players:
            embed.add_field(name="Players", value="\n".join([f"Riot: {p}" for p in players]), inline=False)

        # Subs
        subs = [row_dict.get(f"Sub {i} Riot ID:") for i in range(1, 3) if row_dict.get(f"Sub {i} Riot ID:")]
        if subs:
            embed.add_field(name="Substitutes", value="\n".join([f"Riot: {s}" for s in subs]), inline=False)

        return embed


    @tasks.loop(seconds=30)
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
            for row in new_rows:
                row += [""] * (len(self.header) - len(row))
                row_dict = dict(zip(self.header, row))

                embed = self.build_signup_embed(row_dict)
                await channel.send(embed=embed)

            # Update pointer
            self.last_row_idx = current_last

        except Exception as e:
            print(f"❌ Failed to fetch new signups: {e}")


    #Shows total number of teams signed up.
    @commands.command()
    async def teams(self, ctx):
        if not self.sheet:
            await ctx.send("❌ Google Sheet not connected.")
            return

        min_teams = 23
        try:
            teams = self.last_row_idx - 1  # exclude header
            if teams < 1:
                await ctx.send("📊 No teams have signed up yet.")
            else:
                await ctx.send(f"📊 Total teams signed up: **{teams}** out of {min_teams} to run the event!")
        except Exception as e:
            await ctx.send(f"❌ Failed to fetch records: {e}")


    #Stops the recurring Google Sheets API calls.
    @commands.command()
    async def stop_signups(self, ctx):
        if self.check_signups.is_running():
            self.cog_unload()
            await ctx.send("✅ The signup check task has been stopped.")
        else:
            await ctx.send("⚠️ The signup check task is not currently running.")


    #Restarts the recurring Google Sheets API calls.
    @commands.command()
    async def start_signups(self, ctx):
        if not self.check_signups.is_running():
            self.check_signups.start()
            await ctx.send("✅ The signup check task has been started.")
        else:
            await ctx.send("⚠️ The signup check task is already running.")

async def setup(bot):
    await bot.add_cog(Signups(bot))
