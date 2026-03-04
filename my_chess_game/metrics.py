from __future__ import annotations
from typing import Optional
import os, sys
import pygame


def _resource_path(relative: str) -> str:
    """Resolve path to a bundled resource (dev or frozen exe)."""
    base = getattr(sys, "_MEIPASS",
                   os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


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
    # No separate left-side eval bar – coords live inside squares now
    PLAYER_BAR_H = 44
    H_PAD        = 12
    V_PAD        = 8
    MIN_PANEL_W  = 270
    MAX_PANEL_W  = 380
    NAME         = "Chess Trainer – Educational"
    PIECE_SYMBOLS = ['r','n','b','q','k','p','wR','wN','wB','wQ','wK','wP']
    LOGO_SIZE    = 48

    def __init__(self, screen_w: int = 1440, screen_h: int = 900):
        self.PIECE_IMAGES: dict = {}
        self.IS_FLIPPED    = False
        self.DRAWING_MODE  = False
        self.START_DRAW_POS = None
        self.update(screen_w, screen_h)

    # ── images must be loaded AFTER pygame.init() ──
    def load_images(self):
        for sym in self.PIECE_SYMBOLS:
            path = _resource_path(os.path.join("pieces", f"{sym}.svg"))
            raw = pygame.image.load(path).convert_alpha()
            self.PIECE_IMAGES[sym] = pygame.transform.smoothscale(
                raw, (self.piece_px, self.piece_px)
            )

    def update(self, screen_w: int, screen_h: int):
        sw, sh = screen_w, screen_h
        self.screen_w = sw
        self.screen_h = sh

        # Panel – right side
        panel_w = max(self.MIN_PANEL_W, min(self.MAX_PANEL_W, int(sw * 0.26)))
        self.panel_w  = panel_w
        self.panel_x  = sw - panel_w
        self.panel_y  = 0
        self.panel_h  = sh

        # Board – centered in the space left of the panel
        area_x1 = self.H_PAD
        area_x2 = self.panel_x - self.H_PAD
        area_y1 = self.PLAYER_BAR_H + self.V_PAD
        area_y2 = sh - self.PLAYER_BAR_H - self.V_PAD

        avail_w = area_x2 - area_x1
        avail_h = area_y2 - area_y1
        bp = min(avail_w, avail_h)
        bp = max(240, bp)
        bp = (bp // 8) * 8
        self.board_px = bp
        self.sq       = bp // 8
        self.piece_px = int(self.sq * 0.88)

        # Centre the board in the available area
        self.board_x = area_x1 + (avail_w - bp) // 2
        self.board_y = area_y1 + (avail_h - bp) // 2

        # ── buttons (from bottom up) ──
        bx = self.panel_x + 10
        bw = panel_w - 20
        bh = max(34, min(42, sh // 20))
        by = sh - 10

        self.btn_undo    = pygame.Rect(bx,               by - bh,       bw // 2 - 4, bh)
        self.btn_flip    = pygame.Rect(bx + bw // 2 + 4, by - bh,       bw // 2 - 4, bh)
        by -= bh + 6

        self.btn_draw    = pygame.Rect(bx,               by - bh,       bw // 2 - 4, bh)
        self.btn_evaluate= pygame.Rect(bx + bw // 2 + 4, by - bh,       bw // 2 - 4, bh)
        by -= bh + 6

        self.btn_suggest = pygame.Rect(bx,               by - bh,       bw,          bh)
        by -= bh + 6

        self.btn_history = pygame.Rect(bx,               by - bh,       bw,          bh)
        by -= bh + 6

        self.btn_newgame = pygame.Rect(bx,               by - bh,       bw,          bh)
        by -= bh + 14

        # ── player name bars (full width) ──
        self.black_bar_rect = pygame.Rect(0, 0,       sw, self.PLAYER_BAR_H)
        self.white_bar_rect = pygame.Rect(0, sh - self.PLAYER_BAR_H, sw, self.PLAYER_BAR_H)

        # ── eval bar (horizontal, inside panel, below black bar) ──
        eval_bar_h = max(10, min(16, sh // 55))
        eval_top   = self.PLAYER_BAR_H + 6
        self.eval_bar_rect = pygame.Rect(self.panel_x + 8, eval_top, panel_w - 16, eval_bar_h)

        # ── move history ──
        hist_top = self.eval_bar_rect.bottom + 28
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