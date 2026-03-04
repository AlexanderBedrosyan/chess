import requests

headers = {
    "User-Agent": "MyChessApp/1.0 (contact@example.com)"
}

url = "https://api.chess.com/pub/player/magnuscarlsen/games/2024/01"

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    for game in data.get("games", []):
        print(game["pgn"])  # Извежда PGN на партиите
else:
    print(f"Грешка {response.status_code}: {response.text}")


