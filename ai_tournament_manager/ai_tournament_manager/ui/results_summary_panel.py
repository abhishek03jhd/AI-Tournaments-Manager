from __future__ import annotations
import tkinter as tk
from ai_tournament_manager.domain.models import Bracket, Participant


class ResultsSummaryPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#1e1e2e", **kwargs)
        self._champion_var = tk.StringVar()
        tk.Label(self, text="Results", font=("Helvetica", 12, "bold"), bg="#1e1e2e", fg="#cdd6f4").pack(pady=(8, 2))
        tk.Label(self, textvariable=self._champion_var, font=("Helvetica", 14, "bold"), bg="#1e1e2e", fg="#f9e2af").pack(pady=(0, 6))
        frame = tk.Frame(self, bg="#1e1e2e")
        frame.pack(fill=tk.BOTH, expand=True)
        sb = tk.Scrollbar(frame)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._listbox = tk.Listbox(frame, yscrollcommand=sb.set, bg="#313244", fg="#cdd6f4",
                                   font=("Helvetica", 9), selectbackground="#585b70", relief=tk.FLAT, borderwidth=0)
        self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.config(command=self._listbox.yview)

    def show_champion(self, champion: Participant):
        self._champion_var.set(f"🏆 Champion: {champion.name}")

    def update_results(self, bracket: Bracket):
        self._listbox.delete(0, tk.END)
        for round_ in bracket.rounds:
            self._listbox.insert(tk.END, f"── {round_.label} ──")
            for match in round_.matches:
                if match.winner:
                    self._listbox.insert(tk.END,
                        f"  {match.participant_a.name} vs {match.participant_b.name}  →  ✓ {match.winner.name}")

    def clear(self):
        self._champion_var.set("")
        self._listbox.delete(0, tk.END)
