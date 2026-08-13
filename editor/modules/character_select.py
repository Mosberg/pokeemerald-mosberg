import json
import tkinter as tk
from pathlib import Path
from tkinter import ttk

try:
    from editor.editor import (
        BG_DARK,
        BG_MED,
        BG_CARD,
        BG_INPUT,
        FG_MAIN,
        FG_DIM,
        FG_ACCENT,
        FG_GREEN,
        FG_GOLD,
        DarkButton,
        DarkEntry,
        CardFrame,
        DarkFrame,
        SearchableList,
    )
except Exception:  # pragma: no cover - fallback for standalone use
    BG_DARK = "#1a1a2e"
    BG_MED = "#16213e"
    BG_CARD = "#1e1e2e"
    BG_INPUT = "#2a2a3e"
    FG_MAIN = "#e0e0f0"
    FG_DIM = "#8888aa"
    FG_ACCENT = "#e94560"
    FG_GREEN = "#4ecca3"
    FG_GOLD = "#f6c90e"

    class DarkButton(tk.Button):
        def __init__(self, parent, color="#2d6a4f", **kw):
            super().__init__(parent, bg=color, fg="white", relief="flat", bd=0, **kw)

    class DarkEntry(tk.Entry):
        def __init__(self, parent, **kw):
            super().__init__(parent, bg=BG_INPUT, fg=FG_MAIN, insertbackground=FG_MAIN, **kw)

    class CardFrame(tk.Frame):
        def __init__(self, parent, title="", **kw):
            super().__init__(parent, bg=BG_CARD, **kw)
            if title:
                tk.Label(self, text=title, bg=BG_CARD, fg=FG_ACCENT).pack(anchor="w", padx=8)

    class DarkFrame(tk.Frame):
        def __init__(self, parent, **kw):
            super().__init__(parent, bg=BG_DARK, **kw)

    class SearchableList(tk.Frame):
        def __init__(self, parent, on_select=None, **kw):
            super().__init__(parent, bg=BG_MED, **kw)
            self._all = []
            self._on_select = on_select
            self._lb = tk.Listbox(self, bg=BG_INPUT, fg=FG_MAIN, height=18)
            self._lb.pack(fill=tk.BOTH, expand=True)
            self._lb.bind("<<ListboxSelect>>", self._select)

        def set_items(self, items):
            self._all = list(items)
            self._lb.delete(0, tk.END)
            for item in self._all:
                self._lb.insert(tk.END, item)

        def _select(self, _):
            if self._on_select and self._lb.curselection():
                self._on_select(self._lb.get(self._lb.curselection()[0]))

        def get_selected(self):
            if not self._lb.curselection():
                return None
            return self._lb.get(self._lb.curselection()[0])

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "character_select_menu.json"
ASSET_DIR = ROOT / "graphics" / "character_select"
GENERATED_DIR = ASSET_DIR / "generated"

TRAINER_PIC_OPTIONS = [
    "TRAINER_PIC_NONE",
    "TRAINER_PIC_BRENDAN",
    "TRAINER_PIC_MAY",
    "TRAINER_PIC_RED",
    "TRAINER_PIC_LEAF",
    "TRAINER_PIC_RS_BRENDAN",
    "TRAINER_PIC_RS_MAY",
    "TRAINER_PIC_WALLY",
    "TRAINER_PIC_STEVEN",
    "TRAINER_PIC_COOLTRAINER_M",
    "TRAINER_PIC_COOLTRAINER_F",
    "TRAINER_PIC_LASS",
    "TRAINER_PIC_BEAUTY",
    "TRAINER_PIC_AQUA_GRUNT_M",
    "TRAINER_PIC_AQUA_GRUNT_F",
    "TRAINER_PIC_BLACK_BELT",
    "TRAINER_PIC_BIRD_KEEPER",
    "TRAINER_PIC_MAGMA_ADMIN",
    "TRAINER_PIC_POKEFAN_M",
    "TRAINER_PIC_POKEFAN_F",
]

