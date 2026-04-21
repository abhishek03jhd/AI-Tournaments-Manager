"""BracketVisualizer — canvas-based rendering of the tournament bracket."""
from __future__ import annotations

import tkinter as tk

from ai_tournament_manager.domain.models import Bracket, MatchResult

_SLOT_W = 160
_SLOT_H = 40
_H_GAP = 60   # horizontal gap between rounds
_V_GAP = 10   # vertical gap between match slots


class BracketVisualizer(tk.Frame):
    """Renders the full single-elimination bracket on a scrollable canvas."""

    def __init__(self, master: tk.Widget, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._canvas = tk.Canvas(self, bg="#1e1e2e", highlightthickness=0)
        h_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        v_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bracket: Bracket | None = None

    # ---------------------------------------------------------------- public

    def render(self, bracket: Bracket) -> None:
        """Draw the full bracket from scratch."""
        self._bracket = bracket
        self._canvas.delete("all")
        self._draw_bracket()

    def on_match_complete(self, result: MatchResult) -> None:
        """Refresh the bracket after a match resolves."""
        if self._bracket:
            self._canvas.delete("all")
            self._draw_bracket()

    # ---------------------------------------------------------------- drawing

    def _draw_bracket(self) -> None:
        if not self._bracket:
            return
        rounds = self._bracket.rounds
        n_rounds = len(rounds)
        if n_rounds == 0:
            return

        # Calculate canvas size
        max_matches = len(rounds[0].matches)
        canvas_h = max_matches * (_SLOT_H + _V_GAP) * 2 + 60
        canvas_w = n_rounds * (_SLOT_W + _H_GAP) + _H_GAP
        self._canvas.configure(scrollregion=(0, 0, canvas_w, canvas_h))

        slot_positions: dict[str, tuple[int, int]] = {}  # match_id -> (x, y) center

        for r_idx, round_ in enumerate(rounds):
            x = _H_GAP + r_idx * (_SLOT_W + _H_GAP)
            n_matches = len(round_.matches)
            total_h = canvas_h
            spacing = total_h / (n_matches + 1)

            # Round label
            self._canvas.create_text(
                x + _SLOT_W // 2, 18,
                text=round_.label, fill="#cdd6f4",
                font=("Helvetica", 10, "bold")
            )

            for m_idx, match in enumerate(round_.matches):
                cy = int(spacing * (m_idx + 1))
                slot_positions[match.id] = (x + _SLOT_W // 2, cy)
                self._draw_match_slot(x, cy, match)

        # Draw connector lines between rounds
        for r_idx in range(len(rounds) - 1):
            curr_round = rounds[r_idx]
            next_round = rounds[r_idx + 1]
            for m_idx, match in enumerate(curr_round.matches):
                next_match_idx = m_idx // 2
                if next_match_idx >= len(next_round.matches):
                    continue
                next_match = next_round.matches[next_match_idx]
                if match.id in slot_positions and next_match.id in slot_positions:
                    x1, y1 = slot_positions[match.id]
                    x2, y2 = slot_positions[next_match.id]
                    self._canvas.create_line(
                        x1 + _SLOT_W // 2, y1,
                        x2 - _SLOT_W // 2, y2,
                        fill="#585b70", width=1
                    )

    def _draw_match_slot(self, x: int, cy: int, match) -> None:
        y = cy - _SLOT_H // 2
        # Determine colors
        winner_name = match.winner.name if match.winner else None

        def _slot_color(participant) -> str:
            if participant is None:
                return "#313244"
            if winner_name and participant.name == winner_name:
                return "#a6e3a1"  # green for winner
            if winner_name:
                return "#f38ba8"  # red for loser
            return "#45475a"

        def _text_color(participant) -> str:
            if participant is None:
                return "#6c7086"
            if winner_name and participant.name == winner_name:
                return "#1e1e2e"
            if winner_name:
                return "#1e1e2e"
            return "#cdd6f4"

        half = _SLOT_H // 2 - 1

        # Participant A slot (top half)
        self._canvas.create_rectangle(x, y, x + _SLOT_W, y + half, fill=_slot_color(match.participant_a), outline="#585b70")
        if match.participant_a:
            score_txt = f"  ({match.participant_a.heuristic_score:.1f})" if match.participant_a.heuristic_score else ""
            self._canvas.create_text(
                x + 6, y + half // 2, anchor=tk.W,
                text=f"{match.participant_a.name}{score_txt}",
                fill=_text_color(match.participant_a), font=("Helvetica", 9)
            )

        # Participant B slot (bottom half)
        self._canvas.create_rectangle(x, y + half, x + _SLOT_W, y + _SLOT_H, fill=_slot_color(match.participant_b), outline="#585b70")
        if match.participant_b:
            score_txt = f"  ({match.participant_b.heuristic_score:.1f})" if match.participant_b.heuristic_score else ""
            self._canvas.create_text(
                x + 6, y + half + half // 2, anchor=tk.W,
                text=f"{match.participant_b.name}{score_txt}",
                fill=_text_color(match.participant_b), font=("Helvetica", 9)
            )
