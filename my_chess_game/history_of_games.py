import requests


class HistoryOfGames:
    HEADERS = {"User-Agent": "MyChessApp/1.0 (contact@example.com)"
    }
    URL = "https://api.chess.com/pub/player/"
    PLAYERS = ["magnuscarlsen", "hikaru", "fabianocaruana"]

    def find_all_games(self):
        for player in self.PLAYERS:
            response = requests.get(self.URL + player +"/games/2024/01", headers=self.HEADERS)

            if response.status_code == 200:
                data = response.json()
                for game in data.get("games", []):
                    print(game["pgn"])
            else:
                print(f"Грешка {response.status_code}: {response.text}")


history_of_games = HistoryOfGames()
history_of_games.find_all_games()