DEFAULT_RECORDS = [
    {
        "id": "brendan",
        "name": "Brendan",
        "gender": "male",
        "trainerPic": "TRAINER_PIC_BRENDAN",
        "className": "Rival",
        "sortOrder": 1,
        "frontAsset": "generated/brendan_front.png",
        "backAsset": "generated/brendan_back.png",
        "description": "Default male rival-style avatar.",
        "tags": ["male", "rival", "default"],
        "isDefault": True,
    },
    {
        "id": "may",
        "name": "May",
        "gender": "female",
        "trainerPic": "TRAINER_PIC_MAY",
        "className": "Rival",
        "sortOrder": 2,
        "frontAsset": "generated/may_front.png",
        "backAsset": "generated/may_back.png",
        "description": "Default female rival-style avatar.",
        "tags": ["female", "rival"],
        "isDefault": False,
    },
    {
        "id": "red",
        "name": "Red",
        "gender": "male",
        "trainerPic": "TRAINER_PIC_RED",
        "className": "Champion",
        "sortOrder": 3,
        "frontAsset": "generated/red_front.png",
        "backAsset": "generated/red_back.png",
        "description": "Classic male trainer look with Kanto styling.",
        "tags": ["male", "classic", "kanto"],
        "isDefault": False,
    },
    {
        "id": "leaf",
        "name": "Leaf",
        "gender": "female",
        "trainerPic": "TRAINER_PIC_LEAF",
        "className": "Champion",
        "sortOrder": 4,
        "frontAsset": "generated/leaf_front.png",
        "backAsset": "generated/leaf_back.png",
        "description": "Classic female trainer look with Kanto styling.",
        "tags": ["female", "classic", "kanto"],
        "isDefault": False,
    },
]


def _ensure_data_file():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        DATA_PATH.write_text(json.dumps({"characters": DEFAULT_RECORDS}, indent=2), encoding="utf-8")


def _load_records():
    _ensure_data_file()
    try:
        payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except Exception:
        payload = {"characters": DEFAULT_RECORDS}
    records = payload.get("characters") or []
    if not records:
        records = DEFAULT_RECORDS
    normalized = []
    for idx, entry in enumerate(records, start=1):
        rec = {
            "id": str(entry.get("id") or f"character_{idx}"),
            "name": str(entry.get("name") or "Unnamed"),
            "gender": str(entry.get("gender") or "male").lower(),
            "trainerPic": str(entry.get("trainerPic") or "TRAINER_PIC_BRENDAN"),
            "className": str(entry.get("className") or "Trainer"),
            "sortOrder": int(entry.get("sortOrder") or idx),
            "frontAsset": str(entry.get("frontAsset") or f"generated/{rec_id(entry, idx)}_front.png"),
            "backAsset": str(entry.get("backAsset") or f"generated/{rec_id(entry, idx)}_back.png"),
            "description": str(entry.get("description") or ""),
            "tags": list(entry.get("tags") or []),
            "isDefault": bool(entry.get("isDefault") or False),
        }
        normalized.append(rec)
    return normalized


def rec_id(entry, idx):
    return str(entry.get("id") or f"character_{idx}")


def _write_records(records):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps({"characters": records}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _create_placeholder_portrait(path: Path, title: str, bg_color: str, accent: str, txt_color: str):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (128, 128), bg_color)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((10, 10, 118, 118), radius=16, fill=bg_color, outline=accent, width=4)
    draw.ellipse((28, 22, 100, 94), fill=accent)
    draw.rounded_rectangle((36, 92, 92, 110), radius=8, fill=txt_color)
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font = ImageFont.load_default()
    draw.text((20, 100), title[:10], font=font, fill=txt_color)
    img.save(path)
    return True


def ensure_character_assets(record):
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    rec_id_ = str(record.get("id") or "character")
    front = ASSET_DIR / str(record.get("frontAsset") or f"generated/{rec_id_}_front.png")
    back = ASSET_DIR / str(record.get("backAsset") or f"generated/{rec_id_}_back.png")
    if not front.is_absolute():
        front = ROOT / front
    if not back.is_absolute():
        back = ROOT / back

    if not front.exists():
        _create_placeholder_portrait(front, rec_id_.upper()[:8], "#1a1a2e", "#e94560", "#e0e0f0")
    if not back.exists():
        _create_placeholder_portrait(back, rec_id_.upper()[:8], "#16213e", "#4ecca3", "#e0e0f0")
    return str(front.relative_to(ROOT)), str(back.relative_to(ROOT))


