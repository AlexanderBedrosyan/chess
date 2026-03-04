"""
Chess Trainer – Educational Chess Application
Modern dark UI with position evaluation, move history, and move-quality feedback.
"""
from __future__ import annotations

import math
import os
import threading
from typing import Optional

import chess
import chess.engine
import chess.pgn
import pygame

from history_of_games import HistoryOfGames
from metrics import Colors, HistoryOfMoves, Layout

# ─────────────────────────────────────────────────────────────
# Path to Stockfish
# ─────────────────────────────────────────────────────────────
STOCKFISH_PATH = os.path.join(
    os.getcwd(), "stockfish", "stockfish",
    "stockfish-windows-x86-64-avx2.exe"
)


# ─────────────────────────────────────────────────────────────
# Helper: rounded-rectangle surface
# ─────────────────────────────────────────────────────────────
def draw_rounded_rect(surface: pygame.Surface, color, rect: pygame.Rect,
                      radius: int = 8, alpha: int = 255):
    s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    c = (*color[:3], alpha)
    pygame.draw.rect(s, c, s.get_rect(), border_radius=radius)
    surface.blit(s, rect.topleft)


# ─────────────────────────────────────────────────────────────
# Main application
# ─────────────────────────────────────────────────────────────
class ChessTrainer:

    # ── stockfish analysis time limits ──
    FAST_LIMIT  = chess.engine.Limit(time=0.15)
    DEEP_LIMIT  = chess.engine.Limit(time=0.50)

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Chess Trainer")

        try:
            logo = pygame.image.load("pieces/chess-logo.png")
            pygame.display.set_icon(
                pygame.transform.smoothscale(logo, (48, 48))
            )
        except Exception:
            pass

        self.ly = Layout(1140, 740)
        self.screen = pygame.display.set_mode(
            (self.ly.screen_w, self.ly.screen_h), pygame.RESIZABLE
        )
        self.ly.load_images()

        # ── game state ──
        self.board          = chess.Board()
        self.hm             = HistoryOfMoves()
        self.hist_games     = HistoryOfGames()
        self.selected_sq: Optional[int] = None
        self.legal_targets: list[int]   = []
        self.last_move: Optional[chess.Move] = None

        # ── evaluation ──
        self.white_pct: float = 50.0
        self.black_pct: float = 50.0
        self.eval_score: Optional[int] = None
        self.show_eval    = False

        # ── move-quality / suggestion ──
        self.last_quality_label = ""
        self.last_quality_color = Colors.TEXT_SECOND
        self.last_cp_loss: Optional[int]     = None
        self.suggest_move: Optional[chess.Move] = None
        self.score_before_move: Optional[int]        = None

        # ── pro-game history overlay ──
        self.pro_games_lines: list[str] = []
        self.show_pro_games = False

        # ── background analysis thread ──
        self._analysis_lock   = threading.Lock()
        self._analysis_thread: Optional[threading.Thread] = None
        self._pending_result: Optional[dict] = None

        # ── fonts (cached by size) ──
        self._font_cache: dict[int, pygame.font.Font] = {}

        self.clock = pygame.time.Clock()

    # ─── font helper ───────────────────────────────────────
    def font(self, size: int) -> pygame.font.Font:
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.SysFont("segoeui", size)
        return self._font_cache[size]

    # ─── Board ↔ pixel helpers ──────────────────────────────
    def sq_to_pixel(self, sq: int):
        r, c = divmod(sq, 8)
        if self.ly.IS_FLIPPED:
            r, c = 7 - r, 7 - c
        px = self.ly.board_x + c * self.ly.sq
        py = self.ly.board_y + (7 - r) * self.ly.sq
        return px, py

    def pixel_to_sq(self, x: int, y: int) -> Optional[int]:
        col = (x - self.ly.board_x) // self.ly.sq
        row = 7 - (y - self.ly.board_y) // self.ly.sq
        if self.ly.IS_FLIPPED:
            col, row = 7 - col, 7 - row
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, row)
        return None

    def sq_center(self, sq: int):
        px, py = self.sq_to_pixel(sq)
        return px + self.ly.sq // 2, py + self.ly.sq // 2

    # ─── Stockfish helpers ──────────────────────────────────
    def _run_engine(self, board: chess.Board, limit) -> Optional[int]:
        """Return centipawn score (white POV) or None."""
        try:
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as eng:
                info = eng.analyse(board, limit)
                score = info["score"].white()
                if score.is_mate():
                    return 30000 if score.mate() > 0 else -30000
                return score.score()
        except Exception:
            return None

    def _get_best_move(self, board: chess.Board, limit) -> Optional[chess.Move]:
        try:
            with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as eng:
                result = eng.play(board, limit)
                return result.move
        except Exception:
            return None

    def _score_to_pct(self, score: Optional[int]):
        if score is None:
            return 50.0, 50.0
        clamped = max(-1000, min(1000, score))
        w = 50.0 + clamped / 20.0
        w = max(2.0, min(98.0, w))
        return round(w, 1), round(100.0 - w, 1)

    # ── background analysis after a move ────────────────────
    def _analyze_in_background(self, board_before: chess.Board,
                                move_played: chess.Move,
                                score_before: Optional[int]):
        board_after = board_before.copy()
        board_after.push(move_played)
        score_after = self._run_engine(board_after, self.FAST_LIMIT)

        if score_before is not None and score_after is not None:
            if board_before.turn == chess.WHITE:
                cp_loss = score_before - score_after
            else:
                cp_loss = score_after - score_before
            cp_loss = max(0, cp_loss)
        else:
            cp_loss = None

        result = {"score_after": score_after, "cp_loss": cp_loss}
        with self._analysis_lock:
            self._pending_result = result

    def _start_analysis(self, board_before: chess.Board,
                         move_played: chess.Move,
                         score_before: Optional[int]):
        if self._analysis_thread and self._analysis_thread.is_alive():
            return
        t = threading.Thread(
            target=self._analyze_in_background,
            args=(board_before.copy(), move_played, score_before),
            daemon=True
        )
        self._analysis_thread = t
        t.start()

    # ─── Draw helpers ───────────────────────────────────────
    def _draw_text(self, text: str, size: int, color, x: int, y: int,
                   anchor="topleft"):
        surf = self.font(size).render(text, True, color)
        rect = surf.get_rect(**{anchor: (x, y)})
        self.screen.blit(surf, rect)
        return rect

    def _draw_button(self, rect: pygame.Rect, label: str,
                     active: bool = False, danger: bool = False):
        mx, my = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mx, my)
        if danger:
            color = Colors.BTN_DANGER
        elif active:
            color = Colors.BTN_ACTIVE
        elif hovered:
            color = Colors.BTN_HOVER
        else:
            color = Colors.BTN
        draw_rounded_rect(self.screen, color, rect, radius=7)
        self._draw_text(label, max(13, rect.height - 14),
                        Colors.BTN_TEXT, rect.centerx, rect.centery,
                        anchor="center")
        return hovered

    # ─── Main draw routines ─────────────────────────────────
    def _draw_background(self):
        self.screen.fill(Colors.BG)
        panel_rect = pygame.Rect(
            self.ly.panel_x - 2, 0, self.ly.panel_w + self.ly.H_PAD + 2,
            self.ly.screen_h
        )
        draw_rounded_rect(self.screen, Colors.PANEL, panel_rect, radius=0)
        pygame.draw.line(
            self.screen, Colors.PANEL_BORDER,
            (self.ly.panel_x - 2, 0),
            (self.ly.panel_x - 2, self.ly.screen_h), 1
        )

    def _draw_player_bars(self):
        """Top (Black) and bottom (White) player name + win-% bar."""
        ly = self.ly
        bw = ly.panel_w - 20
        bar_h = 7
        bar_x = ly.panel_x + 10
        font_sz = max(13, ly.sq // 5)

        for is_black in (True, False):
            if is_black:
                pr = ly.black_bar_rect
                label = "\u265f Black"
                pct = self.black_pct
                fill_col = Colors.EVAL_BLACK
                bg_col   = Colors.EVAL_WHITE
            else:
                pr = ly.white_bar_rect
                label = "\u2659 White"
                pct = self.white_pct
                fill_col = Colors.EVAL_WHITE
                bg_col   = Colors.EVAL_BLACK

            draw_rounded_rect(self.screen, Colors.PANEL_SECTION, pr, radius=0)
            self._draw_text(label, font_sz, Colors.TEXT_PRIMARY, bar_x, pr.top + 6)
            self._draw_text(f"{pct:.1f}% win", font_sz, Colors.TEXT_SECOND,
                            pr.right - 10, pr.top + 6, anchor="topright")

            bar_y = pr.bottom - bar_h - 4
            bg_bar = pygame.Rect(bar_x, bar_y, bw, bar_h)
            draw_rounded_rect(self.screen, bg_col, bg_bar, radius=3)
            fill_w = int(bw * pct / 100)
            draw_rounded_rect(self.screen, fill_col,
                              pygame.Rect(bar_x, bar_y, fill_w, bar_h), radius=3)

    def _draw_eval_bar(self):
        """Vertical evaluation bar left of the board."""
        ly = self.ly
        bar_rect = pygame.Rect(ly.eval_x, ly.eval_y, ly.EVAL_BAR_W, ly.eval_h)
        draw_rounded_rect(self.screen, Colors.EVAL_BLACK, bar_rect, radius=4)

        fill_h = int(ly.eval_h * self.white_pct / 100)
        fill_rect = pygame.Rect(
            ly.eval_x, ly.eval_y + ly.eval_h - fill_h,
            ly.EVAL_BAR_W, fill_h
        )
        draw_rounded_rect(self.screen, Colors.EVAL_WHITE, fill_rect, radius=4)

        if self.eval_score is not None:
            cp = self.eval_score
            if abs(cp) >= 29000:
                score_txt = "M" + ("+" if cp > 0 else "-")
            elif cp > 0:
                score_txt = f"+{cp/100:.1f}"
            else:
                score_txt = f"{cp/100:.1f}"
            label_y = ly.eval_y + ly.eval_h // 2
            s = self.font(max(10, ly.EVAL_BAR_W - 2)).render(score_txt, True, Colors.TEXT_SECOND)
            r = s.get_rect(centerx=ly.eval_x + ly.EVAL_BAR_W // 2, centery=label_y)
            self.screen.blit(s, r)

    def _draw_board(self):
        """Draw squares, rank/file labels, highlights."""
        ly = self.ly
        colors = [pygame.Color(Colors.LIGHT_SQ), pygame.Color(Colors.DARK_SQ)]

        for sq in chess.SQUARES:
            r, c = divmod(sq, 8)
            if not ly.IS_FLIPPED:
                vr, vc = r, c
            else:
                vr, vc = 7 - r, 7 - c
            px = ly.board_x + vc * ly.sq
            py = ly.board_y + (7 - vr) * ly.sq
            sq_rect = pygame.Rect(px, py, ly.sq, ly.sq)

            pygame.draw.rect(self.screen, colors[(r + c) % 2], sq_rect)

            if self.last_move and sq in (self.last_move.from_square,
                                          self.last_move.to_square):
                s = pygame.Surface((ly.sq, ly.sq), pygame.SRCALPHA)
                s.fill((*Colors.LAST_MOVE[:3], 90))
                self.screen.blit(s, sq_rect.topleft)

            if self.selected_sq == sq:
                s = pygame.Surface((ly.sq, ly.sq), pygame.SRCALPHA)
                s.fill((*Colors.SELECTED_SQ[:3], 170))
                self.screen.blit(s, sq_rect.topleft)

            if sq in self.legal_targets:
                piece_here = self.board.piece_at(sq)
                if piece_here:
                    s = pygame.Surface((ly.sq, ly.sq), pygame.SRCALPHA)
                    s.fill((*Colors.HIGHLIGHT_SQ[:3], 130))
                    self.screen.blit(s, sq_rect.topleft)
                else:
                    cx = px + ly.sq // 2
                    cy = py + ly.sq // 2
                    r_dot = ly.sq // 7
                    dot_s = pygame.Surface((r_dot * 2, r_dot * 2), pygame.SRCALPHA)
                    pygame.draw.circle(dot_s, (*Colors.HIGHLIGHT_SQ[:3], 160),
                                       (r_dot, r_dot), r_dot)
                    self.screen.blit(dot_s, (cx - r_dot, cy - r_dot))

        for rank in range(8):
            num = str(8 - rank) if not ly.IS_FLIPPED else str(rank + 1)
            s = self.font(max(11, ly.sq // 6)).render(num, True, Colors.TEXT_SECOND)
            self.screen.blit(s, (ly.eval_x + ly.EVAL_BAR_W + 2,
                                  ly.board_y + rank * ly.sq + 3))

        for col in range(8):
            letter = chr(65 + col) if not ly.IS_FLIPPED else chr(65 + 7 - col)
            s = self.font(max(11, ly.sq // 6)).render(letter, True, Colors.TEXT_SECOND)
            self.screen.blit(s, (ly.board_x + col * ly.sq + ly.sq // 2 - 5,
                                  ly.board_y + ly.board_px + 3))

    def _draw_pieces(self):
        ly = self.ly
        offset = (ly.sq - ly.piece_px) // 2
        for sq in chess.SQUARES:
            piece = self.board.piece_at(sq)
            if not piece:
                continue
            r, c = divmod(sq, 8)
            if ly.IS_FLIPPED:
                r, c = 7 - r, 7 - c
            sym = f"w{piece.symbol().upper()}" if piece.color == chess.WHITE \
                  else piece.symbol()
            px = ly.board_x + c * ly.sq + offset
            py = ly.board_y + (7 - r) * ly.sq + offset
            self.screen.blit(ly.PIECE_IMAGES[sym], (px, py))

    def _draw_arrow(self, start, end, color, thickness: int = 4):
        start = (int(start[0]), int(start[1]))
        end   = (int(end[0]),   int(end[1]))
        dx, dy = end[0] - start[0], end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        arrow_sz = self.ly.sq // 4
        ux, uy = dx / dist, dy / dist
        line_end = (int(end[0] - ux * arrow_sz * 0.6),
                    int(end[1] - uy * arrow_sz * 0.6))
        pygame.draw.line(self.screen, color, start, line_end, thickness)
        angle = math.atan2(dy, dx)
        p1 = (end[0] - arrow_sz * math.cos(angle - math.pi / 6),
              end[1] - arrow_sz * math.sin(angle - math.pi / 6))
        p2 = (end[0] - arrow_sz * math.cos(angle + math.pi / 6),
              end[1] - arrow_sz * math.sin(angle + math.pi / 6))
        pygame.draw.polygon(self.screen, color, [end, p1, p2])

    def _draw_arrows(self):
        for start, end in self.hm.arrows:
            self._draw_arrow(start, end, Colors.DRAW_ARROW, thickness=3)
        if self.suggest_move:
            s = self.sq_center(self.suggest_move.from_square)
            e = self.sq_center(self.suggest_move.to_square)
            self._draw_arrow(s, e, Colors.SUGGEST_ARROW, thickness=5)

    def _draw_move_history(self):
        """Render numbered move list inside the right panel."""
        ly = self.ly
        rect = ly.history_rect
        if rect.height < 20:
            return

        self._draw_text("MOVE HISTORY", max(11, ly.sq // 6),
                        Colors.TEXT_SECOND, rect.x, rect.y - 20)
        pygame.draw.line(self.screen, Colors.PANEL_BORDER,
                         (rect.x, rect.y), (rect.right, rect.y), 1)

        moves = self.hm.moves
        if not moves:
            self._draw_text("No moves yet", max(12, ly.sq // 6),
                            Colors.TEXT_SECOND, rect.x + 4, rect.y + 6)
            return

        font_sz = max(12, min(15, ly.sq // 5))
        line_h  = font_sz + 6
        visible = rect.height // line_h

        pairs = []
        for i in range(0, len(moves), 2):
            w_san, w_lbl, w_col = moves[i]
            if i + 1 < len(moves):
                b_san, b_lbl, b_col = moves[i + 1]
            else:
                b_san, b_lbl, b_col = "...", "", Colors.TEXT_SECOND
            pairs.append((i // 2 + 1, w_san, w_lbl, w_col, b_san, b_lbl, b_col))

        total_lines = len(pairs)
        max_scroll = max(0, total_lines - visible)
        self.hm.scroll_offset = max_scroll
        visible_pairs = pairs[self.hm.scroll_offset:self.hm.scroll_offset + visible + 1]

        for idx, (num, ws, wl, wc, bs, bl, bc) in enumerate(visible_pairs):
            y = rect.y + idx * line_h + 4
            self._draw_text(f"{num}.", font_sz, Colors.TEXT_SECOND, rect.x + 2, y)

            wx = rect.x + 26
            w_surf = self.font(font_sz).render(ws, True, Colors.TEXT_PRIMARY)
            self.screen.blit(w_surf, (wx, y))
            if wl:
                badge = self.font(max(9, font_sz - 3)).render(wl[:3], True, wc)
                self.screen.blit(badge, (wx + w_surf.get_width() + 3, y + 2))

            bx2 = rect.x + rect.width // 2
            b_surf = self.font(font_sz).render(bs, True, Colors.TEXT_PRIMARY)
            self.screen.blit(b_surf, (bx2, y))
            if bl:
                badge = self.font(max(9, font_sz - 3)).render(bl[:3], True, bc)
                self.screen.blit(badge, (bx2 + b_surf.get_width() + 3, y + 2))

        if total_lines > visible:
            sb_x = rect.right - 6
            sb_h = rect.height
            thumb_h = max(20, int(sb_h * visible / total_lines))
            thumb_y = rect.y + int((sb_h - thumb_h) * self.hm.scroll_offset / max(1, max_scroll))
            pygame.draw.rect(self.screen, Colors.PANEL_BORDER,
                             pygame.Rect(sb_x, rect.y, 4, sb_h), border_radius=2)
            pygame.draw.rect(self.screen, Colors.TEXT_SECOND,
                             pygame.Rect(sb_x, thumb_y, 4, thumb_h), border_radius=2)

    def _draw_move_quality(self):
        if not self.last_quality_label:
            return
        ly = self.ly
        font_sz = max(12, ly.sq // 5)
        y = ly.history_rect.bottom + 6
        if y + font_sz + 4 > ly.btn_newgame.top - 4:
            return
        label = f"Last move: {self.last_quality_label}"
        if self.last_cp_loss is not None:
            label += f"  (\u2212{self.last_cp_loss} cp)"
        self._draw_text(label, font_sz, self.last_quality_color, ly.panel_x + 10, y)

    def _draw_buttons(self):
        ly = self.ly
        self._draw_button(ly.btn_newgame,  "New Game", danger=True)
        self._draw_button(ly.btn_history,  "Pro Games \U0001f50d")
        self._draw_button(ly.btn_suggest,  "Suggest Best Move")
        self._draw_button(ly.btn_draw,     "Draw", active=ly.DRAWING_MODE)
        self._draw_button(ly.btn_evaluate, "Evaluate", active=self.show_eval)
        self._draw_button(ly.btn_undo,     "\u27f5 Undo")
        self._draw_button(ly.btn_flip,     "\u21c5 Flip")

    def _draw_pro_games_overlay(self):
        ov = pygame.Surface((self.ly.screen_w, self.ly.screen_h), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        self.screen.blit(ov, (0, 0))

        box_w, box_h = 660, 420
        bx = self.ly.screen_w // 2 - box_w // 2
        by = self.ly.screen_h // 2 - box_h // 2
        draw_rounded_rect(self.screen, Colors.PANEL,
                          pygame.Rect(bx, by, box_w, box_h), radius=12)
        pygame.draw.rect(self.screen, Colors.PANEL_BORDER,
                         pygame.Rect(bx, by, box_w, box_h), 2, border_radius=12)

        self._draw_text("Players who reached this position", 18,
                        Colors.TEXT_SECOND, bx + 20, by + 14)
        self._draw_text("\u2715  Click anywhere to close", 13,
                        Colors.TEXT_SECOND, bx + box_w - 20, by + 14, anchor="topright")

        if not self.pro_games_lines:
            self._draw_text("No matching pro games found.", 15,
                            Colors.TEXT_SECOND, bx + box_w // 2, by + box_h // 2,
                            anchor="center")
        else:
            y = by + 44
            for line in self.pro_games_lines[:14]:
                self._draw_text(line, 14, Colors.TEXT_PRIMARY, bx + 20, y)
                y += 26

    def _draw_status(self):
        ly = self.ly
        y = ly.V_PAD + 10
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn == chess.WHITE else "White"
            msg, col = f"\u265a Checkmate! {winner} wins", Colors.BLUNDER
        elif self.board.is_stalemate():
            msg, col = "Stalemate \u2013 Draw!", Colors.INACCURACY
        elif self.board.is_check():
            side = "White" if self.board.turn == chess.WHITE else "Black"
            msg, col = f"\u26a0 {side} is in check!", Colors.MISTAKE
        else:
            side = "White" if self.board.turn == chess.WHITE else "Black"
            msg, col = f"{side} to move", Colors.TEXT_SECOND
        self._draw_text(msg, max(14, ly.sq // 5), col, ly.board_x, y)

    def _refresh_eval(self):
        score = self._run_engine(self.board, self.DEEP_LIMIT)
        self.eval_score = score
        self.white_pct, self.black_pct = self._score_to_pct(score)
        self.score_before_move = score

    def _show_promotion_menu(self, to_sq: int, color: chess.Color) -> chess.PieceType:
        choices = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
        syms    = ["Q",        "R",         "B",           "N"]
        ly = self.ly
        size = ly.sq
        total_w = size * 4 + 8
        sx = ly.board_x + (to_sq % 8) * ly.sq - total_w // 2 + size // 2
        sy = ly.board_y + ly.board_px // 2 - size // 2
        sx = max(ly.board_x, min(ly.board_x + ly.board_px - total_w, sx))
        rects = [pygame.Rect(sx + i * (size + 2), sy, size, size) for i in range(4)]

        while True:
            self._draw_board()
            self._draw_pieces()
            overlay = pygame.Surface((ly.board_px, ly.board_px), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.screen.blit(overlay, (ly.board_x, ly.board_y))
            draw_rounded_rect(self.screen, Colors.PANEL,
                              pygame.Rect(sx - 8, sy - 8, total_w + 16, size + 16), radius=10)
            for i, (rect, pt) in enumerate(zip(rects, choices)):
                sym = f"w{syms[i]}" if color == chess.WHITE else syms[i].lower()
                img = pygame.transform.smoothscale(ly.PIECE_IMAGES[sym], (size, size))
                self.screen.blit(img, rect.topleft)
            pygame.display.flip()

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    for rect, pt in zip(rects, choices):
                        if rect.collidepoint(ev.pos):
                            return pt

    def _try_move(self, target_sq: int):
        if self.selected_sq is None:
            return
        from_sq = self.selected_sq
        move = chess.Move(from_sq, target_sq)

        piece = self.board.piece_at(from_sq)
        if (piece and piece.piece_type == chess.PAWN
                and chess.square_rank(target_sq) in (0, 7)):
            promo_piece = self._show_promotion_menu(target_sq, piece.color)
            move = chess.Move(from_sq, target_sq, promotion=promo_piece)

        if move not in self.board.legal_moves:
            move = chess.Move(from_sq, target_sq)
            if move not in self.board.legal_moves:
                self.selected_sq = None
                self.legal_targets = []
                return

        san = self.board.san(move)
        board_snap = self.board.copy()
        pre_score  = self.score_before_move

        self.board.push(move)
        self.last_move = move
        self.selected_sq  = None
        self.legal_targets = []
        self.suggest_move  = None

        self.hm.moves.append((san, "", Colors.TEXT_SECOND))
        self._start_analysis(board_snap, move, pre_score)

    def _handle_click(self, x: int, y: int):
        ly = self.ly

        if self.show_pro_games:
            self.show_pro_games = False
            return

        if ly.btn_newgame.collidepoint(x, y):
            self.board = chess.Board()
            self.hm.reset()
            self.selected_sq    = None
            self.legal_targets  = []
            self.last_move      = None
            self.suggest_move   = None
            self.eval_score     = None
            self.score_before_move = None
            self.white_pct = self.black_pct = 50.0
            self.last_quality_label = ""
            self.last_cp_loss = None
            return

        if ly.btn_undo.collidepoint(x, y):
            if self.hm.moves:
                self.hm.moves.pop()
            if self.board.move_stack:
                self.board.pop()
                self.last_move = self.board.peek() if self.board.move_stack else None
            self.selected_sq   = None
            self.legal_targets = []
            self.suggest_move  = None
            return

        if ly.btn_flip.collidepoint(x, y):
            ly.toggle_flip()
            return

        if ly.btn_draw.collidepoint(x, y):
            ly.toggle_draw()
            self.hm.arrows.clear()
            return

        if ly.btn_evaluate.collidepoint(x, y):
            self.show_eval = not self.show_eval
            if self.show_eval:
                threading.Thread(target=self._refresh_eval, daemon=True).start()
            return

        if ly.btn_suggest.collidepoint(x, y):
            def _get_suggest():
                best = self._get_best_move(self.board, self.DEEP_LIMIT)
                self.suggest_move = best
            threading.Thread(target=_get_suggest, daemon=True).start()
            return

        if ly.btn_history.collidepoint(x, y):
            self.pro_games_lines = []
            fen = self.board.fen()

            def _fetch():
                try:
                    games = self.hist_games.find_matching_games(fen)
                    lines = []
                    for g_info, _ in games[:10]:
                        d = g_info.get("game_date", "?")
                        w = g_info.get("white_player", "?")
                        b = g_info.get("black_player", "?")
                        r = g_info.get("result", "?")
                        lines.append(f"  {d}  |  {w}  vs  {b}  [{r}]")
                    self.pro_games_lines = lines if lines else []
                except Exception as e:
                    self.pro_games_lines = [f"Error: {e}"]
                finally:
                    self.show_pro_games = True

            threading.Thread(target=_fetch, daemon=True).start()
            return

        if ly.DRAWING_MODE:
            ly.START_DRAW_POS = (x, y)
            return

        sq = self.pixel_to_sq(x, y)
        if sq is None:
            return

        if self.selected_sq is None:
            piece = self.board.piece_at(sq)
            if piece and piece.color == self.board.turn:
                self.selected_sq   = sq
                self.legal_targets = [m.to_square for m in self.board.legal_moves
                                      if m.from_square == sq]
                self.suggest_move  = None
        else:
            if sq == self.selected_sq:
                self.selected_sq   = None
                self.legal_targets = []
            elif sq in self.legal_targets:
                self._try_move(sq)
            else:
                piece = self.board.piece_at(sq)
                if piece and piece.color == self.board.turn:
                    self.selected_sq   = sq
                    self.legal_targets = [m.to_square for m in self.board.legal_moves
                                          if m.from_square == sq]
                else:
                    self.selected_sq   = None
                    self.legal_targets = []

    def run(self):
        running = True
        while running:

            with self._analysis_lock:
                result = self._pending_result
                self._pending_result = None

            if result:
                score = result.get("score_after")
                cp_loss = result.get("cp_loss")
                if score is not None:
                    self.eval_score = score
                    self.white_pct, self.black_pct = self._score_to_pct(score)
                    self.score_before_move = score
                if cp_loss is not None and self.hm.moves:
                    label, color = self.hm._classify(cp_loss)
                    self.last_quality_label = label
                    self.last_quality_color = color
                    self.last_cp_loss = cp_loss
                    if self.hm.moves:
                        san, _, _ = self.hm.moves[-1]
                        self.hm.moves[-1] = (san, label, color)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.VIDEORESIZE:
                    new_w, new_h = max(640, event.w), max(480, event.h)
                    self.screen = pygame.display.set_mode(
                        (new_w, new_h), pygame.RESIZABLE
                    )
                    self._font_cache.clear()
                    self.ly.update(new_w, new_h)
                    self.ly.load_images()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self._handle_click(*event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.ly.DRAWING_MODE and self.ly.START_DRAW_POS:
                        self.hm.arrows.append(
                            (self.ly.START_DRAW_POS, event.pos)
                        )
                        self.ly.START_DRAW_POS = None

                elif event.type == pygame.MOUSEWHEEL:
                    ly = self.ly
                    mx, my = pygame.mouse.get_pos()
                    if ly.history_rect.collidepoint(mx, my):
                        self.hm.scroll_offset = max(
                            0, self.hm.scroll_offset - event.y
                        )

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if self.board.move_stack:
                            if self.hm.moves:
                                self.hm.moves.pop()
                            self.board.pop()
                            self.last_move = self.board.peek() if self.board.move_stack else None
                    elif event.key == pygame.K_f:
                        self.ly.toggle_flip()
                    elif event.key == pygame.K_ESCAPE:
                        self.show_pro_games = False
                        self.selected_sq    = None
                        self.legal_targets  = []

            self._draw_background()
            self._draw_eval_bar()
            self._draw_board()
            self._draw_pieces()
            self._draw_arrows()
            self._draw_status()
            self._draw_player_bars()
            self._draw_move_history()
            self._draw_move_quality()
            self._draw_buttons()

            if self.show_pro_games:
                self._draw_pro_games_overlay()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


# ─────────────────────────────────────────────────────────────


if __name__ == "__main__":
    app = ChessTrainer()
    app.run()
