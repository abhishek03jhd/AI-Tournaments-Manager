"""SimulationControls — Step / Run All / Reset / Export buttons."""
from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable


class SimulationControls(tk.Frame):
    """Control bar wired to TournamentController actions."""

    def __init__(
        self,
        master: tk.Widget,
        on_step: Callable[[], None],
        on_run_all: Callable[[], None],
        on_reset: Callable[[], None],
        on_export: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._on_step = on_step
        self._on_run_all = on_run_all
        self._on_reset = on_reset
        self._on_export = on_export
        self._running = False
        self._build()

    def _build(self) -> None:
        btn_cfg = dict(font=("Helvetica", 10, "bold"), width=10, pady=4)
        self._step_btn = tk.Button(self, text="▶ Step", command=self._step, bg="#89b4fa", fg="#1e1e2e", **btn_cfg)
        self._run_btn = tk.Button(self, text="⏩ Run All", command=self._run_all, bg="#a6e3a1", fg="#1e1e2e", **btn_cfg)
        self._reset_btn = tk.Button(self, text="↺ Reset", command=self._reset, bg="#f38ba8", fg="#1e1e2e", **btn_cfg)
        self._export_btn = tk.Button(self, text="💾 Export", command=self._export, bg="#fab387", fg="#1e1e2e", **btn_cfg)

        for btn in (self._step_btn, self._run_btn, self._reset_btn, self._export_btn):
            btn.pack(side=tk.LEFT, padx=6, pady=6)

    # ---------------------------------------------------------------- handlers

    def _step(self) -> None:
        self._on_step()

    def _run_all(self) -> None:
        self._set_running(True)
        try:
            self._on_run_all()
        finally:
            self._set_running(False)

    def _reset(self) -> None:
        self._on_reset()

    def _export(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Tournament Results",
        )
        if path:
            try:
                self._on_export(path)
                messagebox.showinfo("Export", f"Results saved to:\n{path}")
            except Exception as exc:  # noqa: BLE001
                messagebox.showerror("Export Error", str(exc))

    # ---------------------------------------------------------------- state

    def _set_running(self, running: bool) -> None:
        self._running = running
        state = tk.DISABLED if running else tk.NORMAL
        self._step_btn.configure(state=state)
        self._reset_btn.configure(state=state)

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable all controls (e.g., before tournament is created)."""
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in (self._step_btn, self._run_btn, self._reset_btn, self._export_btn):
            btn.configure(state=state)
