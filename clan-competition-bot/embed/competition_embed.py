import discord
from models.competition import Competition

def get_competition_embed(competition: Competition, current_leaderboard_string: str):
	embed = discord.Embed(title=f"{competition.name}", description=f"https://wiseoldman.net/competitions/{competition.wom_id}")
	embed.set_thumbnail(url=competition.thumbnail_url)
	embed.add_field(name="", value=f"Competition ends on: {competition.ends_on}",inline=False)
	embed.add_field(name="Top Players*", value=current_leaderboard_string, inline=False)    
	embed.set_footer(text="*Updates every 5 minutes")
	return embed