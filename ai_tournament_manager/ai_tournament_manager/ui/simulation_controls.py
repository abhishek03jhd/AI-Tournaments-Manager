from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable


class SimulationControls(tk.Frame):
    def __init__(self, master, on_step, on_run_all, on_reset, on_export, **kwargs):
        super().__init__(master, **kwargs)
        self._on_step, self._on_run_all, self._on_reset, self._on_export = on_step, on_run_all, on_reset, on_export
        cfg = dict(font=("Helvetica", 10, "bold"), width=10, pady=4)
        self._step_btn = tk.Button(self, text="▶ Step", command=on_step, bg="#89b4fa", fg="#1e1e2e", **cfg)
        self._run_btn = tk.Button(self, text="⏩ Run All", command=self._run_all, bg="#a6e3a1", fg="#1e1e2e", **cfg)
        self._reset_btn = tk.Button(self, text="↺ Reset", command=on_reset, bg="#f38ba8", fg="#1e1e2e", **cfg)
        self._export_btn = tk.Button(self, text="💾 Export", command=self._export, bg="#fab387", fg="#1e1e2e", **cfg)
        for btn in (self._step_btn, self._run_btn, self._reset_btn, self._export_btn):
            btn.pack(side=tk.LEFT, padx=6, pady=6)

    def _run_all(self):
        self._step_btn.configure(state=tk.DISABLED)
        self._reset_btn.configure(state=tk.DISABLED)
        try:
            self._on_run_all()
        finally:
            self._step_btn.configure(state=tk.NORMAL)
            self._reset_btn.configure(state=tk.NORMAL)

    def _export(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
            filetypes=[("Text", "*.txt"), ("CSV", "*.csv"), ("All", "*.*")], title="Export Results")
        if path:
            try:
                self._on_export(path)
                messagebox.showinfo("Export", f"Saved to:\n{path}")
            except Exception as exc:
                messagebox.showerror("Export Error", str(exc))

    def set_enabled(self, enabled: bool):
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self._step_btn, self._run_btn, self._reset_btn, self._export_btn):
            btn.configure(state=state)
