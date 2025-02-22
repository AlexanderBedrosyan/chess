import pygame
import chess
import math
from metrics import DisplayMetrics, HistoryOfMoves

# pygame.init()
#
# display_board = DisplayMetrics()
# display_board.transform_symbols_into_image()
# logo_image = pygame.image.load("pieces/chess-logo.png")
#
# logo_image = pygame.transform.scale(logo_image, (display_board.LOGO_SIZE, display_board.LOGO_SIZE))
# pygame.display.set_icon(logo_image)
#
# history_of_moves = HistoryOfMoves()
#
# # Desk starting
# board = chess.Board()
# screen = pygame.display.set_mode((display_board.WIDTH + 50, display_board.HEIGHT), pygame.RESIZABLE)
# pygame.display.set_caption(display_board.NAME_OF_THE_BOARD)
#
#
# def draw_board():
#     colors = [pygame.Color(display_board.FIRST_COLOR), pygame.Color(display_board.SECOND_COLOR)]
#     font = pygame.font.Font(None, display_board.FONT_SIZE)
#
#     screen.fill(display_board.ADDITIONAL_COLOR)  # Grey background
#
#     for row in range(8):
#         for col in range(8):
#             color = colors[(row + col) % 2]
#             pygame.draw.rect(screen, color, pygame.Rect(
#                 col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE, row * display_board.SQUARE_SIZE,
#                 display_board.SQUARE_SIZE, display_board.SQUARE_SIZE
#             ))
#
#     for row in range(8):
#         num = str(8 - row) if not display_board.IS_FLIPPED else str(row + 1)
#         text = font.render(num, True, pygame.Color(display_board.LETTERS_AND_DIGITS_COLOR))
#         screen.blit(text, (10, row * display_board.SQUARE_SIZE + display_board.SQUARE_SIZE // 3))
#
#     for col in range(8):
#         letter = chr(65 + col) if not display_board.IS_FLIPPED else chr(65 + (7 - col))
#         text = font.render(letter, True, pygame.Color(display_board.LETTERS_AND_DIGITS_COLOR))
#         screen.blit(text, (
#             col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + display_board.SQUARE_SIZE // 3,
#             display_board.HEIGHT - 80
#         ))
#
#
# def draw_arrow(start, end, color="white", thickness=2):
#     arrow_size = display_board.SQUARE_SIZE // 5
#     start = (int(start[0]), int(start[1]))
#     end = (int(end[0]), int(end[1]))
#
#     pygame.draw.line(screen, pygame.Color(color), start, end, thickness)
#
#     dx = end[0] - start[0]
#     dy = end[1] - start[1]
#     angle = math.atan2(dy, dx)
#
#     arrow_p1 = (end[0] - arrow_size * math.cos(angle - math.pi / 6),
#                 end[1] - arrow_size * math.sin(angle - math.pi / 6))
#
#     arrow_p2 = (end[0] - arrow_size * math.cos(angle + math.pi / 6),
#                 end[1] - arrow_size * math.sin(angle + math.pi / 6))
#
#     pygame.draw.polygon(screen, pygame.Color(color), [end, arrow_p1, arrow_p2])
#
#
# def draw_arrows():
#     if history_of_moves.arrows:
#         for start, end in history_of_moves.arrows:
#             draw_arrow(start, end, color="white", thickness=2)
#
#
# def draw_button():
#     mouse_x, mouse_y = pygame.mouse.get_pos()
#
#     if display_board.UNDO_BUTTON.collidepoint(mouse_x, mouse_y):
#         color = pygame.Color("darkgray")
#     else:
#         color = pygame.Color("gray")
#
#     pygame.draw.rect(screen, color, display_board.UNDO_BUTTON, border_radius=30)
#     undo_text = pygame.font.Font(None, 30).render("Undo", True, pygame.Color("white"))
#     text_rect = undo_text.get_rect(center=display_board.UNDO_BUTTON.center)
#     screen.blit(undo_text, text_rect)
#
#     flip_color = pygame.Color("darkgray") if display_board.FLIP_BUTTON.collidepoint(mouse_x, mouse_y) else pygame.Color(
#         "gray")
#     pygame.draw.rect(screen, flip_color, display_board.FLIP_BUTTON, border_radius=30)
#     flip_text = pygame.font.Font(None, 30).render("Flip Board", True, pygame.Color("white"))
#     screen.blit(flip_text, flip_text.get_rect(center=display_board.FLIP_BUTTON.center))
#
#     draw_color = pygame.Color("darkgray") if display_board.DRAW_BUTTON.collidepoint(mouse_x, mouse_y) else pygame.Color(
#         "gray")
#     pygame.draw.rect(screen, draw_color, display_board.DRAW_BUTTON, border_radius=30)
#     draw_text = pygame.font.Font(None, 30).render("Draw", True, pygame.Color("white"))
#     screen.blit(draw_text, draw_text.get_rect(center=display_board.DRAW_BUTTON.center))
#
#
# def draw_message(message, color="red"):
#     font = pygame.font.Font(None, 50)
#     text = font.render(message, True, pygame.Color(color))
#     text_rect = text.get_rect(center=(display_board.WIDTH - 70, 20))
#     screen.blit(text, text_rect)
#
#
# # Drawing the pieces
# def draw_pieces():
#     offset = (display_board.SQUARE_SIZE - display_board.SCALED_SIZE) // 2
#
#     for square in chess.SQUARES:
#         piece = board.piece_at(square)
#         if piece:
#             row, col = divmod(square, 8)
#
#             if display_board.IS_FLIPPED:
#                 row = 7 - row
#                 col = 7 - col
#
#             symbol = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE else piece.symbol()
#
#             screen.blit(display_board.PIECE_IMAGES[symbol], (
#                 col * display_board.SQUARE_SIZE + display_board.EXTRA_SPACE + offset,
#                 (7 - row) * display_board.SQUARE_SIZE + offset
#             ))
#
#
# # Main loop
# running = True
# selected_square = None
#
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#
#         elif event.type == pygame.MOUSEBUTTONDOWN:
#             x, y = event.pos
#             col = (x - display_board.EXTRA_SPACE) // display_board.SQUARE_SIZE
#             row = 7 - (y // display_board.SQUARE_SIZE)
#
#             if display_board.DRAW_BUTTON.collidepoint(x, y):
#                 display_board.drawing_on_board()
#                 history_of_moves.arrows = []
#             elif display_board.DRAWING_MODE:
#                 display_board.START_DRAW_POSITION = event.pos
#
#             if display_board.UNDO_BUTTON.collidepoint(x, y):
#                 history_of_moves.undo_last_move(board)
#
#             elif display_board.FLIP_BUTTON.collidepoint(x, y):
#                 display_board.board_flip()
#
#             if display_board.IS_FLIPPED:
#                 col = 7 - col
#                 row = 7 - row
#
#             if 0 <= col < 8 and 0 <= row < 8:
#                 square = chess.square(col, row)
#
#                 if selected_square is None:
#                     if board.piece_at(square):
#                         selected_square = square
#                         legal_moves = [move for move in board.legal_moves if move.from_square == square]
#                         print(f"Позволени ходове за {board.piece_at(square)}: {[board.san(m) for m in legal_moves]}")
#
#                         attacked_squares = board.attacks(square)
#                         attacked_pieces = [(chess.square_name(sq), board.piece_at(sq)) for sq in attacked_squares if
#                                            board.piece_at(sq)]
#
#                         if attacked_pieces:
#                             print(f"Заплашени фигури от {board.piece_at(square)}: {attacked_pieces}")
#                         else:
#                             print(f"{board.piece_at(square)} не заплашва никоя фигура.")
#                 else:
#                     move = chess.Move(selected_square, square)
#                     if move in board.legal_moves:
#                         board.push(move)
#                         print(board)
#                         history_of_moves.add_move_in_history(board)
#                     selected_square = None
#
#         elif event.type == pygame.MOUSEBUTTONUP and display_board.DRAWING_MODE:
#             if display_board.START_DRAW_POSITION:
#                 end_pos = event.pos
#                 history_of_moves.arrows.append((display_board.START_DRAW_POSITION, end_pos))
#                 display_board.START_DRAW_POSITION = None
#
#         elif event.type == pygame.MOUSEBUTTONUP and display_board.DRAWING_MODE:
#             display_board.START_DRAW_POSITION = None
#
#
#     draw_board()
#     draw_pieces()
#     draw_button()
#     draw_arrows()
#
#     if board.is_checkmate():
#         draw_message("Checkmate!", "red")
#     elif board.is_check():
#         draw_message("Check!", "orange")
#
#     pygame.display.flip()
#
# pygame.quit()


