import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BG_DARK = "#1a1a2e"
BG_CARD = "#1e1e2e"
FG_MAIN = "#e0e0f0"
FG_DIM = "#8888aa"
FG_ACCENT = "#e94560"
FG_GREEN = "#4ecca3"


class _CardFrame(tk.Frame):
    def __init__(self, parent, title="", **kw):
        super().__init__(
            parent,
            bg=BG_CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground="#333355",
            **kw
        )
        if title:
            tk.Label(
                self, text=title, bg=BG_CARD, fg=FG_ACCENT, font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=8, pady=(6, 2))


class _DarkFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)


class ProjectOverviewTab(_DarkFrame):
    """High-level summary of the editable project domains and asset folders."""

    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="Project Overview",
            bg=BG_DARK,
            fg=FG_ACCENT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        summary = _CardFrame(self, title="Editable content")
        summary.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        text = (
            "This editor is organized into modular workspaces for the major content domains in the project:\n\n"
            "- Pokémon data: species stats, types, abilities, dex info\n"
            "- Move data: power, accuracy, type, category, PP\n"
            "- Item data: prices, effect params, item names\n"
            "- Trainer data: classes, battle parties, portraits\n"
            "- Type data: type chart and badge presentation\n"
            "- World data: heal locations and wild encounters\n"
            "- Build settings: config.mk and ROM build flow\n\n"
            "Project directories exposed by the editor:\n"
            "- src/data/ : game data tables and JSON roots\n"
            "- include/constants/ : enums and constants\n"
            "- graphics/ : sprite, icon, and badge art\n"
            "- data/ : JSON and data tables for world content\n"
        )

        label = tk.Label(
            summary,
            text=text,
            bg=BG_CARD,
            fg=FG_MAIN,
            justify="left",
            font=("Segoe UI", 10),
            wraplength=900,
        )
        label.pack(anchor="w", padx=12, pady=12)

        stats = _CardFrame(self, title="Project status")
        stats.pack(fill=tk.X, padx=16, pady=(0, 14))

        items = [
            ("Species", self._count(ROOT / "include/constants/species.h")),
            ("Moves", self._count(ROOT / "include/constants/moves.h")),
            ("Items", self._count(ROOT / "include/constants/items.h")),
            ("Abilities", self._count(ROOT / "include/constants/abilities.h")),
            ("World JSON", self._count(ROOT / "src/data/wild_encounters.json")),
            ("Graphics", self._count(ROOT / "graphics")),
        ]

        for name, value in items:
            row = tk.Frame(stats, bg=BG_CARD)
            row.pack(fill=tk.X, padx=12, pady=6)
            tk.Label(
                row,
                text=name,
                bg=BG_CARD,
                fg=FG_DIM,
                width=20,
                anchor="w",
                font=("Segoe UI", 10),
            ).pack(side=tk.LEFT)
            tk.Label(
                row, text=value, bg=BG_CARD, fg=FG_GREEN, font=("Segoe UI", 10, "bold")
            ).pack(side=tk.LEFT)

    def _count(self, path):
        try:
            if path.is_dir():
                return str(len(list(path.rglob("*"))))
            if path.exists():
                return str(path.stat().st_size)
            return "0"
        except Exception:
            return "0"
