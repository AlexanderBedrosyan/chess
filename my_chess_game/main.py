import pygame
import chess

pygame.init()

# Размери на дъската и добавени полета за координатите
SQUARE_SIZE = 80
BOARD_SIZE = SQUARE_SIZE * 8
EXTRA_SPACE = 40  # Разстояние за буквите и цифрите
WIDTH, HEIGHT = BOARD_SIZE + EXTRA_SPACE, BOARD_SIZE + EXTRA_SPACE

# Зареждане на изображенията на фигурите и оразмеряване
piece_images = {}
piece_symbols = ['r', 'n', 'b', 'q', 'k', 'p', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
scaled_size = int(SQUARE_SIZE * 0.85)

for symbol in piece_symbols:
    piece_images[symbol] = pygame.transform.scale(
        pygame.image.load(f"pieces/{symbol}.svg"), (scaled_size, scaled_size)
    )

# Инициализация на дъската
board = chess.Board()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lokomotiv Plovdiv Chess Game")

# Функция за рисуване на дъската с буквите и цифрите
def draw_board():
    colors = [pygame.Color("#D2B48C"), pygame.Color("#8B4513")]
    font = pygame.font.Font(None, 30)

    screen.fill((50, 50, 50))  # Сив фон за допълнителното пространство

    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(
                col * SQUARE_SIZE + EXTRA_SPACE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE
            ))

    # Рисуване на цифрите (отстрани)
    for row in range(8):
        text = font.render(str(8 - row), True, pygame.Color("white"))
        screen.blit(text, (10, row * SQUARE_SIZE + SQUARE_SIZE // 3))

    # Рисуване на буквите (отдолу)
    for col in range(8):
        text = font.render(chr(65 + col), True, pygame.Color("white"))
        screen.blit(text, (col * SQUARE_SIZE + EXTRA_SPACE + SQUARE_SIZE // 3, HEIGHT - 30))

# Функция за рисуване на фигурите
def draw_pieces():
    offset = (SQUARE_SIZE - scaled_size) // 2  # Центриране в квадратите

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            symbol = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE else piece.symbol()

            screen.blit(piece_images[symbol], (
                col * SQUARE_SIZE + EXTRA_SPACE + offset,
                (7 - row) * SQUARE_SIZE + offset
            ))

# Основен цикъл
running = True
selected_square = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            col = (x - EXTRA_SPACE) // SQUARE_SIZE
            row = 7 - (y // SQUARE_SIZE)
            if 0 <= col < 8 and 0 <= row < 8:
                square = chess.square(col, row)

                if selected_square is None:
                    if board.piece_at(square):
                        selected_square = square
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                    selected_square = None

    draw_board()
    draw_pieces()
    pygame.display.flip()

pygame.quit()