class Chess(DisplayMetrics, HistoryOfMoves):

    display_board = DisplayMetrics()
    display_board.transform_symbols_into_image()
    logo_image = pygame.image.load("pieces/chess-logo.png")

    logo_image = pygame.transform.scale(logo_image, (display_board.LOGO_SIZE, display_board.LOGO_SIZE))
    pygame.display.set_icon(logo_image)

    history_of_moves = HistoryOfMoves()
    # Desk starting
    board = chess.Board()
    screen = pygame.display.set_mode((display_board.WIDTH + 50, display_board.HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption(display_board.NAME_OF_THE_BOARD)

    def draw_board(self):
        colors = [pygame.Color(self.display_board.FIRST_COLOR), pygame.Color(self.display_board.SECOND_COLOR)]
        font = pygame.font.Font(None, self.display_board.FONT_SIZE)

        self.screen.fill(self.display_board.ADDITIONAL_COLOR)  # Grey background

        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(
                    col * self.display_board.SQUARE_SIZE + self.display_board.EXTRA_SPACE, row * self.display_board.SQUARE_SIZE,
                    self.display_board.SQUARE_SIZE, self.display_board.SQUARE_SIZE
                ))

        for row in range(8):
            num = str(8 - row) if not self.display_board.IS_FLIPPED else str(row + 1)
            text = font.render(num, True, pygame.Color(self.display_board.LETTERS_AND_DIGITS_COLOR))
            self.screen.blit(text, (10, row * self.display_board.SQUARE_SIZE + self.display_board.SQUARE_SIZE // 3))

        for col in range(8):
            letter = chr(65 + col) if not self.display_board.IS_FLIPPED else chr(65 + (7 - col))
            text = font.render(letter, True, pygame.Color(self.display_board.LETTERS_AND_DIGITS_COLOR))
            self.screen.blit(text, (
                col * self.display_board.SQUARE_SIZE + self.display_board.EXTRA_SPACE + self.display_board.SQUARE_SIZE // 3,
                self.display_board.HEIGHT - 80
            ))

    def draw_arrow(self, start, end, color="white", thickness=2):
        arrow_size = self.display_board.SQUARE_SIZE // 5
        start = (int(start[0]), int(start[1]))
        end = (int(end[0]), int(end[1]))

        pygame.draw.line(self.screen, pygame.Color(color), start, end, thickness)

        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)

        arrow_p1 = (end[0] - arrow_size * math.cos(angle - math.pi / 6),
                    end[1] - arrow_size * math.sin(angle - math.pi / 6))

        arrow_p2 = (end[0] - arrow_size * math.cos(angle + math.pi / 6),
                    end[1] - arrow_size * math.sin(angle + math.pi / 6))

        pygame.draw.polygon(self.screen, pygame.Color(color), [end, arrow_p1, arrow_p2])

    def draw_arrows(self):
        if self.history_of_moves.arrows:
            for start, end in self.history_of_moves.arrows:
                self.draw_arrow(start, end, color="white", thickness=2)

    def draw_button(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.display_board.UNDO_BUTTON.collidepoint(mouse_x, mouse_y):
            color = pygame.Color("darkgray")
        else:
            color = pygame.Color("gray")

        pygame.draw.rect(self.screen, color, self.display_board.UNDO_BUTTON, border_radius=30)
        undo_text = pygame.font.Font(None, 30).render("Undo", True, pygame.Color("white"))
        text_rect = undo_text.get_rect(center=self.display_board.UNDO_BUTTON.center)
        self.screen.blit(undo_text, text_rect)

        flip_color = pygame.Color("darkgray") if self.display_board.FLIP_BUTTON.collidepoint(mouse_x,
                                                                                        mouse_y) else pygame.Color(
            "gray")
        pygame.draw.rect(self.screen, flip_color, self.display_board.FLIP_BUTTON, border_radius=30)
        flip_text = pygame.font.Font(None, 30).render("Flip Board", True, pygame.Color("white"))
        self.screen.blit(flip_text, flip_text.get_rect(center=self.display_board.FLIP_BUTTON.center))

        draw_color = pygame.Color("darkgray") if self.display_board.DRAW_BUTTON.collidepoint(mouse_x,
                                                                                        mouse_y) else pygame.Color(
            "gray")
        pygame.draw.rect(self.screen, draw_color, self.display_board.DRAW_BUTTON, border_radius=30)
        draw_text = pygame.font.Font(None, 30).render("Draw", True, pygame.Color("white"))
        self.screen.blit(draw_text, draw_text.get_rect(center=self.display_board.DRAW_BUTTON.center))

    def draw_message(self, message, color="red"):
        font = pygame.font.Font(None, 50)
        text = font.render(message, True, pygame.Color(color))
        text_rect = text.get_rect(center=(self.display_board.WIDTH - 70, 20))
        self.screen.blit(text, text_rect)

    # Drawing the pieces
    def draw_pieces(self):
        offset = (self.display_board.SQUARE_SIZE - self.display_board.SCALED_SIZE) // 2

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)

                if self.display_board.IS_FLIPPED:
                    row = 7 - row
                    col = 7 - col

                symbol = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE else piece.symbol()

                self.screen.blit(self.display_board.PIECE_IMAGES[symbol], (
                    col * self.display_board.SQUARE_SIZE + self.display_board.EXTRA_SPACE + offset,
                    (7 - row) * self.display_board.SQUARE_SIZE + offset
                ))

    def starting_game(self):
        pygame.init()

        # Main loop
        running = True
        selected_square = None

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    col = (x - self.display_board.EXTRA_SPACE) // self.display_board.SQUARE_SIZE
                    row = 7 - (y // self.display_board.SQUARE_SIZE)

                    if self.display_board.DRAW_BUTTON.collidepoint(x, y):
                        self.display_board.drawing_on_board()
                        self.history_of_moves.arrows = []
                    elif self.display_board.DRAWING_MODE:
                        self.display_board.START_DRAW_POSITION = event.pos

                    if self.display_board.UNDO_BUTTON.collidepoint(x, y):
                        self.history_of_moves.undo_last_move(self.board)

                    elif self.display_board.FLIP_BUTTON.collidepoint(x, y):
                        self.display_board.board_flip()

                    if self.display_board.IS_FLIPPED:
                        col = 7 - col
                        row = 7 - row

                    if 0 <= col < 8 and 0 <= row < 8:
                        square = chess.square(col, row)

                        if selected_square is None:
                            if self.board.piece_at(square):
                                selected_square = square
                                legal_moves = [move for move in self.board.legal_moves if move.from_square == square]
                                print(
                                    f"Позволени ходове за {self.board.piece_at(square)}: {[self.board.san(m) for m in legal_moves]}")

                                attacked_squares = self.board.attacks(square)
                                attacked_pieces = [(chess.square_name(sq), self.board.piece_at(sq)) for sq in attacked_squares if
                                                   self.board.piece_at(sq)]

                                if attacked_pieces:
                                    print(f"Заплашени фигури от {self.board.piece_at(square)}: {attacked_pieces}")
                                else:
                                    print(f"{self.board.piece_at(square)} не заплашва никоя фигура.")
                        else:
                            move = chess.Move(selected_square, square)
                            if move in self.board.legal_moves:
                                self.board.push(move)
                                print(self.board)
                                self.history_of_moves.add_move_in_history(self.board)
                            selected_square = None

                elif event.type == pygame.MOUSEBUTTONUP and self.display_board.DRAWING_MODE:
                    if self.display_board.START_DRAW_POSITION:
                        end_pos = event.pos
                        self.history_of_moves.arrows.append((self.display_board.START_DRAW_POSITION, end_pos))
                        self.display_board.START_DRAW_POSITION = None

                elif event.type == pygame.MOUSEBUTTONUP and self.display_board.DRAWING_MODE:
                    self.display_board.START_DRAW_POSITION = None

            self.draw_board()
            self.draw_pieces()
            self.draw_button()
            self.draw_arrows()

            if self.board.is_checkmate():
                self.draw_message("Checkmate!", "red")
            elif self.board.is_check():
                self.draw_message("Check!", "orange")

            pygame.display.flip()

        pygame.quit()


game = Chess()

game.starting_game()