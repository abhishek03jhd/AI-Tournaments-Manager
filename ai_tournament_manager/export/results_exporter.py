from __future__ import annotations

import csv
import os

from ai_tournament_manager.domain.models import Bracket


class ExportError(Exception):
    """Raised when the export path is not writable."""

class ResultsExporter:
    """Exports tournament results to plain-text or CSV."""

    def export(self, bracket: Bracket, path: str) -> None:
        """Write all match outcomes to a file.

        Format is determined by the file extension:
        - .csv  → CSV format
        - anything else → plain-text

        Raises:
            ExportError: If the path is not writable.
        """
        try:
            if path.lower().endswith(".csv"):
                self._export_csv(bracket, path)
            else:
                self._export_text(bracket, path)
        except OSError as exc:
            raise ExportError(
                f"Cannot write to '{path}': {exc}. "
                "Please choose a different file path."
            ) from exc

    def _rows(self, bracket: Bracket) -> list[dict]:
        rows = []
        for round_ in bracket.rounds:
            for match in round_.matches:
                if match.winner is None:
                    continue
                loser = (
                    match.participant_b
                    if match.winner is match.participant_a
                    else match.participant_a
                )
                rows.append({
                    "round": round_.label,
                    "participant_a": match.participant_a.name if match.participant_a else "",
                    "participant_b": match.participant_b.name if match.participant_b else "",
                    "winner": match.winner.name,
                    "loser": loser.name if loser else "",
                })
        return rows

    def _export_csv(self, bracket: Bracket, path: str) -> None:
        rows = self._rows(bracket)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["round", "participant_a", "participant_b", "winner", "loser"])
            writer.writeheader()
            writer.writerows(rows)

    def _export_text(self, bracket: Bracket, path: str) -> None:
        rows = self._rows(bracket)
        lines = ["AI Tournament Manager — Results\n", "=" * 40 + "\n"]
        for row in rows:
            lines.append(
                f"[{row['round']}] {row['participant_a']} vs {row['participant_b']} → Winner: {row['winner']}\n"
            )
        if bracket.champion:
            lines.append(f"\nChampion: {bracket.champion.name}\n")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
