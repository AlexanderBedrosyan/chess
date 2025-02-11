import pygame
import chess
from metrix import DisplayMetrix

pygame.init()

display_board = DisplayMetrix()
display_board.transform_symbols_into_image()

# Desk starting
board = chess.Board()
screen = pygame.display.set_mode((display_board.WIDTH, display_board.HEIGHT))
pygame.display.set_caption(display_board.NAME_OF_THE_BOARD)

# Функция за рисуване на дъската с буквите и цифрите
def draw_board():
    colors = [pygame.Color("#D2B48C"), pygame.Color("#8B4513")]
    font = pygame.font.Font(None, 30)

    screen.fill((50, 50, 50))  # Сив фон за допълнителното пространство

    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(
                col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE, row * display_board.SQUARE_SIZE, display_board.SQUARE_SIZE, display_board.SQUARE_SIZE
            ))

    # Рисуване на цифрите (отстрани)
    for row in range(8):
        text = font.render(str(8 - row), True, pygame.Color("white"))
        screen.blit(text, (10, row * display_board.SQUARE_SIZE + display_board.SQUARE_SIZE // 3))

    # Рисуване на буквите (отдолу)
    for col in range(8):
        text = font.render(chr(65 + col), True, pygame.Color("white"))
        screen.blit(text, (col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + display_board.SQUARE_SIZE // 3, display_board.HEIGHT - 30))

# Функция за рисуване на фигурите
def draw_pieces():
    offset = (display_board.SQUARE_SIZE - display_board.SCALED_SIZE) // 2  # Центриране в квадратите

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            symbol = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE else piece.symbol()

            screen.blit(display_board.PIECE_IMAGES[symbol], (
                col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + offset,
                (7 - row) * display_board.SQUARE_SIZE + offset
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
            col = (x - display_board.EXTRA_SPACE) // display_board.SQUARE_SIZE
            row = 7 - (y // display_board.SQUARE_SIZE)
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

