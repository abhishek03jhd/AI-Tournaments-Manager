from __future__ import annotations
import csv
from ai_tournament_manager.domain.models import Bracket


class ExportError(Exception):
    pass


class ResultsExporter:
    def export(self, bracket: Bracket, path: str) -> None:
        try:
            if path.lower().endswith(".csv"):
                self._export_csv(bracket, path)
            else:
                self._export_text(bracket, path)
        except OSError as exc:
            raise ExportError(f"Cannot write to '{path}': {exc}. Please choose a different path.") from exc

    def _rows(self, bracket):
        rows = []
        for round_ in bracket.rounds:
            for match in round_.matches:
                if not match.winner:
                    continue
                loser = match.participant_b if match.winner is match.participant_a else match.participant_a
                rows.append({"round": round_.label,
                             "participant_a": match.participant_a.name if match.participant_a else "",
                             "participant_b": match.participant_b.name if match.participant_b else "",
                             "winner": match.winner.name,
                             "loser": loser.name if loser else ""})
        return rows

    def _export_csv(self, bracket, path):
        rows = self._rows(bracket)
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["round", "participant_a", "participant_b", "winner", "loser"])
            w.writeheader()
            w.writerows(rows)

    def _export_text(self, bracket, path):
        rows = self._rows(bracket)
        lines = ["AI Tournament Manager — Results\n", "=" * 40 + "\n"]
        for row in rows:
            lines.append(f"[{row['round']}] {row['participant_a']} vs {row['participant_b']} → Winner: {row['winner']}\n")
        if bracket.champion:
            lines.append(f"\nChampion: {bracket.champion.name}\n")
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)
