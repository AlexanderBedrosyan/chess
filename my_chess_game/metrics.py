import pygame


class DisplayMetrix:
    """
    Board size and additional params for drawing
    """

    SQUARE_SIZE = 80
    BOARD_SIZE = SQUARE_SIZE * 8
    EXTRA_SPACE = 40
    WIDTH, HEIGHT = BOARD_SIZE + EXTRA_SPACE, BOARD_SIZE + EXTRA_SPACE
    NAME_OF_THE_BOARD = "Lokomotiv Plovdiv Chess Game"
    PIECE_IMAGES = {}
    PIECE_SYMBOLS = ['r', 'n', 'b', 'q', 'k', 'p', 'wR', 'wN', 'wB', 'wQ', 'wK', 'wP']
    SCALED_SIZE = int(SQUARE_SIZE * 0.85)

    def transform_symbols_into_image(self):
        for symbol in self.PIECE_SYMBOLS:
            self.PIECE_IMAGES[symbol] = pygame.transform.scale(
                pygame.image.load(f"pieces/{symbol}.svg"), (self.SCALED_SIZE, self.SCALED_SIZE)
            )