def load_character_preview(record, size=(128, 128)):
    try:
        from PIL import Image, ImageTk
    except Exception:
        return None
    front_path = ROOT / str(record.get("frontAsset") or "")
    if not front_path.exists() or not str(record.get("frontAsset") or "").strip():
        front_path = GENERATED_DIR / f"{record.get('id', 'character')}_front.png"
    try:
        img = Image.open(front_path).convert("RGBA")
        img = img.resize(size, Image.NEAREST)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class CharacterSelectTab(DarkFrame):
    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.app = app
        self._records = []
        self._current = None
        self._preview_ref = None
        self._build_ui()
        self._load_records()

    def _build_ui(self):
        tk.Label(
            self,
            text="Character Select Editor",
            bg=BG_DARK,
            fg=FG_ACCENT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=16, pady=(16, 8))

        toolbar = tk.Frame(self, bg=BG_DARK)
        toolbar.pack(fill=tk.X, padx=16, pady=(0, 10))

        self._new_btn = DarkButton(toolbar, text="＋ New", command=self._new_record, color="#3f51b5")
        self._new_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._save_btn = DarkButton(toolbar, text="💾 Save", command=self._save_records, color="#2d6a4f")
        self._save_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._dup_btn = DarkButton(toolbar, text="⧉ Duplicate", command=self._duplicate_record, color="#3a3f5c")
        self._dup_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._delete_btn = DarkButton(toolbar, text="🗑 Delete", command=self._delete_record, color="#b71c1c")
        self._delete_btn.pack(side=tk.LEFT, padx=(0, 8))
        self._gen_btn = DarkButton(toolbar, text="🖼 Generate art", command=self._generate_art, color="#006064")
        self._gen_btn.pack(side=tk.LEFT)

        pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK, sashwidth=6)
        pane.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        left = tk.Frame(pane, bg=BG_MED, width=260)
        pane.add(left, minsize=220)
        tk.Label(left, text="SELECTABLE CHARACTERS", bg=BG_MED, fg=FG_ACCENT, font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._list = SearchableList(left, on_select=self._select_record)
        self._list.pack(fill=tk.BOTH, expand=True)

        right = DarkFrame(pane)
        pane.add(right, minsize=640)

        top = DarkFrame(right)
        top.pack(fill=tk.X, padx=12, pady=12)

        preview_card = CardFrame(top, title="Preview")
        preview_card.pack(side=tk.LEFT, padx=(0, 12))
        self._preview_label = tk.Label(preview_card, text="No preview", bg=BG_CARD, fg=FG_DIM, width=16, height=10)
        self._preview_label.pack(padx=12, pady=(2, 8))

        info_card = CardFrame(top, title="Character Details")
        info_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        fields = [
            ("ID", "id", 16),
            ("Display name", "name", 18),
            ("Class", "className", 18),
        ]
        self._vars = {}
        for label, key, width in fields:
            row = tk.Frame(info_card, bg=BG_CARD)
            row.pack(fill=tk.X, padx=8, pady=4)
            tk.Label(row, text=label + ":", bg=BG_CARD, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            var = tk.StringVar()
            self._vars[key] = var
            DarkEntry(row, textvariable=var, width=width, font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=8)

        row = tk.Frame(info_card, bg=BG_CARD)
        row.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(row, text="Gender:", bg=BG_CARD, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._gender_var = tk.StringVar(value="male")
        gender_cb = ttk.Combobox(row, textvariable=self._gender_var, values=["male", "female"], state="readonly", width=12)
        gender_cb.pack(side=tk.LEFT, padx=8)

        default_row = tk.Frame(info_card, bg=BG_CARD)
        default_row.pack(fill=tk.X, padx=8, pady=4)
        self._default_var = tk.BooleanVar(value=False)
        tk.Checkbutton(default_row, text="Default selectable option", variable=self._default_var, bg=BG_CARD, fg=FG_GOLD, selectcolor=BG_INPUT).pack(side=tk.LEFT)

        self._trainer_var = tk.StringVar(value="TRAINER_PIC_BRENDAN")
        trainer_row = tk.Frame(info_card, bg=BG_CARD)
        trainer_row.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(trainer_row, text="Trainer pic:", bg=BG_CARD, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        trainer_cb = ttk.Combobox(trainer_row, textvariable=self._trainer_var, values=TRAINER_PIC_OPTIONS, state="readonly", width=24)
        trainer_cb.pack(side=tk.LEFT, padx=8)

        bottom = tk.Frame(right, bg=BG_DARK)
        bottom.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        asset_card = CardFrame(bottom, title="Asset Settings")
        asset_card.pack(fill=tk.X, pady=(0, 8))
        for lbl, key in [("Front asset", "frontAsset"), ("Back asset", "backAsset")]:
            row = tk.Frame(asset_card, bg=BG_CARD)
            row.pack(fill=tk.X, padx=8, pady=4)
            tk.Label(row, text=lbl + ":", bg=BG_CARD, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT)
            var = tk.StringVar()
            self._vars[key] = var
            DarkEntry(row, textvariable=var, width=40).pack(side=tk.LEFT, padx=8, fill=tk.X, expand=True)

        tags_card = CardFrame(bottom, title="Tags and Notes")
        tags_card.pack(fill=tk.BOTH, expand=True)
        self._tags_var = tk.StringVar()
        DarkEntry(tags_card, textvariable=self._tags_var, width=50).pack(fill=tk.X, padx=8, pady=(4, 8))
        tk.Label(tags_card, text="Description:", bg=BG_CARD, fg=FG_DIM, font=("Segoe UI", 9)).pack(anchor="w", padx=8)
        self._description_widget = tk.Text(tags_card, bg=BG_INPUT, fg=FG_MAIN, insertbackground=FG_MAIN, height=6, relief="flat")
        self._description_widget.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self._status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self._status_var, bg=BG_DARK, fg=FG_GREEN, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=16, pady=(0, 12))
        self._load_records()

    def _load_records(self):
        self._records = _load_records()
        self._list.set_items([record["name"] for record in self._records])
        if self._records:
            self._select_record(self._records[0]["name"])

    def _select_record(self, name):
        by_name = {rec["name"]: rec for rec in self._records}
        rec = by_name.get(name)
        if rec is None:
            return
        self._current = rec
        for key, var in self._vars.items():
            var.set(rec.get(key, ""))
        self._gender_var.set(rec.get("gender", "male"))
        self._default_var.set(bool(rec.get("isDefault")))
        self._trainer_var.set(rec.get("trainerPic") or "TRAINER_PIC_BRENDAN")
        self._tags_var.set(", ".join(rec.get("tags") or []))
        self._description_widget.delete("1.0", tk.END)
        self._description_widget.insert("1.0", rec.get("description") or "")
        self._update_preview(rec)

    def _current_record(self):
        if not self._current:
            return None
        rec = dict(self._current)
        rec["id"] = self._vars["id"].get().strip() or rec.get("id") or "character"
        rec["name"] = self._vars["name"].get().strip() or rec.get("name") or rec["id"]
        rec["className"] = self._vars["className"].get().strip() or rec.get("className") or "Trainer"
        rec["gender"] = self._gender_var.get().strip().lower() or rec.get("gender") or "male"
        rec["trainerPic"] = self._trainer_var.get().strip() or rec.get("trainerPic") or "TRAINER_PIC_BRENDAN"
        rec["frontAsset"] = self._vars["frontAsset"].get().strip() or rec.get("frontAsset") or f"generated/{rec['id']}_front.png"
        rec["backAsset"] = self._vars["backAsset"].get().strip() or rec.get("backAsset") or f"generated/{rec['id']}_back.png"
        rec["description"] = self._description_widget.get("1.0", tk.END).strip()
        rec["tags"] = [tag.strip() for tag in self._tags_var.get().split(",") if tag.strip()]
        rec["isDefault"] = bool(self._default_var.get())
        return rec

    def _update_preview(self, rec):
        try:
            from PIL import Image, ImageTk
        except Exception:
            self._preview_label.config(text="No PIL", fg=FG_DIM)
            return
        photo = load_character_preview(rec, size=(128, 128))
        if photo is None:
            self._preview_label.config(text="No preview", fg=FG_DIM)
            return
        self._preview_ref = photo
        self._preview_label.config(image=photo, text="")

    def _new_record(self):
        record = {
            "id": f"character_{len(self._records) + 1}",
            "name": f"Custom {len(self._records) + 1}",
            "gender": "male",
            "trainerPic": "TRAINER_PIC_BRENDAN",
            "className": "Custom",
            "sortOrder": len(self._records) + 1,
            "frontAsset": f"generated/character_{len(self._records) + 1}_front.png",
            "backAsset": f"generated/character_{len(self._records) + 1}_back.png",
            "description": "Custom avatar created in the editor.",
            "tags": ["custom"],
            "isDefault": False,
        }
        self._records.append(record)
        self._list.set_items([r["name"] for r in self._records])
        self._save_records()
        self._select_record(record["name"])
        self._status_var.set("Created new character")

    def _duplicate_record(self):
        if not self._current:
            return
        rec = dict(self._current)
        rec["id"] = f"{rec['id']}_copy"
        rec["name"] = f"{rec['name']} Copy"
        rec["frontAsset"] = rec["frontAsset"].replace(rec["id"], rec["id"])
        rec["backAsset"] = rec["backAsset"].replace(rec["id"], rec["id"])
        self._records.append(rec)
        self._list.set_items([r["name"] for r in self._records])
        self._save_records()
        self._select_record(rec["name"])
        self._status_var.set("Duplicated character")

    def _delete_record(self):
        if not self._current:
            return
        self._records = [rec for rec in self._records if rec["name"] != self._current["name"]]
        self._list.set_items([r["name"] for r in self._records])
        self._save_records()
        self._status_var.set("Deleted character")

    def _generate_art(self):
        if not self._current:
            return
        rec = self._current_record()
        if not rec:
            return
        ensure_character_assets(rec)
        self._update_preview(rec)
        self._status_var.set(f"Generated art for {rec['name']}")

    def _save_records(self):
        records = []
        for rec in self._records:
            if self._current and rec.get("name") == self._current.get("name"):
                rec = self._current_record() or rec
            records.append(rec)
        for rec in records:
            rec["id"] = str(rec.get("id") or rec.get("name") or "character")
            rec["name"] = str(rec.get("name") or rec["id"]) 
            rec["gender"] = str(rec.get("gender") or "male").lower()
            rec["trainerPic"] = str(rec.get("trainerPic") or "TRAINER_PIC_BRENDAN")
            rec["className"] = str(rec.get("className") or "Trainer")
            rec["sortOrder"] = int(rec.get("sortOrder") or 0)
            rec["frontAsset"] = str(rec.get("frontAsset") or f"generated/{rec['id']}_front.png")
            rec["backAsset"] = str(rec.get("backAsset") or f"generated/{rec['id']}_back.png")
            rec["description"] = str(rec.get("description") or "")
            rec["tags"] = [str(tag).strip() for tag in (rec.get("tags") or []) if str(tag).strip()]
            rec["isDefault"] = bool(rec.get("isDefault"))
            ensure_character_assets(rec)
        _write_records(records)
        self._status_var.set(f"Saved {len(records)} character entries")
        self._records = records
        self._list.set_items([r["name"] for r in self._records])

    def set_data(self, data=None, *args, **kwargs):
        if isinstance(data, list):
            self._records = data
        elif isinstance(data, dict):
            self._records = data.get("characters", [])
        self._list.set_items([r["name"] for r in self._records])
        if self._records:
            self._select_record(self._records[0]["name"])
