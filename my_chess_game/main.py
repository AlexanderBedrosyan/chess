import pygame
import chess
from metrics import DisplayMetrix, HistoryOfMoves

pygame.init()

display_board = DisplayMetrix()
display_board.transform_symbols_into_image()

history_of_moves = HistoryOfMoves()

# Desk starting
board = chess.Board()
screen = pygame.display.set_mode((display_board.WIDTH + 50, display_board.HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption(display_board.NAME_OF_THE_BOARD)


def draw_board():
    colors = [pygame.Color(display_board.FIRST_COLOR), pygame.Color(display_board.SECOND_COLOR)]
    font = pygame.font.Font(None, display_board.FONT_SIZE)

    screen.fill(display_board.ADDITIONAL_COLOR)  # Grey background

    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(screen, color, pygame.Rect(
                col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE, row * display_board.SQUARE_SIZE,
                display_board.SQUARE_SIZE, display_board.SQUARE_SIZE
            ))

        # Рисуване на цифрите (обратен ред, ако flipped)
    for row in range(8):
        num = str(8 - row) if not display_board.IS_FLIPPED else str(row + 1) 
        text = font.render(num, True, pygame.Color(display_board.LETTERS_AND_DIGITS_COLOR))
        screen.blit(text, (10, row * display_board.SQUARE_SIZE + display_board.SQUARE_SIZE // 3))

    # Рисуване на буквите (обратен ред, ако flipped)
    for col in range(8):
        letter = chr(65 + col) if not display_board.IS_FLIPPED else chr(65 + (7 - col))
        text = font.render(letter, True, pygame.Color(display_board.LETTERS_AND_DIGITS_COLOR))
        screen.blit(text, (
            col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + display_board.SQUARE_SIZE // 3,
            display_board.HEIGHT - 80
        ))
    # # Drawing numbers
    # for row in range(8):
    #     text = font.render(str(8 - row), True, pygame.Color(display_board.LETTERS_AND_DIGITS_COLOR))
    #     screen.blit(text, (10, row * display_board.SQUARE_SIZE + display_board.SQUARE_SIZE // 3))
    #
    # # Drawing letters
    # for col in range(8):
    #     text = font.render(chr(65 + col), True, pygame.Color(display_board.LETTERS_AND_DIGITS_COLOR))
    #     screen.blit(text, (col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + display_board.SQUARE_SIZE // 3, display_board.HEIGHT - 80))


def draw_button():
    mouse_x, mouse_y = pygame.mouse.get_pos()

    if display_board.UNDO_BUTTON.collidepoint(mouse_x, mouse_y):
        color = pygame.Color("darkgray")
    else:
        color = pygame.Color("gray")

    pygame.draw.rect(screen, color, display_board.UNDO_BUTTON, border_radius=30)
    undo_text = pygame.font.Font(None, 30).render("Undo", True, pygame.Color("white"))
    text_rect = undo_text.get_rect(center=display_board.UNDO_BUTTON.center)
    screen.blit(undo_text, text_rect)

    flip_color = pygame.Color("darkgray") if display_board.FLIP_BUTTON.collidepoint(mouse_x, mouse_y) else pygame.Color(
        "gray")
    pygame.draw.rect(screen, flip_color, display_board.FLIP_BUTTON, border_radius=30)
    flip_text = pygame.font.Font(None, 30).render("Flip Board", True, pygame.Color("white"))
    screen.blit(flip_text, flip_text.get_rect(center=display_board.FLIP_BUTTON.center))


# Drawing the pieces
def draw_pieces():
    offset = (display_board.SQUARE_SIZE - display_board.SCALED_SIZE) // 2  # Put into the center

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)

            if display_board.IS_FLIPPED:
                row = 7 - row
                col = 7 - col

            symbol = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE else piece.symbol()

            screen.blit(display_board.PIECE_IMAGES[symbol], (
                col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + offset,
                (7 - row) * display_board.SQUARE_SIZE + offset
            ))


# Main loop
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

            if display_board.UNDO_BUTTON.collidepoint(x, y):
                history_of_moves.undo_last_move(board)

            elif display_board.FLIP_BUTTON.collidepoint(x, y):
                display_board.board_flip()

            if display_board.IS_FLIPPED:
                col = 7 - col  # Обръщаме колоните
                row = 7 - row

            if 0 <= col < 8 and 0 <= row < 8:
                square = chess.square(col, row)

                if selected_square is None:
                    if board.piece_at(square):
                        selected_square = square
                        legal_moves = [move for move in board.legal_moves if move.from_square == square]
                        print(f"Позволени ходове за {board.piece_at(square)}: {[board.san(m) for m in legal_moves]}")

                        attacked_squares = board.attacks(square)
                        attacked_pieces = [(chess.square_name(sq), board.piece_at(sq)) for sq in attacked_squares if
                                           board.piece_at(sq)]

                        if attacked_pieces:
                            print(f"Заплашени фигури от {board.piece_at(square)}: {attacked_pieces}")
                        else:
                            print(f"{board.piece_at(square)} не заплашва никоя фигура.")
                else:
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        board.push(move)
                        print(board)
                        history_of_moves.add_move_in_history(board)
                    selected_square = None

    draw_board()
    draw_pieces()
    draw_button()
    pygame.display.flip()

pygame.quit()
