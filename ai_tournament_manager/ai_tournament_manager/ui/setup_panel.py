from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Callable
from ai_tournament_manager.domain.enums import AlgorithmType, SeedingMode
from ai_tournament_manager.domain.models import Participant
from ai_tournament_manager.domain.validators import ValidationError, validate_attribute_value, validate_participant_count, validate_participant_name

_ATTRS = ["strength", "speed", "stamina"]
_ALGORITHMS = [a.value for a in AlgorithmType]
_SEEDINGS = [s.value for s in SeedingMode]


class SetupPanel(tk.Frame):
    def __init__(self, master, on_create: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self._on_create = on_create
        self._rows: list[dict] = []
        self._error_var = tk.StringVar()
        self._algorithm_var = tk.StringVar(value=AlgorithmType.MINIMAX.value)
        self._seeding_var = tk.StringVar(value=SeedingMode.RANDOM.value)
        self._build()

    def _build(self):
        tk.Label(self, text="AI Tournament Manager", font=("Helvetica", 16, "bold")).grid(row=0, column=0, columnspan=6, pady=(10, 4))
        for col, text in enumerate(["Name", "Strength", "Speed", "Stamina", "", ""]):
            tk.Label(self, text=text, font=("Helvetica", 10, "bold")).grid(row=1, column=col, padx=4)
        self._rows_frame = tk.Frame(self)
        self._rows_frame.grid(row=2, column=0, columnspan=6, sticky="ew")
        for _ in range(4):
            self._add_row()
        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=6, pady=4)
        tk.Button(btn_frame, text="+ Add Participant", command=self._add_row).pack(side=tk.LEFT, padx=4)
        algo_frame = tk.Frame(self)
        algo_frame.grid(row=4, column=0, columnspan=6, pady=4)
        tk.Label(algo_frame, text="Algorithm:").pack(side=tk.LEFT)
        ttk.Combobox(algo_frame, textvariable=self._algorithm_var, values=_ALGORITHMS, state="readonly", width=20).pack(side=tk.LEFT, padx=4)
        seed_frame = tk.Frame(self)
        seed_frame.grid(row=5, column=0, columnspan=6, pady=4)
        tk.Label(seed_frame, text="Seeding:").pack(side=tk.LEFT)
        ttk.Combobox(seed_frame, textvariable=self._seeding_var, values=_SEEDINGS, state="readonly", width=15).pack(side=tk.LEFT, padx=4)
        tk.Label(self, textvariable=self._error_var, fg="red", wraplength=400).grid(row=6, column=0, columnspan=6)
        tk.Button(self, text="Create Tournament", command=self._on_create_clicked,
                  bg="#4CAF50", fg="white", font=("Helvetica", 11, "bold")).grid(row=7, column=0, columnspan=6, pady=8)

    def _add_row(self):
        row_idx = len(self._rows)
        frame = self._rows_frame
        name_var = tk.StringVar()
        attr_vars = [tk.StringVar(value="50") for _ in _ATTRS]
        tk.Entry(frame, textvariable=name_var, width=18).grid(row=row_idx, column=0, padx=3, pady=2)
        for col, av in enumerate(attr_vars, start=1):
            tk.Entry(frame, textvariable=av, width=8).grid(row=row_idx, column=col, padx=3, pady=2)
        tk.Button(frame, text="✕", fg="red", command=lambda r=row_idx: self._remove_row(r)).grid(row=row_idx, column=4, padx=2)
        self._rows.append({"name_var": name_var, "attr_vars": attr_vars})

    def _remove_row(self, row_idx):
        if row_idx < len(self._rows):
            self._rows[row_idx]["name_var"].set("")
            self._rows[row_idx]["removed"] = True

    def _on_create_clicked(self):
        self._error_var.set("")
        participants = []
        for row in self._rows:
            if row.get("removed"):
                continue
            name = row["name_var"].get().strip()
            if not name:
                continue
            try:
                validate_participant_name(name)
            except ValidationError as e:
                self._error_var.set(str(e))
                return
            attrs = {}
            for attr_name, av in zip(_ATTRS, row["attr_vars"]):
                try:
                    val = float(av.get().strip())
                    validate_attribute_value(val)
                except (ValueError, ValidationError) as e:
                    self._error_var.set(f"'{attr_name}' for '{name}': {e}")
                    return
                attrs[attr_name] = val
            participants.append(Participant(name=name, attributes=attrs))
        try:
            validate_participant_count(len(participants))
        except ValidationError as e:
            self._error_var.set(str(e))
            return
        self._on_create(participants, AlgorithmType(self._algorithm_var.get()), SeedingMode(self._seeding_var.get()))
