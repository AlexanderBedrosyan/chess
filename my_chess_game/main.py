import pygame
import chess
import math
from metrics import DisplayMetrics, HistoryOfMoves
import chess.engine
import os


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

    def evaluate_position(self, board):
        stockfish_path = os.path.join(os.getcwd(), "stockfish", "stockfish/stockfish-windows-x86-64-avx2.exe")
        with chess.engine.SimpleEngine.popen_uci(stockfish_path) as engine:
            info = engine.analyse(board, chess.engine.Limit(time=0.5))
            score = info["score"].relative.score(mate_score=10000)
            return score

    def convert_score_to_percentage(self, score):
        if score is None:
            return 50, 50

        if score > 0:
            white_percentage = 50 + score / 100
            black_percentage = 50 - score / 100
        else:
            white_percentage = 50 - abs(score) / 100
            black_percentage = 50 + abs(score) / 100

        return white_percentage, black_percentage

    def draw_evaluation_bar(self, board):
        current_score = self.evaluate_position(board)

        white_percentage, black_percentage = self.convert_score_to_percentage(current_score)

        # Можеш да нарисуваш текста на екрана (с Pygame):
        font = pygame.font.SysFont(None, 36)

        white_text = font.render(f"White: {white_percentage:.1f}% chance for win", True, (255, 255, 255))
        black_text = font.render(f"Black: {black_percentage:.1f}% chance for win", True, (0, 0, 0))

        # Разположи текстовете на екрана (напр. горе в ляво):
        self.screen.blit(white_text, (10, 10))
        self.screen.blit(black_text, (10, 50))

        pygame.display.flip()

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

    def show_promotion_menu(self, square, color):
        menu_width = 220
        menu_height = 70
        x = self.display_board.WIDTH // 2 - menu_width // 2
        y = self.display_board.HEIGHT // 2 - menu_height // 2
        promotion_pieces = [
            chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT
        ]

        piece_symbols = ["Q", "R", "B", "N"]
        buttons = []

        for i, piece in enumerate(promotion_pieces):
            rect = pygame.Rect(x + i * 50, y, 50, 50)
            buttons.append((rect, piece))

        while True:
            self.draw_board()
            self.draw_pieces()

            pygame.draw.rect(self.screen, pygame.Color("gray"), (x, y, menu_width, menu_height), border_radius=10)

            for i, (rect, piece) in enumerate(buttons):
                symbol = f"w{piece_symbols[i]}" if color == chess.WHITE else piece_symbols[i]
                if len(symbol) == 1:
                    symbol = symbol.lower()
                self.screen.blit(self.display_board.PIECE_IMAGES[symbol], rect.topleft)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for rect, piece in buttons:
                        if rect.collidepoint(mouse_x, mouse_y):
                            self.board.remove_piece_at(square)
                            self.board.set_piece_at(square, chess.Piece(piece, color))
                            return

    def handle_promotion(self, square, current_piece):
        self.board.remove_piece_at(square)
        if current_piece.symbol() == 'P':
            self.board.set_piece_at(square, chess.Piece(chess.QUEEN, chess.WHITE))
        else:
            self.board.set_piece_at(square, chess.Piece(chess.QUEEN, chess.BLACK))

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
                                    f"Позволени ходове за {self.board.piece_at(square)}: {[self.board.san(m) for m in legal_moves]}"
                                )

                                attacked_squares = self.board.attacks(square)
                                attacked_pieces = [(chess.square_name(sq), self.board.piece_at(sq)) for sq in attacked_squares if
                                                   self.board.piece_at(sq)]

                                if attacked_pieces:
                                    print(f"Заплашени фигури от {self.board.piece_at(square)}: {attacked_pieces}")
                                else:
                                    print(f"{self.board.piece_at(square)} не заплашва никоя фигура.")

                        else:
                            move = chess.Move(selected_square, square)
                            if move.to_square // 8 == 0 or move.to_square // 8 == 7:
                                self.board.push(move)
                                piece = self.board.piece_at(square)

                                if piece and piece.symbol() in ('p', 'P'):
                                    self.show_promotion_menu(move.to_square, piece.color)
                                    # self.handle_promotion(square, current_pieces)

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
            self.draw_evaluation_bar(self.board)

            if self.board.is_checkmate():
                self.draw_message("Checkmate!", "red")
            elif self.board.is_check():
                self.draw_message("Check!", "orange")

            pygame.display.flip()

        pygame.quit()


game = Chess()
game.starting_game()
