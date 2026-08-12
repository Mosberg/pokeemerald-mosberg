import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext

ROOT = Path(__file__).resolve().parents[2]

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


class ProjectSettingsTab(_DarkFrame):
    """Edit project build settings in config.mk."""

    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self,
            text="Project Settings",
            bg=BG_DARK,
            fg=FG_ACCENT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))
        tk.Label(
            self,
            text="Tune the build and toolchain defaults for repeated project builds.",
            bg=BG_DARK,
            fg=FG_DIM,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=16, pady=(0, 12))

        card = _CardFrame(self, title="config.mk")
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

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

        btn_row = _DarkFrame(self)
        btn_row.pack(fill=tk.X, padx=16, pady=(0, 10))
        _DarkButton(
            btn_row,
            text="↻ Reload",
            command=self._reload,
            color="#3a3f5c",
            padx=18,
            pady=8,
        ).pack(side=tk.LEFT)
        _DarkButton(
            btn_row, text="💾 Save", command=self._save, color=BTN_SAVE, padx=18, pady=8
        ).pack(side=tk.LEFT, padx=8)

        self._status = tk.Label(
            self, text="Ready", bg=BG_DARK, fg=FG_GREEN, font=("Segoe UI", 10, "bold")
        )
        self._status.pack(anchor="w", padx=16, pady=(0, 12))
        self._reload()

    def _reload(self):
        path = ROOT / "config.mk"
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", text)
            self._status.config(text="Loaded config.mk", fg=FG_GREEN)
        except Exception as exc:
            self._status.config(text=f"Error loading config: {exc}", fg="#ff6b6b")

    def _save(self):
        path = ROOT / "config.mk"
        try:
            path.write_text(self._text.get("1.0", tk.END), encoding="utf-8")
            self._status.config(text="Saved config.mk", fg=FG_GREEN)
        except Exception as exc:
            self._status.config(text=f"Error saving config: {exc}", fg="#ff6b6b")
