"""AI Tournament Manager — application entry point."""
from __future__ import annotations

import logging
import tkinter as tk
from tkinter import messagebox

from ai_tournament_manager.domain.enums import AlgorithmType, SeedingMode
from ai_tournament_manager.domain.models import MatchResult, Participant
from ai_tournament_manager.engine.tournament_controller import TournamentController
from ai_tournament_manager.ui.bracket_visualizer import BracketVisualizer
from ai_tournament_manager.ui.decision_tree_visualizer import DecisionTreeVisualizer
from ai_tournament_manager.ui.results_summary_panel import ResultsSummaryPanel
from ai_tournament_manager.ui.setup_panel import SetupPanel
from ai_tournament_manager.ui.simulation_controls import SimulationControls

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AI Tournament Manager")
        self.geometry("1280x800")
        self.configure(bg="#1e1e2e")
        self._controller = TournamentController()
        self._build()

    def _build(self) -> None:
        self._setup = SetupPanel(self, on_create=self._on_create, bg="#181825")
        self._setup.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        self._controls = SimulationControls(
            self,
            on_step=self._on_step,
            on_run_all=self._on_run_all,
            on_reset=self._on_reset,
            on_export=self._on_export,
            bg="#181825",
        )
        self._controls.pack(side=tk.TOP, fill=tk.X, padx=8)
        self._controls.set_enabled(False)

        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#1e1e2e", sashwidth=6)
        pane.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=8, pady=4)

        self._bracket_viz = BracketVisualizer(pane, bg="#1e1e2e")
        pane.add(self._bracket_viz, minsize=400)

        self._tree_viz = DecisionTreeVisualizer(pane, bg="#181825")
        pane.add(self._tree_viz, minsize=350)

        self._results = ResultsSummaryPanel(pane)
        pane.add(self._results, minsize=200)

    def _on_create(self, participants, algorithm, seeding) -> None:
        try:
            bracket = self._controller.create_tournament(participants, algorithm, seeding)
            self._controller.register_on_match_complete(self._on_match_complete)
            self._controller.register_on_tournament_complete(self._on_tournament_complete)
            self._bracket_viz.render(bracket)
            self._results.clear()
            self._controls.set_enabled(True)
        except Exception as exc:
            logger.exception("Error creating tournament")
            messagebox.showerror("Error", f"Could not create tournament:\n{exc}")

    def _on_match_complete(self, result: MatchResult) -> None:
        self._bracket_viz.on_match_complete(result)
        self._tree_viz.on_match_complete(result)
        if self._controller.bracket:
            self._results.update_results(self._controller.bracket)

    def _on_tournament_complete(self, champion: Participant) -> None:
        self._results.show_champion(champion)

    def _on_step(self) -> None:
        try:
            self._controller.step()
        except Exception as exc:
            messagebox.showerror("Simulation Error", f"{exc}\n\nYou may Reset and try again.")

    def _on_run_all(self) -> None:
        try:
            self._controller.run_all()
        except Exception as exc:
            messagebox.showerror("Simulation Error", f"{exc}\n\nYou may Reset and try again.")

    def _on_reset(self) -> None:
        self._controller.reset()
        if self._controller.bracket:
            self._bracket_viz.render(self._controller.bracket)
        self._tree_viz._canvas.delete("all")
        self._results.clear()

    def _on_export(self, path: str) -> None:
        self._controller.export_results(path)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
