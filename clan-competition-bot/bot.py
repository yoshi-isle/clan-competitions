import datetime
import discord
import os
import logging
from wise_old_man_client import WiseOldManClient
from leaderboard_formatter import LeaderboardFormatter
from discord.ext import commands
from dotenv import load_dotenv

class Bot(commands.Bot):
    def __init__(self):
        # Load environmental variables
        load_dotenv()
        
        # Logging
        self.logger: logging.Logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)

        # Services
        self.wom_client: WiseOldManClient = WiseOldManClient(self.logger)
        self.leaderboard_formatter: LeaderboardFormatter = LeaderboardFormatter(self.logger)
    
        # Initialize bot
        intents=discord.Intents.all()
        intents.message_content=True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        await self.tree.sync()
        print(f"{self.user} has connected to Discord!")


bot=Bot()

@bot.tree.command(name="ping", description="Tests that the bot is running")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.name}!", ephemeral=True)

"""
Creates and tracks a competition using the WOM competition ID.
"""
@bot.tree.command(name="track_ongoing_competition", description="Track a new competition")
async def track_ongoing_competition(interaction: discord.Interaction, competition_id: int, thumbnail_url: str):
    if not competition_id:
        await interaction.response.send_message("No competition ID given")
        return
    if not thumbnail_url:
        await interaction.response.send_message("No valid image given")
        return
    
    bot.logger.info(f"User {interaction.user.display_name} invoked the track_ongoing_competition command (ID: {competition_id}, Thumbnail URL: {thumbnail_url})")
    
    try:
        data = await bot.wom_client.fetch_competition(competition_id)
        (leaderboard, ends_on) = bot.leaderboard_formatter.format_leaderboard(data)
        embed = discord.Embed(title="Runecrafting Competition", description="https://wiseoldman.net/competitions/77662")
        embed.set_thumbnail(url=thumbnail_url)
        embed.add_field(name="", value=f"Competition ends on: {ends_on}",inline=False)
        embed.add_field(name="Top Players*",
                            value=leaderboard,
                            inline=False,)    
        embed.set_footer(text="*Updates every 5 minutes")
        await interaction.channel.send(embed=embed)

    except Exception as e:
        await interaction.response.send_message("Error", ephemeral=True)
        bot.logger.error(f"Error tracking competition (ID: {competition_id})")
    
if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
