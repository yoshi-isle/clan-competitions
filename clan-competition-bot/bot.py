import datetime
import discord
import os
import logging
from wise_old_man_client import WiseOldManClient
from leaderboard_formatter import LeaderboardFormatter
from discord.ext import commands
from dotenv import load_dotenv
from database import Database
from embed.competition_embed import get_competition_embed
from models.competition import Competition

class Bot(commands.Bot):
    def __init__(self):
        # Load environmental variables
        load_dotenv()
        
        # Logging
        self.logger: logging.Logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)

        # Services
        self.database: Database = Database(self.logger)
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
@bot.tree.command(name="create_competition_embed", description="Creates a competition embed (doesn't start the auto-updater)")
async def track_ongoing_competition(interaction: discord.Interaction, competition_id: int, thumbnail_url: str, competition_title: str, ends_on: str):
    bot.logger.info(f"User {interaction.user.display_name} invoked the track_ongoing_competition command (ID: {competition_id}, Thumbnail URL: {thumbnail_url})")
    if not competition_id:
        bot.logger.warning(f"Interaction by {interaction.user.display_name} - No competition ID given")
        await interaction.response.send_message("No competition ID given")
        return
    if not thumbnail_url:
        bot.logger.warning(f"Interaction by {interaction.user.display_name} - No thumbnail_url given")
        await interaction.response.send_message("No valid image given")
        return
    
    try:
        data = await bot.wom_client.fetch_competition(competition_id)
        competition = Competition(
            message_id=None,
            is_active=False,
            thumbnail_url=thumbnail_url,
            name=competition_title,
            wom_id=competition_id)
        bot.logger.info(f"Competition created: {competition}\nAttempting to insert into db...")
        
        bot.database.competition_collection.insert_one(competition.to_dict())
                
        current_leaderboard_string = bot.leaderboard_formatter.format_leaderboard(data)
        message: discord.Message = await interaction.channel.send(embed=get_competition_embed(competition, current_leaderboard_string, ends_on))
        bot.logger.info(f"Updating message ID {message.id} for record {competition}...")

        bot.database.competition_collection.update_one(
            {"wom_id": competition_id},
            {"$set": {"message_id": message.id}}
        )

    except Exception as e:
        await interaction.response.send_message("Error", ephemeral=True)
        bot.logger.error(f"Error tracking competition (ID: {competition_id}) - {e}")
    
if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
