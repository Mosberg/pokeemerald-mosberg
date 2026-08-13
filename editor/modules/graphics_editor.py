import tkinter as tk
from pathlib import Path
from tkinter import ttk

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
        super().__init__(parent, bg=BG_CARD, bd=0, highlightthickness=1, highlightbackground="#333355", **kw)
        if title:
            tk.Label(self, text=title, bg=BG_CARD, fg=FG_ACCENT, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=8, pady=(6, 2))


class _DarkFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)


class _DarkButton(tk.Button):
    def __init__(self, parent, color=BTN_SAVE, **kw):
        super().__init__(parent, bg=color, fg="white", relief="flat", activebackground=color, activeforeground="white", cursor="hand2", bd=0, font=kw.pop("font", ("Segoe UI", 10, "bold")), **kw)


class GraphicsEditorTab(_DarkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Graphics Editor", bg=BG_DARK, fg=FG_ACCENT, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=16, pady=(16, 8))

        toolbar = tk.Frame(self, bg=BG_DARK)
        toolbar.pack(fill=tk.X, padx=16, pady=(0, 10))

        tk.Label(toolbar, text="Folder:", bg=BG_DARK, fg=FG_DIM, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self._folder_var = tk.StringVar(value="graphics")
        combo = ttk.Combobox(toolbar, textvariable=self._folder_var, values=["graphics", "graphics/pokemon", "graphics/items", "graphics/types", "graphics/trainers", "graphics/character_select"], state="readonly", width=28)
        combo.pack(side=tk.LEFT, padx=8)
        combo.bind("<<ComboboxSelected>>", lambda _: self._reload_files())

        _DarkButton(toolbar, text="↻ Refresh", command=self._reload_files, color="#3a3f5c", padx=16, pady=6).pack(side=tk.LEFT, padx=(8, 0))

        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK, sashwidth=6)
        pane.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        left = tk.Frame(pane, bg="#16213e", width=260)
        pane.add(left, minsize=220)
        tk.Label(left, text="FILES", bg="#16213e", fg=FG_ACCENT, font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._file_list = tk.Listbox(left, bg=BG_INPUT, fg=FG_MAIN, relief="flat", selectbackground="#0f3460", selectforeground=FG_MAIN, activestyle="none", font=("Consolas", 10))
        self._file_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 6))
        self._file_list.bind("<<ListboxSelect>>", self._select_file)

        right = _CardFrame(pane, title="Preview")
        pane.add(right, minsize=500)
        self._preview = tk.Label(right, text="No image selected", bg=BG_CARD, fg=FG_DIM, width=40, height=16, compound="center")
        self._preview.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self._status = tk.Label(self, text="Ready", bg=BG_DARK, fg=FG_GREEN, font=("Segoe UI", 10, "bold"))
        self._status.pack(anchor="w", padx=16, pady=(0, 12))
        self._reload_files()

    def _reload_files(self):
        base = ROOT / self._folder_var.get().replace('/', '\\')
        files = []
        try:
            if base.exists() and base.is_dir():
                for p in sorted(base.rglob('*')):
                    if p.is_file() and p.suffix.lower() in {'.png', '.bmp', '.gif', '.jpg', '.jpeg'}:
                        files.append(str(p.relative_to(ROOT)))
        except Exception as exc:
            self._status.config(text=f"Error loading graphics: {exc}", fg="#ff6b6b")
        self._file_list.delete(0, tk.END)
        for entry in files:
            self._file_list.insert(tk.END, entry)
        self._status.config(text=f"Loaded {len(files)} graphics files", fg=FG_GREEN)

    def _select_file(self, _event=None):
        selection = self._file_list.curselection()
        if not selection:
            return
        rel = self._file_list.get(selection[0])
        path = ROOT / rel
        if not path.exists():
            self._preview.config(text="Missing image", fg="#ff6b6b")
            return
        try:
            from PIL import Image, ImageTk
            img = Image.open(path)
            img.thumbnail((640, 640))
            photo = ImageTk.PhotoImage(img)
            self._preview.config(image=photo, text="", compound="center")
            self._preview.image = photo
            self._status.config(text=f"Preview: {rel}", fg=FG_GREEN)
        except Exception:
            self._preview.config(text=f"{rel}\n\nPreview unavailable\nInstall Pillow for image previews.", fg=FG_MAIN)
            self._status.config(text=f"Preview unavailable for {rel}", fg=FG_DIM)
