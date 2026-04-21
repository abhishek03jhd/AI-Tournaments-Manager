"""DecisionTreeVisualizer — renders Minimax/Alpha-Beta trees and Hill Climbing paths."""
from __future__ import annotations

import tkinter as tk

from ai_tournament_manager.domain.models import AlgorithmResult, MatchResult, TreeNode

_NODE_R = 28       # node circle radius
_H_GAP = 20        # horizontal gap between sibling subtrees
_V_GAP = 70        # vertical gap between levels

_COLOR_NORMAL = "#45475a"
_COLOR_WIN_PATH = "#a6e3a1"
_COLOR_PRUNED = "#f38ba8"
_COLOR_TEXT = "#cdd6f4"
_COLOR_TEXT_DARK = "#1e1e2e"
_COLOR_EDGE = "#585b70"
_COLOR_WIN_EDGE = "#a6e3a1"
_COLOR_HC_NODE = "#89b4fa"
_COLOR_HC_LOCAL_MAX = "#fab387"


class DecisionTreeVisualizer(tk.Frame):
    """Scrollable canvas that renders the AI decision artifact for the last match."""

    def __init__(self, master: tk.Widget, **kwargs) -> None:
        super().__init__(master, **kwargs)
        tk.Label(self, text="Decision Tree / Search Path", font=("Helvetica", 11, "bold"),
                 bg="#181825", fg="#cdd6f4").pack(side=tk.TOP, fill=tk.X)
        self._canvas = tk.Canvas(self, bg="#181825", highlightthickness=0)
        h_scroll = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        v_scroll = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Zoom support
        self._scale = 1.0
        self._canvas.bind("<Control-MouseWheel>", self._on_zoom)

    # ---------------------------------------------------------------- public

    def on_match_complete(self, result: MatchResult) -> None:
        self.render(result.algorithm_result)

    def render(self, algo_result: AlgorithmResult) -> None:
        self._canvas.delete("all")
        if algo_result.search_tree is not None:
            self._render_tree(algo_result.search_tree)
        elif algo_result.search_path is not None:
            self._render_hill_climbing(algo_result.search_path)

    # ---------------------------------------------------------------- tree

    def _render_tree(self, root: TreeNode) -> None:
        positions: dict[int, tuple[float, float]] = {}
        self._assign_positions(root, 0, [0.0], positions, id_map={})
        # Shift so minimum x >= NODE_R + 10
        if positions:
            min_x = min(p[0] for p in positions.values())
            shift = _NODE_R + 10 - min_x if min_x < _NODE_R + 10 else 0
            positions = {k: (v[0] + shift, v[1]) for k, v in positions.items()}
        max_x = max((p[0] for p in positions.values()), default=200) + _NODE_R + 10
        max_y = max((p[1] for p in positions.values()), default=200) + _NODE_R + 10
        self._canvas.configure(scrollregion=(0, 0, max_x, max_y))
        self._draw_tree_edges(root, positions, {})
        self._draw_tree_nodes(root, positions, {})

    def _assign_positions(
        self, node: TreeNode, depth: int, x_counter: list[float],
        positions: dict, id_map: dict
    ) -> float:
        nid = id(node)
        if not node.children:
            cx = x_counter[0] * (_NODE_R * 2 + _H_GAP) + _NODE_R + 10
            x_counter[0] += 1
        else:
            child_xs = []
            for child in node.children:
                cx = self._assign_positions(child, depth + 1, x_counter, positions, id_map)
                child_xs.append(cx)
            cx = (child_xs[0] + child_xs[-1]) / 2
        cy = depth * _V_GAP + _NODE_R + 30
        positions[nid] = (cx, cy)
        return cx

    def _draw_tree_edges(self, node: TreeNode, positions: dict, visited: dict) -> None:
        nid = id(node)
        if nid in visited:
            return
        visited[nid] = True
        px, py = positions.get(nid, (0, 0))
        for child in node.children:
            cid = id(child)
            cx, cy = positions.get(cid, (0, 0))
            color = _COLOR_WIN_EDGE if (node.is_winning_path and child.is_winning_path) else _COLOR_EDGE
            self._canvas.create_line(px, py, cx, cy, fill=color, width=2 if color == _COLOR_WIN_EDGE else 1)
            self._draw_tree_edges(child, positions, visited)

    def _draw_tree_nodes(self, node: TreeNode, positions: dict, visited: dict) -> None:
        nid = id(node)
        if nid in visited:
            return
        visited[nid] = True
        px, py = positions.get(nid, (0, 0))
        r = _NODE_R
        if node.pruned:
            fill = _COLOR_PRUNED
        elif node.is_winning_path:
            fill = _COLOR_WIN_PATH
        else:
            fill = _COLOR_NORMAL
        text_color = _COLOR_TEXT_DARK if fill in (_COLOR_WIN_PATH, _COLOR_PRUNED) else _COLOR_TEXT
        self._canvas.create_oval(px - r, py - r, px + r, py + r, fill=fill, outline="#313244", width=2)
        # Short label
        short = node.label.split(" vs ")[0][:8] if " vs " in node.label else node.label[:8]
        self._canvas.create_text(px, py - 8, text=short, fill=text_color, font=("Helvetica", 7, "bold"))
        val_txt = f"{node.value:.1f}"
        if node.alpha is not None:
            val_txt += f"\nα={node.alpha:.0f}"
        if node.beta is not None:
            val_txt += f" β={node.beta:.0f}"
        self._canvas.create_text(px, py + 8, text=val_txt, fill=text_color, font=("Helvetica", 7))
        if node.pruned:
            self._canvas.create_line(px - r, py - r, px + r, py + r, fill="#1e1e2e", width=2)
        for child in node.children:
            self._draw_tree_nodes(child, positions, visited)

    # ---------------------------------------------------------------- hill climbing

    def _render_hill_climbing(self, path) -> None:
        if not path:
            return
        n = len(path)
        canvas_w = n * 120 + 40
        canvas_h = 200
        self._canvas.configure(scrollregion=(0, 0, canvas_w, canvas_h))
        cx_prev, cy_prev = None, None
        for i, state in enumerate(path):
            cx = 40 + i * 120
            cy = 100
            fill = _COLOR_HC_LOCAL_MAX if state.is_local_max else _COLOR_HC_NODE
            r = 30
            self._canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=fill, outline="#313244", width=2)
            name = state.participant.name[:10]
            self._canvas.create_text(cx, cy - 10, text=name, fill=_COLOR_TEXT_DARK, font=("Helvetica", 8, "bold"))
            self._canvas.create_text(cx, cy + 10, text=f"{state.heuristic_value:.1f}", fill=_COLOR_TEXT_DARK, font=("Helvetica", 8))
            if state.is_local_max:
                self._canvas.create_text(cx, cy + r + 12, text="★ local max", fill=_COLOR_HC_LOCAL_MAX, font=("Helvetica", 7))
            if cx_prev is not None:
                self._canvas.create_line(cx_prev + r, cy_prev, cx - r, cy, fill=_COLOR_EDGE, arrow=tk.LAST, width=2)
            cx_prev, cy_prev = cx, cy

    # ---------------------------------------------------------------- zoom

    def _on_zoom(self, event: tk.Event) -> None:
        factor = 1.1 if event.delta > 0 else 0.9
        self._scale *= factor
        self._canvas.scale("all", event.x, event.y, factor, factor)
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
