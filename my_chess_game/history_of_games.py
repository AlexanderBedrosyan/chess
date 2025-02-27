import requests
import chess.pgn
import io


class HistoryOfGames:
    HEADERS = {
        "User-Agent": "MyChessApp/1.0 (contact@example.com)"
    }
    URL = "https://api.chess.com/pub/player/"
    PLAYERS = ["magnuscarlsen", "hikaru", "fabianocaruana"]

    def find_all_games(self):
        games = []
        for player in self.PLAYERS:
            response = requests.get(self.URL + player + "/games/2024/01", headers=self.HEADERS)

            if response.status_code == 200:
                data = response.json()
                for game in data.get("games", []):
                    pgn_text = game["pgn"]
                    fens = self.get_fen_positions(pgn_text)
                    games.append(fens)
                    # print(game["pgn"])
                    print(fens)
                    exit()
            else:
                print(f"Грешка {response.status_code}: {response.text}")

        return games

    def get_fen_positions(self, pgn_text):
        fen_positions = []
        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if not game:
            return fen_positions

        board = game.board()
        fen_positions.append(board.fen())

        for move in game.mainline_moves():
            board.push(move)
            fen_positions.append(board.fen())

        return fen_positions

    def find_matching_games(self, current_fen):
        games = self.find_all_games()
        matching_games = []

        for game in games:
            if current_fen in game:
                matching_games.append(game)

        return matching_games


history_of_games = HistoryOfGames()
print(history_of_games.find_all_games())
current_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
print(history_of_games.find_matching_games(current_fen))
