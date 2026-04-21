from __future__ import annotations
import tkinter as tk
from ai_tournament_manager.domain.models import Bracket, MatchResult

_SLOT_W, _SLOT_H, _H_GAP = 160, 40, 60


class BracketVisualizer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._canvas = tk.Canvas(self, bg="#1e1e2e", highlightthickness=0)
        h_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        v_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._bracket: Bracket | None = None

    def render(self, bracket: Bracket):
        self._bracket = bracket
        self._canvas.delete("all")
        self._draw()

    def on_match_complete(self, result: MatchResult):
        if self._bracket:
            self._canvas.delete("all")
            self._draw()

    def _draw(self):
        if not self._bracket:
            return
        rounds = self._bracket.rounds
        if not rounds:
            return
        max_matches = len(rounds[0].matches)
        canvas_h = max_matches * (_SLOT_H + 10) * 2 + 60
        canvas_w = len(rounds) * (_SLOT_W + _H_GAP) + _H_GAP
        self._canvas.configure(scrollregion=(0, 0, canvas_w, canvas_h))
        positions = {}
        for r_idx, round_ in enumerate(rounds):
            x = _H_GAP + r_idx * (_SLOT_W + _H_GAP)
            spacing = canvas_h / (len(round_.matches) + 1)
            self._canvas.create_text(x + _SLOT_W // 2, 18, text=round_.label, fill="#cdd6f4", font=("Helvetica", 10, "bold"))
            for m_idx, match in enumerate(round_.matches):
                cy = int(spacing * (m_idx + 1))
                positions[match.id] = (x + _SLOT_W // 2, cy)
                self._draw_slot(x, cy, match)
        for r_idx in range(len(rounds) - 1):
            for m_idx, match in enumerate(rounds[r_idx].matches):
                next_idx = m_idx // 2
                if next_idx >= len(rounds[r_idx + 1].matches):
                    continue
                next_match = rounds[r_idx + 1].matches[next_idx]
                if match.id in positions and next_match.id in positions:
                    x1, y1 = positions[match.id]
                    x2, y2 = positions[next_match.id]
                    self._canvas.create_line(x1 + _SLOT_W // 2, y1, x2 - _SLOT_W // 2, y2, fill="#585b70")

    def _draw_slot(self, x, cy, match):
        y = cy - _SLOT_H // 2
        wn = match.winner.name if match.winner else None
        half = _SLOT_H // 2 - 1

        def color(p):
            if p is None: return "#313244"
            if wn and p.name == wn: return "#a6e3a1"
            if wn: return "#f38ba8"
            return "#45475a"

        def tc(p):
            if p is None: return "#6c7086"
            return "#1e1e2e" if wn else "#cdd6f4"

        for i, p in enumerate([match.participant_a, match.participant_b]):
            yy = y + i * half
            self._canvas.create_rectangle(x, yy, x + _SLOT_W, yy + half, fill=color(p), outline="#585b70")
            if p:
                sc = f"  ({p.heuristic_score:.1f})" if p.heuristic_score else ""
                self._canvas.create_text(x + 6, yy + half // 2, anchor=tk.W, text=f"{p.name}{sc}", fill=tc(p), font=("Helvetica", 9))
