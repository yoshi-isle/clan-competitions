from logging import Logger

class LeaderboardFormatter:
    def __init__(self, logger: Logger):
        self.logger = logger

    def format_leaderboard(self, data):
        self.logger.info(f"Formatting leaderboard")
        placement = 1
        top_players = data['participations'][:15]
        self.logger.info(f"Top players {top_players}")
        formatted_leaderboard = ""
        for i, player_data in enumerate(top_players):
            username = player_data['player']['username']
            gained = player_data['progress']['gained']
            self.logger.info(f"{i}: {player_data}")
            self.logger.info(f"{username} gained {gained} XP")
            emoji = ""
            if placement == 1:
                emoji = "🏆 "
            elif placement == 2:
                emoji = "🥈 "
            elif placement == 3:
                emoji = "🥉 "
            formatted_leaderboard += f"{emoji}{i+1}. {username}: {gained} xp\n"
            placement += 1
        self.logger.info(f"{formatted_leaderboard}")
        return formatted_leaderboard, data["endsAt"]
