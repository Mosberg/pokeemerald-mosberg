import json
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "src" / "data"

BG_DARK = "#1a1a2e"
BG_CARD = "#1e1e2e"
BG_INPUT = "#2a2a3e"
FG_MAIN = "#e0e0f0"
FG_DIM = "#8888aa"
FG_ACCENT = "#e94560"
FG_GREEN = "#4ecca3"
BTN_SAVE = "#2d6a4f"


class _CardFrame(tk.Frame):
    def __init__(self, parent, title="", **kw):
        super().__init__(
            parent,
            bg=BG_CARD,
            bd=0,
            highlightthickness=1,
            highlightbackground="#333355",
            **kw,
        )
        if title:
            tk.Label(
                self, text=title, bg=BG_CARD, fg=FG_ACCENT, font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", padx=8, pady=(6, 2))


class _DarkFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)


class _DarkButton(tk.Button):
    def __init__(self, parent, color=BTN_SAVE, **kw):
        super().__init__(
            parent,
            bg=color,
            fg="white",
            relief="flat",
            activebackground=color,
            activeforeground="white",
            cursor="hand2",
            bd=0,
            font=kw.pop("font", ("Segoe UI", 10, "bold")),
            **kw,
        )


class WorldDataTab(_DarkFrame):
    """Edit the JSON-backed world definitions such as wild encounters and heal locations."""

    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.app = app
        self._selected_file = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="World Content Editor",
            bg=BG_DARK,
            fg=FG_ACCENT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        toolbar = tk.Frame(self, bg=BG_DARK)
        toolbar.pack(fill=tk.X, padx=16, pady=(0, 10))

        tk.Label(
            toolbar, text="Data file:", bg=BG_DARK, fg=FG_DIM, font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)
        self._file_var = tk.StringVar(value="wild_encounters.json")
        combo = ttk.Combobox(
            toolbar,
            textvariable=self._file_var,
            values=["wild_encounters.json", "heal_locations.json"],
            state="readonly",
            width=28,
        )
        combo.pack(side=tk.LEFT, padx=8)
        combo.bind("<<ComboboxSelected>>", lambda _: self._load_file())

        _DarkButton(
            toolbar,
            text="↻ Reload",
            command=self._load_file,
            color="#3a3f5c",
            padx=16,
            pady=6,
        ).pack(side=tk.LEFT, padx=(8, 0))
        _DarkButton(
            toolbar,
            text="💾 Save",
            command=self._save_file,
            color=BTN_SAVE,
            padx=16,
            pady=6,
        ).pack(side=tk.LEFT, padx=(8, 0))

        card = _CardFrame(self, title="JSON data")
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self._text = scrolledtext.ScrolledText(
            card,
            font=("Consolas", 10),
            bg=BG_INPUT,
            fg=FG_MAIN,
            insertbackground=FG_MAIN,
            wrap=tk.WORD,
            relief="flat",
            padx=6,
            pady=6,
        )
        self._text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self._status = tk.Label(
            self, text="Ready", bg=BG_DARK, fg=FG_GREEN, font=("Segoe UI", 10, "bold")
        )
        self._status.pack(anchor="w", padx=16, pady=(0, 10))
        self._load_file()

    def _load_file(self):
        name = self._file_var.get().strip()
        path = DATA_ROOT / name
        self._selected_file = path
        try:
            if not path.exists():
                raise FileNotFoundError(path)
            data = json.loads(path.read_text(encoding="utf-8"))
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", json.dumps(data, indent=2, ensure_ascii=False))
            self._status.config(text=f"Loaded {name}", fg=FG_GREEN)
        except Exception as exc:
            self._status.config(text=f"Error loading {name}: {exc}", fg="#ff6b6b")

    def _save_file(self):
        if not self._selected_file:
            return
        try:
            text = self._text.get("1.0", tk.END)
            parsed = json.loads(text)
            self._selected_file.write_text(
                json.dumps(parsed, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            self._status.config(text=f"Saved {self._selected_file.name}", fg=FG_GREEN)
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))
            self._status.config(
                text=f"Error saving {self._selected_file.name}: {exc}", fg="#ff6b6b"
            )
