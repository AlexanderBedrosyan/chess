from __future__ import annotations
from typing import Optional
import pygame


# ─────────────────────────────────────────────
# Colour palette – modern dark chess trainer
# ─────────────────────────────────────────────
class Colors:
    # Backgrounds
    BG           = (13,  15,  22)
    PANEL        = (20,  23,  35)
    PANEL_BORDER = (38,  44,  60)
    PANEL_SECTION= (28,  32,  46)

    # Board squares (classic wood)
    LIGHT_SQ     = (240, 217, 181)
    DARK_SQ      = (181, 136,  99)
    HIGHLIGHT_SQ = (105, 185, 105, 160)   # legal-move target
    SELECTED_SQ  = ( 80, 160, 130, 200)   # selected piece
    LAST_MOVE    = (200, 180,  60, 100)   # last-move tint
    SUGGEST_ARROW= ( 80, 160, 255)        # best-move arrow
    DRAW_ARROW   = (255, 255, 255)        # user-drawn arrows

    # Evaluation bar
    EVAL_WHITE   = (245, 245, 245)
    EVAL_BLACK   = ( 18,  20,  26)

    # Text
    TEXT_PRIMARY = (230, 233, 240)
    TEXT_SECOND  = (140, 148, 168)
    TEXT_DARK    = ( 50,  55,  68)

    # Buttons
    BTN          = ( 38,  44,  62)
    BTN_HOVER    = ( 55,  64,  90)
    BTN_ACTIVE   = ( 88, 166, 255)
    BTN_DANGER   = (180,  55,  55)
    BTN_TEXT     = (220, 225, 235)

    # Move quality colours
    BEST         = ( 90, 215, 130)
    EXCELLENT    = (110, 200, 140)
    GOOD         = (150, 200, 100)
    INACCURACY   = (240, 185,  60)
    MISTAKE      = (230, 130,  50)
    BLUNDER      = (210,  55,  55)


# ─────────────────────────────────────────────
# Dynamic Layout – recomputed on every resize
# ─────────────────────────────────────────────
class Layout:
    EVAL_BAR_W  = 16
    COORD_W     = 22
    COORD_H     = 22
    H_PAD       = 10
    V_PAD       = 10
    MIN_PANEL_W = 260
    MAX_PANEL_W = 370
    NAME        = "Chess Trainer – Educational"
    PIECE_SYMBOLS = ['r','n','b','q','k','p','wR','wN','wB','wQ','wK','wP']
    LOGO_SIZE   = 48

    def __init__(self, screen_w: int = 1140, screen_h: int = 740):
        self.PIECE_IMAGES: dict = {}
        self.IS_FLIPPED   = False
        self.DRAWING_MODE = False
        self.START_DRAW_POS = None
        self.update(screen_w, screen_h)

    # ── images must be loaded AFTER pygame.init() ──
    def load_images(self):
        for sym in self.PIECE_SYMBOLS:
            raw = pygame.image.load(f"pieces/{sym}.svg").convert_alpha()
            self.PIECE_IMAGES[sym] = pygame.transform.smoothscale(
                raw, (self.piece_px, self.piece_px)
            )

    def update(self, screen_w: int, screen_h: int):
        sw, sh = screen_w, screen_h
        self.screen_w = sw
        self.screen_h = sh

        # Panel
        panel_w = max(self.MIN_PANEL_W, min(self.MAX_PANEL_W, int(sw * 0.28)))
        self.panel_w = panel_w

        # Board
        avail_w = sw - panel_w - self.H_PAD * 4 - self.EVAL_BAR_W - self.COORD_W
        avail_h = sh - self.V_PAD * 2 - self.COORD_H - 40   # 40 for player label rows
        bp = min(avail_w, avail_h)
        bp = max(240, bp)
        bp = (bp // 8) * 8
        self.board_px = bp
        self.sq       = bp // 8
        self.piece_px = int(self.sq * 0.88)

        # Positions
        self.eval_x  = self.H_PAD
        self.eval_y  = self.V_PAD + 40          # below black-player label
        self.eval_h  = bp

        self.board_x = self.H_PAD + self.EVAL_BAR_W + self.COORD_W
        self.board_y = self.V_PAD + 40

        self.panel_x = sw - panel_w - self.H_PAD
        self.panel_y = 0
        self.panel_h = sh

        # ── buttons (from bottom up) ──
        bx = self.panel_x + 10
        bw = panel_w - 20
        bh = 36
        by = sh - 10

        self.btn_undo    = pygame.Rect(bx,               by - bh,       bw // 2 - 4, bh)
        self.btn_flip    = pygame.Rect(bx + bw // 2 + 4, by - bh,       bw // 2 - 4, bh)
        by -= bh + 8

        self.btn_draw    = pygame.Rect(bx,               by - bh,       bw // 2 - 4, bh)
        self.btn_evaluate= pygame.Rect(bx + bw // 2 + 4, by - bh,       bw // 2 - 4, bh)
        by -= bh + 8

        self.btn_suggest = pygame.Rect(bx,               by - bh,       bw,          bh)
        by -= bh + 8

        self.btn_history = pygame.Rect(bx,               by - bh,       bw,          bh)
        by -= bh + 8

        self.btn_newgame = pygame.Rect(bx,               by - bh,       bw,          bh)
        by -= bh + 16

        # ── sub-regions inside panel ──
        self.black_bar_rect = pygame.Rect(self.panel_x, 0,       panel_w, 44)
        self.white_bar_rect = pygame.Rect(self.panel_x, sh - 44, panel_w, 44)

        hist_top = self.black_bar_rect.bottom + 6
        hist_bot = self.btn_newgame.top - 10
        self.history_rect = pygame.Rect(
            self.panel_x + 8, hist_top,
            panel_w - 16, max(40, hist_bot - hist_top)
        )

    # ── state toggles ──
    def toggle_flip(self):
        self.IS_FLIPPED = not self.IS_FLIPPED

    def toggle_draw(self):
        self.DRAWING_MODE = not self.DRAWING_MODE
        if not self.DRAWING_MODE:
            self.START_DRAW_POS = None


# ─────────────────────────────────────────────
# Move history for the current game
# ─────────────────────────────────────────────
class HistoryOfMoves:
    """Tracks SAN moves + quality labels for the current game."""

    QUALITY_MAP = [
        (  0, "Best",       Colors.BEST),
        ( 10, "Excellent",  Colors.EXCELLENT),
        ( 25, "Good",       Colors.GOOD),
        ( 50, "Inaccuracy", Colors.INACCURACY),
        (100, "Mistake",    Colors.MISTAKE),
        (9999,"Blunder",    Colors.BLUNDER),
    ]

    def __init__(self):
        self.moves: list  = []   # list of (san: str, quality_label: str, quality_color: tuple)
        self.arrows: list = []   # user-drawn arrows [(start_pos, end_pos)]
        self.scroll_offset = 0

    def add_move(self, san: str, cp_loss: Optional[int] = None):
        if cp_loss is None:
            label, color = "", Colors.TEXT_SECOND
        else:
            label, color = self._classify(cp_loss)
        self.moves.append((san, label, color))

    def undo(self, board):
        if self.moves:
            self.moves.pop()
        if len(board.move_stack) > 0:
            board.pop()

    def reset(self):
        self.moves.clear()
        self.arrows.clear()
        self.scroll_offset = 0

    def _classify(self, cp_loss: int):
        for threshold, label, color in self.QUALITY_MAP:
            if cp_loss <= threshold:
                return label, color
        return "Blunder", Colors.BLUNDER