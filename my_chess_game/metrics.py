import pygame


class DisplayMetrics:
    """
    Board size and additional params for drawing
    """

    EXTRA_SPACE = 40
    INFO_PANEL_WIDTH = 200
    WIDTH, HEIGHT = 800, 700
    BOARD_SIZE = HEIGHT if HEIGHT < WIDTH - INFO_PANEL_WIDTH else WIDTH - INFO_PANEL_WIDTH
    SQUARE_SIZE = BOARD_SIZE // 8
    UNDO_BUTTON = pygame.Rect(WIDTH - INFO_PANEL_WIDTH + 50, 50, 160, 40)
    PEN_BUTTON = pygame.Rect(WIDTH - INFO_PANEL_WIDTH + 20, 110, 160, 40)
    CHAT_BOX = pygame.Rect(WIDTH - INFO_PANEL_WIDTH + 20, 180, 160, 400)
    NAME_OF_THE_BOARD = "Lokomotiv Plovdiv Chess Game"
    PIECE_IMAGES = {}
    PIECE_SYMBOLS = ['r', 'n', 'b', 'q', 'k', 'p', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    SCALED_SIZE = int(SQUARE_SIZE * 0.85)
    FONT_SIZE = 30
    FIRST_COLOR = "#D2B48C"
    SECOND_COLOR = "#8B4513"
    ADDITIONAL_COLOR = (50, 50, 50)
    LETTERS_AND_DIGITS_COLOR = "white"
    FLIP_BUTTON = pygame.Rect(WIDTH - INFO_PANEL_WIDTH + 50, 100, 160, 40)
    DRAW_BUTTON = pygame.Rect(WIDTH - INFO_PANEL_WIDTH + 50, 150, 160, 40)
    IS_FLIPPED = False
    DRAWING_MODE = False
    START_DRAW_POSITION = None
    LOGO_SIZE = 50

    def transform_symbols_into_image(self):
        for symbol in self.PIECE_SYMBOLS:
            self.PIECE_IMAGES[symbol] = pygame.transform.scale(
                pygame.image.load(f"pieces/{symbol}.svg"), (self.SCALED_SIZE, self.SCALED_SIZE)
            )

    def board_flip(self):
        if self.IS_FLIPPED:
            self.IS_FLIPPED = False
            return
        self.IS_FLIPPED = True

    def drawing_on_board(self):
        if self.DRAWING_MODE:
            self.DRAWING_MODE = False
            return
        self.DRAWING_MODE = True


class HistoryOfMoves:

    def __init__(self):
        self.history = []
        self.arrows = []

    def add_move_in_history(self, last_move):
        self.history.append(last_move)

    def undo_last_move(self, current_board):
        if self.history:
            self.history.pop()
            current_board.pop()

    def add_new_arrow(self, current_tuple):
        self.arrows.append(current_tuple)