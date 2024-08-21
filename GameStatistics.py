import json
import collections
from json import JSONDecodeError


class GameStatistics:
    """
        A class for managing game statistics.

        Attributes:
            player_performance (dict): Stores player performance data.
            typed_characters (Counter): Stores counts of typed characters.
        """

    def __init__(self):
        data = self.load_data_from_file()
        self.player_performance = data.get("player_performance", {})
        self.typed_characters = collections.Counter(data.get("typed_characters", {}))

    def print_yellow(self, text):
        """Prints text in yellow color"""

        print("\033[33m{}\033[0m".format(text))

    def load_data_from_file(self):
        """ Loads data from a JSON file named 'statistics.json'.
        If the file is not found or there's a JSON decoding error, it prints an error message and returns
            an empty dictionary. """
        try:
            with open('statistics.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, JSONDecodeError) as error:
            self.print_yellow(f"Error loading data: {error}")
            return {}

    def update_player_performance(self, player):
        """Updates player performance data. Increments the performance count for a player if they answered correctly
        and writes the updated data to the JSON file """

        if player["correct"]:
            player_name = player['name']
            if player_name not in self.player_performance:
                self.player_performance[player_name] = 0
            self.player_performance[player_name] += 1
            self.write_statistics_to_file()  # Update JSON file

    def update_typed_characters(self, answer):
        """Updates the count of typed characters"""

        for char in answer:
            self.typed_characters[char] += 1

    def print_statistics(self):
        """
            Prints statistics including the top 3 best teams ever played on the server, the most commonly typed
            character, and the least commonly typed character"""

        self.print_yellow("Statistics:")
        # Best Teams Ever Played
        if len(self.player_performance) >= 1:
            best_teams = sorted(self.player_performance, key=self.player_performance.get, reverse=True)[:3]
            self.print_yellow("Top 3 best teams ever to play on this server:")
            for idx, team in enumerate(best_teams, start=1):
                self.print_yellow(f"{idx}. {team}")
        else:
            self.print_yellow("No player performance data available.")

        # Most Commonly Typed Character
        most_common_character = self.typed_characters.most_common(1)[0][0]
        least_common_character = self.typed_characters.most_common()[-1][0]
        self.print_yellow(f"Most commonly typed character: {most_common_character}")
        self.print_yellow(f"Least commonly typed character: {least_common_character}\n")

    def write_statistics_to_file(self):
        """Writes the current statistics data to the 'statistics.json' file"""

        with open('statistics.json', 'w') as file:
            statistics_data = {
                'player_performance': self.player_performance,
                'typed_characters': dict(self.typed_characters)
            }
            json.dump(statistics_data, file)

    def read_statistics_from_file(self):
        """Reads statistics data from the 'statistics.json' file and updates class attributes accordingly"""

        with open('statistics.json', 'r') as file:
            statistics_data = json.load(file)
            self.player_performance = statistics_data.get('player_performance', {})
            self.typed_characters = collections.Counter(statistics_data.get('typed_characters', {}))

    def get_statistics(self):
        """Generates a message containing statistics, including the top 3 best teams ever played and the most commonly
        typed character,lest commonly typed character and returns it as a string"""

        stat_mes = ""
        stat_mes += "Statistics: \n"

        # Top 3 Best Teams Ever Played
        if len(self.player_performance) >= 1:
            best_teams = sorted(self.player_performance, key=self.player_performance.get, reverse=True)[:3]
            stat_mes += "Top 3 best teams ever to play on this server:\n"
            for idx, team in enumerate(best_teams, start=1):
                stat_mes += f"{idx}. {team}\n"
        else:
            stat_mes += "No player performance data available.\n"

        # Most Commonly Typed Character
        most_common_character = self.typed_characters.most_common(1)[0][0]
        stat_mes += f"\nMost commonly typed character: {most_common_character}"

        least_common_character = self.typed_characters.most_common()[-1][0]
        stat_mes += f"\nLeast commonly typed character: {least_common_character}\n"
        return stat_mes