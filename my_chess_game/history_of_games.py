import requests


class HistoryOfGames:
    HEADERS = {"User-Agent": "MyChessApp/1.0 (contact@example.com)"
    }
    URL = "https://api.chess.com/pub/player/magnuscarlsen/games/2024/01"

    def find_all_games(self):
        response = requests.get(self.URL, headers=self.HEADERS)

        if response.status_code == 200:
            data = response.json()
            for game in data.get("games", []):
                print(game["pgn"])
        else:
            print(f"Грешка {response.status_code}: {response.text}")


history_of_games = HistoryOfGames()
history_of_games.find_all_games()
