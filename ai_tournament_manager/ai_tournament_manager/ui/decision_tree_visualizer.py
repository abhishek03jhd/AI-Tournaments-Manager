from __future__ import annotations
import tkinter as tk
from ai_tournament_manager.domain.models import AlgorithmResult, MatchResult, TreeNode

_NODE_R, _H_GAP, _V_GAP = 28, 20, 70
_C = {"normal": "#45475a", "win": "#a6e3a1", "pruned": "#f38ba8",
      "text": "#cdd6f4", "dark": "#1e1e2e", "edge": "#585b70",
      "win_edge": "#a6e3a1", "hc": "#89b4fa", "hc_max": "#fab387"}


class DecisionTreeVisualizer(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        tk.Label(self, text="Decision Tree / Search Path", font=("Helvetica", 11, "bold"),
                 bg="#181825", fg="#cdd6f4").pack(side=tk.TOP, fill=tk.X)
        self._canvas = tk.Canvas(self, bg="#181825", highlightthickness=0)
        h = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._canvas.xview)
        v = tk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=h.set, yscrollcommand=v.set)
        h.pack(side=tk.BOTTOM, fill=tk.X)
        v.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._canvas.bind("<Control-MouseWheel>", self._zoom)

    def on_match_complete(self, result: MatchResult):
        self.render(result.algorithm_result)

    def render(self, ar: AlgorithmResult):
        self._canvas.delete("all")
        if ar.search_tree:
            self._render_tree(ar.search_tree)
        elif ar.search_path:
            self._render_hc(ar.search_path)

    def _render_tree(self, root):
        pos = {}
        self._place(root, 0, [0.0], pos)
        if pos:
            mn = min(p[0] for p in pos.values())
            shift = max(0, _NODE_R + 10 - mn)
            pos = {k: (v[0] + shift, v[1]) for k, v in pos.items()}
        mx = max((p[0] for p in pos.values()), default=200) + _NODE_R + 10
        my = max((p[1] for p in pos.values()), default=200) + _NODE_R + 10
        self._canvas.configure(scrollregion=(0, 0, mx, my))
        self._edges(root, pos, set())
        self._nodes(root, pos, set())

    def _place(self, node, depth, xc, pos):
        nid = id(node)
        if not node.children:
            cx = xc[0] * (_NODE_R * 2 + _H_GAP) + _NODE_R + 10
            xc[0] += 1
        else:
            xs = [self._place(c, depth + 1, xc, pos) for c in node.children]
            cx = (xs[0] + xs[-1]) / 2
        pos[nid] = (cx, depth * _V_GAP + _NODE_R + 30)
        return cx

    def _edges(self, node, pos, seen):
        nid = id(node)
        if nid in seen: return
        seen.add(nid)
        px, py = pos.get(nid, (0, 0))
        for child in node.children:
            cx, cy = pos.get(id(child), (0, 0))
            color = _C["win_edge"] if node.is_winning_path and child.is_winning_path else _C["edge"]
            self._canvas.create_line(px, py, cx, cy, fill=color, width=2 if color == _C["win_edge"] else 1)
            self._edges(child, pos, seen)

    def _nodes(self, node, pos, seen):
        nid = id(node)
        if nid in seen: return
        seen.add(nid)
        px, py = pos.get(nid, (0, 0))
        r = _NODE_R
        fill = _C["pruned"] if node.pruned else (_C["win"] if node.is_winning_path else _C["normal"])
        tc = _C["dark"] if fill in (_C["win"], _C["pruned"]) else _C["text"]
        self._canvas.create_oval(px-r, py-r, px+r, py+r, fill=fill, outline="#313244", width=2)
        short = node.label.split(" vs ")[0][:8] if " vs " in node.label else node.label[:8]
        self._canvas.create_text(px, py-8, text=short, fill=tc, font=("Helvetica", 7, "bold"))
        vt = f"{node.value:.1f}"
        if node.alpha is not None: vt += f"\nα={node.alpha:.0f}"
        if node.beta is not None: vt += f" β={node.beta:.0f}"
        self._canvas.create_text(px, py+8, text=vt, fill=tc, font=("Helvetica", 7))
        if node.pruned:
            self._canvas.create_line(px-r, py-r, px+r, py+r, fill=_C["dark"], width=2)
        for child in node.children:
            self._nodes(child, pos, seen)

    def _render_hc(self, path):
        if not path: return
        cw = len(path) * 120 + 40
        self._canvas.configure(scrollregion=(0, 0, cw, 200))
        prev = None
        for i, state in enumerate(path):
            cx, cy, r = 40 + i * 120, 100, 30
            fill = _C["hc_max"] if state.is_local_max else _C["hc"]
            self._canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=fill, outline="#313244", width=2)
            self._canvas.create_text(cx, cy-10, text=state.participant.name[:10], fill=_C["dark"], font=("Helvetica", 8, "bold"))
            self._canvas.create_text(cx, cy+10, text=f"{state.heuristic_value:.1f}", fill=_C["dark"], font=("Helvetica", 8))
            if state.is_local_max:
                self._canvas.create_text(cx, cy+r+12, text="★ local max", fill=_C["hc_max"], font=("Helvetica", 7))
            if prev:
                self._canvas.create_line(prev[0]+r, prev[1], cx-r, cy, fill=_C["edge"], arrow=tk.LAST, width=2)
            prev = (cx, cy)

    def _zoom(self, event):
        f = 1.1 if event.delta > 0 else 0.9
        self._canvas.scale("all", event.x, event.y, f, f)
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
