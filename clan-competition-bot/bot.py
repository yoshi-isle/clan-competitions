import datetime
import discord
import os
import logging
from wise_old_man_client import WiseOldManClient
from leaderboard_formatter import LeaderboardFormatter
from discord.ext import commands, tasks
from dotenv import load_dotenv
from database import Database
from embed.competition_embed import get_competition_embed
from models.competition import Competition
from constants import MAIN_CHANNEL_ID

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
        self.update_leaderboard.start()
        await self.tree.sync()
        print(f"{self.user} has connected to Discord!")
        
    @tasks.loop(minutes=5)
    async def update_leaderboard(self):
        bot.logger.info(f"Running update_leaderboard")

        competition: Competition = Competition.from_dict(self.database.competition_collection.find_one({"is_active": True}))
        if competition:
            bot.logger.info(f"Found competition: {competition}")
        else:
            bot.logger.warning("No active competitions found")
            return
        
        data = await bot.wom_client.fetch_competition(competition.wom_id)
        
        current_leaderboard_string = bot.leaderboard_formatter.format_leaderboard(data)
        message = await bot.get_channel(MAIN_CHANNEL_ID).fetch_message(competition.message_id)
        await message.edit(embed=get_competition_embed(competition, current_leaderboard_string))

bot=Bot()

@bot.tree.command(name="ping", description="Tests that the bot is running")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello {interaction.user.name}!", ephemeral=True)

"""
Creates and tracks a competition using the WOM competition ID.
"""
@bot.tree.command(name="create_competition_embed", description="Creates a competition embed (doesn't start the auto-updater)")
async def track_ongoing_competition(interaction: discord.Interaction, competition_id: int, thumbnail_url: str, competition_title: str, ends_on: str):
    bot.logger.info(f"User {interaction.user.display_name} invoked the create_competition_embed command (ID: {competition_id}, Thumbnail URL: {thumbnail_url})")
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
            wom_id=competition_id,
            ends_on=data["endsAt"])
        bot.logger.info(f"Competition created: {competition}\nAttempting to insert into db...")
        bot.database.competition_collection.insert_one(competition.to_dict())
                
        current_leaderboard_string = bot.leaderboard_formatter.format_leaderboard(data)
        message: discord.Message = await interaction.channel.send(embed=get_competition_embed(competition, current_leaderboard_string))
        bot.logger.info(f"Updating message ID {message.id} for record {competition}...")

        bot.database.competition_collection.update_one(
            {"wom_id": competition_id},
            {"$set": {"message_id": message.id}}
        )

    except Exception as e:
        await interaction.response.send_message("Error", ephemeral=True)
        bot.logger.error(f"Error tracking competition (ID: {competition_id}) - {e}")

"""
Starts a competition by message ID
"""
@bot.tree.command(name="start_competition_tracking", description="Starts tracking a competition")
async def track_ongoing_competition(interaction: discord.Interaction, message_id: str):
    bot.logger.info(f"User {interaction.user.display_name} invoked the start_competition_tracking command (Message id: {message_id})")

    try:
        competition: Competition = Competition.from_dict(bot.database.competition_collection.find_one({"message_id": int(message_id)}))
        if competition:
            bot.logger.info(f"Found competition: {competition}")
        else:
            bot.logger.error(f"No competition found for {message_id}")
            
        bot.database.competition_collection.update_one(
            {"message_id": int(message_id)},
            {"$set": {"is_active": True}}
        )
        
    except Exception as e:
        bot.logger.error("")

"""
Stop a competition by message ID
"""
@bot.tree.command(name="stop_competition_tracking", description="Starts tracking a competition")
async def track_ongoing_competition(interaction: discord.Interaction, message_id: str):
    bot.logger.info(f"User {interaction.user.display_name} invoked the stop_competition_tracking command (Message id: {message_id})")

    try:
        competition: Competition = Competition.from_dict(bot.database.competition_collection.find_one({"message_id": int(message_id)}))
        if competition:
            bot.logger.info(f"Found competition: {competition}")
        else:
            bot.logger.error(f"No competition found for {message_id}")
            
        bot.database.competition_collection.update_one(
            {"message_id": int(message_id)},
            {"$set": {"is_active": False}}
        )
        
    except Exception as e:
        bot.logger.error("")

if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
