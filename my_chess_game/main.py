import pygame
import chess

pygame.init()

WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

piece_images = {}
piece_symbols = ['r', 'n', 'b', 'q', 'k', 'p', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
for symbol in piece_symbols:
    piece_images[symbol] = pygame.transform.scale(
        pygame.image.load(f"pieces/{symbol}.svg"), (SQUARE_SIZE, SQUARE_SIZE)
    )

board = chess.Board()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lokomotiv Plovdiv Chess Game")


def draw_board():
    """Drawing the desk"""
    colors = [pygame.Color("#D2B48C"), pygame.Color("#8B4513")]
    for row in range(ROWS):
        for col in range(COLS):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces():
    """Drawing the pieces over the desk"""
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)

            symbol = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE else piece.symbol()

            shadow_offset = 5
            shadow_color = (50, 50, 50, 100)  # Полупрозрачна сянка
            shadow = piece_images[symbol].copy()
            shadow.fill(shadow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(shadow, (col * SQUARE_SIZE + shadow_offset, (7 - row) * SQUARE_SIZE + shadow_offset))

            # Рисуваме истинската фигура
            screen.blit(piece_images[symbol], (col * SQUARE_SIZE, (7 - row) * SQUARE_SIZE))


running = True
selected_square = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            col, row = x // SQUARE_SIZE, 7 - (y // SQUARE_SIZE)
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
