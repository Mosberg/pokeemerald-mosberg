"""
pokeemerald-expansion Editor — Improved GUI with full graphics support.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import parser as pparser
import writer
import images as img_util

ROOT = Path(__file__).parent.parent

# ── Theme colours ──────────────────────────────────────────────────────────────
BG_DARK   = "#1a1a2e"
BG_MED    = "#16213e"
BG_PANEL  = "#0f3460"
BG_CARD   = "#1e1e2e"
BG_INPUT  = "#2a2a3e"
FG_MAIN   = "#e0e0f0"
FG_DIM    = "#8888aa"
FG_ACCENT = "#e94560"
FG_GREEN  = "#4ecca3"
FG_GOLD   = "#f6c90e"
BTN_SAVE  = "#2d6a4f"
BTN_BUILD = "#1565c0"
BTN_CLEAN = "#b71c1c"

TYPE_COLORS = {
    "NORMAL": "#A8A878", "FIGHTING": "#C03028", "FLYING": "#A890F0",
    "POISON": "#A040A0", "GROUND": "#E0C068", "ROCK": "#B8A038",
    "BUG": "#A8B820", "GHOST": "#705898", "STEEL": "#B8B8D0",
    "MYSTERY": "#68A090", "FIRE": "#F08030", "WATER": "#6890F0",
    "GRASS": "#78C850", "ELECTRIC": "#F8D030", "PSYCHIC": "#F85888",
    "ICE": "#98D8D8", "DRAGON": "#7038F8", "DARK": "#705848",
    "FAIRY": "#EE99AC", "STELLAR": "#40B5A5", "NONE": "#888888",
}

STAT_DEFS = [
    ("baseHP",        "HP",      "#ff6b6b", 255),
    ("baseAttack",    "Attack",  "#ffa06a", 255),
    ("baseDefense",   "Defense", "#ffd93d", 255),
    ("baseSpAttack",  "Sp.Atk",  "#6bcbff", 255),
    ("baseSpDefense", "Sp.Def",  "#95e57a", 255),
    ("baseSpeed",     "Speed",   "#ff96c8", 255),
]


def _apply_theme(widget):
    try:
        widget.configure(bg=BG_DARK, fg=FG_MAIN)
    except Exception:
        pass


# ── Reusable Widgets ───────────────────────────────────────────────────────────

class DarkFrame(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_DARK, **kw)


class CardFrame(tk.Frame):
    def __init__(self, parent, title="", **kw):
        super().__init__(parent, bg=BG_CARD, bd=0, highlightthickness=1,
                         highlightbackground="#333355", **kw)
        if title:
            tk.Label(self, text=title, bg=BG_CARD, fg=FG_ACCENT,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=8, pady=(6, 2))


class DarkLabel(tk.Label):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=kw.pop("bg", BG_DARK), fg=kw.pop("fg", FG_MAIN), **kw)


class DarkEntry(tk.Entry):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG_INPUT, fg=FG_MAIN,
                         insertbackground=FG_MAIN, relief="flat",
                         highlightthickness=1, highlightbackground="#444466",
                         font=kw.pop("font", ("Segoe UI", 10)), **kw)


class DarkButton(tk.Button):
    def __init__(self, parent, color=BTN_SAVE, **kw):
        super().__init__(parent, bg=color, fg="white", relief="flat",
                         activebackground=color, activeforeground="white",
                         cursor="hand2", bd=0,
                         font=kw.pop("font", ("Segoe UI", 10, "bold")), **kw)


class SearchableList(tk.Frame):
    """Dark-themed searchable listbox."""
    def __init__(self, parent, on_select=None, **kw):
        super().__init__(parent, bg=BG_MED, **kw)
        self._all = []
        self._on_select = on_select

        search_row = tk.Frame(self, bg=BG_MED)
        search_row.pack(fill=tk.X, padx=4, pady=(4, 0))
        tk.Label(search_row, text="🔍", bg=BG_MED, fg=FG_DIM).pack(side=tk.LEFT)
        self._sv = tk.StringVar()
        self._sv.trace_add("write", self._filter)
        tk.Entry(search_row, textvariable=self._sv, bg=BG_INPUT, fg=FG_MAIN,
                 insertbackground=FG_MAIN, relief="flat", font=("Segoe UI", 10),
                 highlightthickness=1, highlightbackground="#444466").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4), pady=4)

        self._count_var = tk.StringVar()
        tk.Label(self, textvariable=self._count_var, bg=BG_MED, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(anchor="e", padx=6)

        lb_frame = tk.Frame(self, bg=BG_MED)
        lb_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
        self._lb = tk.Listbox(lb_frame, bg=BG_INPUT, fg=FG_MAIN, relief="flat",
                              selectbackground=BG_PANEL, selectforeground=FG_GREEN,
                              activestyle="none", font=("Consolas", 10), bd=0,
                              highlightthickness=0)
        sb = ttk.Scrollbar(lb_frame, orient=tk.VERTICAL, command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._lb.bind("<<ListboxSelect>>", self._sel)

    def _filter(self, *_):
        q = self._sv.get().lower()
        filtered = [x for x in self._all if q in x.lower()]
        self._lb.delete(0, tk.END)
        for x in filtered:
            self._lb.insert(tk.END, x)
        self._count_var.set(f"{len(filtered)} / {len(self._all)}")

    def _sel(self, _):
        sel = self._lb.curselection()
        if sel and self._on_select:
            self._on_select(self._lb.get(sel[0]))

    def set_items(self, items):
        self._all = list(items)
        self._filter()

    def get_selected(self):
        sel = self._lb.curselection()
        return self._lb.get(sel[0]) if sel else None

    def select(self, name):
        items = list(self._lb.get(0, tk.END))
        if name in items:
            idx = items.index(name)
            self._lb.selection_clear(0, tk.END)
            self._lb.selection_set(idx)
            self._lb.see(idx)


class TypeBadge(tk.Label):
    """A colored type badge label that shows type icon if available."""
    def __init__(self, parent, type_name="NONE", size=(64, 22), **kw):
        super().__init__(parent, bd=0, cursor="arrow", **kw)
        self._size = size
        self._img_ref = None
        self.set_type(type_name)

    def set_type(self, type_name):
        self._type = type_name
        # Try real icon first
        icon = img_util.get_type_icon(type_name, self._size)
        if icon:
            self.configure(image=icon, bg=BG_DARK, text="")
            self._img_ref = icon
        else:
            badge = img_util.make_type_badge_image(type_name, self._size[0], self._size[1])
            self.configure(image=badge, bg=BG_DARK, text="")
            self._img_ref = badge


class StatRow(tk.Frame):
    """A stat label + entry + bar row."""
    def __init__(self, parent, label, field, color, max_val=255):
        super().__init__(parent, bg=BG_CARD)
        self._field = field
        self._color = color
        self._max_val = max_val
        self._var = tk.StringVar(value="0")

        tk.Label(self, text=label, bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9), width=8, anchor="e").pack(side=tk.LEFT, padx=(0, 4))
        self._val_lbl = tk.Label(self, textvariable=self._var, bg=BG_CARD, fg=FG_MAIN,
                                  font=("Consolas", 10, "bold"), width=4, anchor="e")
        self._val_lbl.pack(side=tk.LEFT)
        self._entry = DarkEntry(self, textvariable=self._var, width=5,
                                 font=("Consolas", 10), justify="right")
        self._entry.pack(side=tk.LEFT, padx=4)

        self._bar_canvas = tk.Canvas(self, height=14, bg="#2a2a3e",
                                      highlightthickness=0, bd=0)
        self._bar_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        self._bar_canvas.bind("<Configure>", self._redraw_bar)
        self._var.trace_add("write", lambda *_: self._redraw_bar())

    def _redraw_bar(self, *_):
        self._bar_canvas.delete("all")
        try:
            val = int(self._var.get())
        except ValueError:
            val = 0
        w = self._bar_canvas.winfo_width()
        h = self._bar_canvas.winfo_height()
        if w <= 1:
            return
        fill_w = max(1, int(w * min(val, self._max_val) / self._max_val))
        # Determine color based on value
        if val < 50:
            bar_color = "#e74c3c"
        elif val < 80:
            bar_color = "#f39c12"
        elif val < 100:
            bar_color = "#27ae60"
        elif val < 150:
            bar_color = self._color
        else:
            bar_color = FG_GOLD
        self._bar_canvas.create_rectangle(0, 2, fill_w, h-2, fill=bar_color, outline="")

    def get_value(self):
        return self._var.get()

    def set_value(self, v):
        self._var.set(str(v))
        self.after(10, self._redraw_bar)

    def bind_change(self, callback):
        self._var.trace_add("write", lambda *_: callback())


# ── Pokémon Tab ────────────────────────────────────────────────────────────────

class PokemonTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._data = {}
        self._abilities_data = {}
        self._current = None
        self._shiny = False
        self._img_ref = None
        self._stat_rows = {}
        self._build_ui()

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                               sashwidth=6, sashrelief=tk.FLAT, sashpad=2)
        paned.pack(fill=tk.BOTH, expand=True)

        # ── Left sidebar ──
        left = tk.Frame(paned, bg=BG_MED, width=210)
        paned.add(left, minsize=180)
        tk.Label(left, text="POKÉMON", bg=BG_MED, fg=FG_ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._list = SearchableList(left, on_select=self._load_species)
        self._list.pack(fill=tk.BOTH, expand=True)

        # ── Right panel ──
        right = DarkFrame(paned)
        paned.add(right, minsize=550)

        # Top: sprite + header info side by side
        top_row = DarkFrame(right)
        top_row.pack(fill=tk.X, padx=12, pady=10)

        # Sprite card
        sprite_card = CardFrame(top_row, title="Sprite")
        sprite_card.pack(side=tk.LEFT, padx=(0, 12))

        self._sprite_lbl = tk.Label(sprite_card, bg=BG_CARD, width=10, height=7,
                                     text="No sprite", fg=FG_DIM,
                                     font=("Segoe UI", 9))
        self._sprite_lbl.pack(padx=12, pady=(2, 6))

        shiny_row = tk.Frame(sprite_card, bg=BG_CARD)
        shiny_row.pack(pady=(0, 6))
        self._shiny_var = tk.BooleanVar(value=False)
        tk.Checkbutton(shiny_row, text="✨ Shiny", variable=self._shiny_var,
                       bg=BG_CARD, fg=FG_GOLD, selectcolor=BG_INPUT,
                       activebackground=BG_CARD, activeforeground=FG_GOLD,
                       command=self._toggle_shiny,
                       font=("Segoe UI", 9)).pack()

        # Nat dex badge
        self._dex_lbl = tk.Label(sprite_card, text="#???", bg=BG_CARD, fg=FG_DIM,
                                  font=("Consolas", 10, "bold"))
        self._dex_lbl.pack(pady=(0, 6))

        # Header info
        info_card = CardFrame(top_row, title="Basic Info")
        info_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        row1 = DarkFrame(info_card)
        row1.configure(bg=BG_CARD)
        row1.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(row1, text="Species Name:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._name_var = tk.StringVar()
        DarkEntry(row1, textvariable=self._name_var, width=18,
                  font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=8)

        row2 = tk.Frame(info_card, bg=BG_CARD)
        row2.pack(fill=tk.X, padx=8, pady=4)
        tk.Label(row2, text="Category:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._cat_var = tk.StringVar()
        DarkEntry(row2, textvariable=self._cat_var, width=14).pack(side=tk.LEFT, padx=8)
        tk.Label(row2, text="Pokémon", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)

        # Types
        type_row = tk.Frame(info_card, bg=BG_CARD)
        type_row.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(type_row, text="Types:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self._type1_var = tk.StringVar()
        self._type2_var = tk.StringVar()
        self._type1_badge = TypeBadge(type_row, bg=BG_DARK, size=(72, 24))
        self._type1_badge.pack(side=tk.LEFT, padx=(8, 4))
        self._type2_badge = TypeBadge(type_row, bg=BG_DARK, size=(72, 24))
        self._type2_badge.pack(side=tk.LEFT, padx=4)

        self._type1_cb = ttk.Combobox(type_row, textvariable=self._type1_var,
                                       width=11, state="readonly")
        self._type1_cb.pack(side=tk.LEFT, padx=(12, 4))
        self._type1_cb.bind("<<ComboboxSelected>>", lambda e: (
            self._type1_badge.set_type(self._type1_var.get()),
        ))
        self._type2_cb = ttk.Combobox(type_row, textvariable=self._type2_var,
                                       width=11, state="readonly")
        self._type2_cb.pack(side=tk.LEFT, padx=4)
        self._type2_cb.bind("<<ComboboxSelected>>", lambda e: (
            self._type2_badge.set_type(self._type2_var.get()),
        ))

        # Abilities
        ab_card = CardFrame(info_card, title="Abilities")
        ab_card.configure(bg=BG_CARD)
        ab_card.pack(fill=tk.X, padx=8, pady=4)

        ab_row = tk.Frame(ab_card, bg=BG_CARD)
        ab_row.pack(fill=tk.X, padx=6, pady=4)
        self._ab_vars = [tk.StringVar(), tk.StringVar(), tk.StringVar()]
        self._ab_cbs = []
        self._ab_desc_lbls = []
        for i, lbl in enumerate(["Ability 1", "Ability 2", "Hidden"]):
            col = tk.Frame(ab_row, bg=BG_CARD)
            col.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)
            tk.Label(col, text=lbl, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 8)).pack(anchor="w")
            cb = ttk.Combobox(col, textvariable=self._ab_vars[i], width=18, state="readonly")
            cb.pack(fill=tk.X)
            cb.bind("<<ComboboxSelected>>", lambda e, idx=i: self._update_ab_desc(idx))
            self._ab_cbs.append(cb)
            desc = tk.Label(col, text="", bg=BG_CARD, fg=FG_DIM,
                            font=("Segoe UI", 8), wraplength=160, justify="left")
            desc.pack(anchor="w", pady=(2, 0))
            self._ab_desc_lbls.append(desc)

        # ── Stats ──
        stats_card = CardFrame(right, title="Base Stats")
        stats_card.pack(fill=tk.X, padx=12, pady=(0, 6))

        self._bst_var = tk.StringVar(value="BST: 0")
        tk.Label(stats_card, textvariable=self._bst_var, bg=BG_CARD, fg=FG_GOLD,
                 font=("Segoe UI", 10, "bold")).pack(anchor="e", padx=8)

        for field, label, color, max_val in STAT_DEFS:
            row = StatRow(stats_card, label, field, color, max_val)
            row.pack(fill=tk.X, padx=8, pady=2)
            row.bind_change(self._update_bst)
            self._stat_rows[field] = row

        # ── Other info ──
        other_card = CardFrame(right, title="Additional Info")
        other_card.pack(fill=tk.X, padx=12, pady=(0, 6))

        other_inner = tk.Frame(other_card, bg=BG_CARD)
        other_inner.pack(fill=tk.X, padx=8, pady=6)
        self._other_vars = {}
        for col_idx, (label, field, tip) in enumerate([
            ("Catch Rate", "catchRate", "0-255"),
            ("Height (dm)", "height", "e.g. 7 = 0.7m"),
            ("Weight (hg)", "weight", "e.g. 69 = 6.9kg"),
            ("Friendship", "friendship", "0-255, 70=standard"),
        ]):
            cell = tk.Frame(other_inner, bg=BG_CARD)
            cell.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)
            tk.Label(cell, text=label, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 8)).pack(anchor="w")
            var = tk.StringVar()
            self._other_vars[field] = var
            DarkEntry(cell, textvariable=var, width=8, justify="center").pack(fill=tk.X)
            tk.Label(cell, text=tip, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 7)).pack(anchor="w")

        # ── Pokédex description ──
        desc_card = CardFrame(right, title="Pokédex Description")
        desc_card.pack(fill=tk.X, padx=12, pady=(0, 6))
        self._desc_text = tk.Text(desc_card, height=4, font=("Segoe UI", 10),
                                   bg=BG_INPUT, fg=FG_MAIN, insertbackground=FG_MAIN,
                                   relief="flat", wrap=tk.WORD, padx=4, pady=4)
        self._desc_text.pack(fill=tk.X, padx=8, pady=(0, 8))

        # ── Save button ──
        btn_frame = DarkFrame(right)
        btn_frame.pack(fill=tk.X, padx=12, pady=6)
        DarkButton(btn_frame, text="💾  Save Changes", command=self._save,
                   color=BTN_SAVE, padx=20, pady=8).pack(side=tk.LEFT)
        self._status_lbl = tk.Label(btn_frame, text="", bg=BG_DARK, fg=FG_GREEN,
                                     font=("Segoe UI", 10))
        self._status_lbl.pack(side=tk.LEFT, padx=12)

    def _update_bst(self):
        try:
            total = sum(int(self._stat_rows[f].get_value() or 0)
                        for f, *_ in STAT_DEFS)
            self._bst_var.set(f"BST: {total}")
        except ValueError:
            pass

    def _update_ab_desc(self, idx):
        ab_name = self._ab_vars[idx].get()
        info = self._abilities_data.get(ab_name, {})
        desc = info.get('description', '')
        self._ab_desc_lbls[idx].config(text=desc)

    def _toggle_shiny(self):
        self._shiny = self._shiny_var.get()
        if self._current:
            self._load_sprite(self._current, self._shiny)

    def _load_sprite(self, species_name, shiny=False):
        sprite = img_util.get_pokemon_front(species_name, size=(128, 128), shiny=shiny)
        if sprite:
            self._sprite_lbl.configure(image=sprite, text="", width=0, height=0)
            self._img_ref = sprite
        else:
            # Try icon as fallback
            icon = img_util.get_pokemon_icon(species_name, size=(64, 64), shiny=shiny)
            if icon:
                self._sprite_lbl.configure(image=icon, text="", width=0, height=0)
                self._img_ref = icon
            else:
                self._sprite_lbl.configure(image="", text=f"No sprite\n{species_name}",
                                            width=12, height=6)
                self._img_ref = None

    def set_data(self, data, types, abilities, abilities_data):
        self._data = data
        self._abilities_data = abilities_data
        ab_names = sorted(abilities)
        type_names = types

        self._type1_cb['values'] = type_names
        self._type2_cb['values'] = type_names
        for cb in self._ab_cbs:
            cb['values'] = ab_names

        self._list.set_items(sorted(data.keys()))

    def _load_species(self, name):
        self._current = name
        fields = self._data.get(name, {})

        self._name_var.set(fields.get('speciesName', name))
        self._cat_var.set(fields.get('categoryName', ''))

        dex = fields.get('natDexNum', '')
        self._dex_lbl.config(text=f"#{dex}" if dex else "#???")

        t1 = fields.get('type1', 'NORMAL')
        t2 = fields.get('type2', t1)
        self._type1_var.set(t1)
        self._type2_var.set(t2)
        self._type1_badge.set_type(t1)
        self._type2_badge.set_type(t2)

        for i, key in enumerate(['ability1', 'ability2', 'abilityH']):
            ab = fields.get(key, 'NONE')
            self._ab_vars[i].set(ab)
            self._update_ab_desc(i)

        for field, *_ in STAT_DEFS:
            self._stat_rows[field].set_value(fields.get(field, '0'))

        for field in ['catchRate', 'height', 'weight']:
            self._other_vars[field].set(fields.get(field, '0'))

        fr = fields.get('friendship', '70')
        if 'STANDARD' in str(fr):
            fr = '70'
        self._other_vars['friendship'].set(fr)

        self._desc_text.delete("1.0", tk.END)
        self._desc_text.insert("1.0", fields.get('description', ''))

        self._status_lbl.config(text="")
        self._update_bst()

        # Load sprite in background to avoid UI freeze
        threading.Thread(target=self._bg_load_sprite, args=(name,), daemon=True).start()

    def _bg_load_sprite(self, name):
        shiny = self._shiny_var.get()
        img_util.get_pokemon_front(name, size=(128, 128), shiny=shiny)
        self.after(0, self._load_sprite, name, shiny)

    def _save(self):
        if not self._current:
            return
        fields = {
            'speciesName': self._name_var.get(),
            'categoryName': self._cat_var.get(),
            'type1': self._type1_var.get(),
            'type2': self._type2_var.get(),
            'ability1': self._ab_vars[0].get(),
            'ability2': self._ab_vars[1].get(),
            'abilityH': self._ab_vars[2].get(),
        }
        for field, *_ in STAT_DEFS:
            try:
                fields[field] = int(self._stat_rows[field].get_value())
            except ValueError:
                pass
        for field in ['catchRate', 'height', 'weight', 'friendship']:
            try:
                fields[field] = int(self._other_vars[field].get())
            except ValueError:
                pass

        source = self._data.get(self._current, {}).get('_source_file')
        try:
            writer.save_species(self._current, fields, source)
            self._data[self._current].update(fields)
            self._status_lbl.config(text="✓ Saved!", fg=FG_GREEN)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            self._status_lbl.config(text="✗ Error", fg=FG_ACCENT)


# ── Moves Tab ──────────────────────────────────────────────────────────────────

class MovesTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._data = {}
        self._current = None
        self._build_ui()

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                               sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(paned, bg=BG_MED, width=210)
        paned.add(left, minsize=180)
        tk.Label(left, text="MOVES", bg=BG_MED, fg=FG_ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._list = SearchableList(left, on_select=self._load_move)
        self._list.pack(fill=tk.BOTH, expand=True)

        right = DarkFrame(paned)
        paned.add(right, minsize=500)

        # Header row with name + type badge + category
        header = CardFrame(right, title="Move Info")
        header.pack(fill=tk.X, padx=12, pady=10)

        row1 = tk.Frame(header, bg=BG_CARD)
        row1.pack(fill=tk.X, padx=8, pady=6)
        tk.Label(row1, text="Name:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._name_var = tk.StringVar()
        DarkEntry(row1, textvariable=self._name_var, width=20,
                  font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=8)

        row2 = tk.Frame(header, bg=BG_CARD)
        row2.pack(fill=tk.X, padx=8, pady=(0, 8))

        tk.Label(row2, text="Type:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._type_var = tk.StringVar()
        self._type_badge = TypeBadge(row2, bg=BG_DARK, size=(72, 24))
        self._type_badge.pack(side=tk.LEFT, padx=(8, 4))
        self._type_cb = ttk.Combobox(row2, textvariable=self._type_var, width=12, state="readonly")
        self._type_cb.pack(side=tk.LEFT, padx=(4, 20))
        self._type_cb.bind("<<ComboboxSelected>>", lambda e: self._type_badge.set_type(self._type_var.get()))

        tk.Label(row2, text="Category:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._cat_var = tk.StringVar()
        self._cat_cb = ttk.Combobox(row2, textvariable=self._cat_var, width=11, state="readonly",
                                     values=["PHYSICAL", "SPECIAL", "STATUS"])
        self._cat_cb.pack(side=tk.LEFT, padx=8)
        self._cat_cb.bind("<<ComboboxSelected>>", lambda e: self._update_cat_badge())

        self._cat_badge = tk.Label(row2, text="", bg=BG_CARD, fg=FG_MAIN,
                                    font=("Segoe UI", 9, "bold"), padx=8, pady=3)
        self._cat_badge.pack(side=tk.LEFT, padx=4)

        # Stats
        stats_card = CardFrame(right, title="Move Stats")
        stats_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        inner = tk.Frame(stats_card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=8, pady=8)

        self._move_vars = {}
        stat_data = [
            ("Power", "power", "0 = status", "#f08030"),
            ("Accuracy", "accuracy", "0 = always hits", "#6890f0"),
            ("PP", "pp", "max power points", "#78c850"),
            ("Priority", "priority", "-6 to +5", "#f85888"),
        ]
        for i, (label, field, tip, color) in enumerate(stat_data):
            cell = tk.Frame(inner, bg=BG_CARD)
            cell.grid(row=i // 2, column=i % 2, padx=16, pady=6, sticky="w")
            tk.Label(cell, text=label, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 9)).pack(anchor="w")
            var = tk.StringVar()
            self._move_vars[field] = var
            entry = DarkEntry(cell, textvariable=var, width=7,
                               font=("Consolas", 12, "bold"), justify="center")
            entry.pack(pady=2)
            tk.Label(cell, text=tip, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 7)).pack(anchor="w")

        # Power bar
        pb_frame = tk.Frame(stats_card, bg=BG_CARD)
        pb_frame.pack(fill=tk.X, padx=8, pady=(0, 6))
        tk.Label(pb_frame, text="Power:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._power_canvas = tk.Canvas(pb_frame, height=12, bg="#2a2a3e",
                                        highlightthickness=0, bd=0)
        self._power_canvas.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
        self._power_canvas.bind("<Configure>", lambda e: self._update_power_bar())
        self._move_vars['power'].trace_add("write", lambda *_: self._update_power_bar())

        # Description
        desc_card = CardFrame(right, title="Move Description")
        desc_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        self._desc_text = tk.Text(desc_card, height=3, font=("Segoe UI", 10),
                                   bg=BG_INPUT, fg=FG_MAIN, insertbackground=FG_MAIN,
                                   relief="flat", wrap=tk.WORD, padx=4, pady=4)
        self._desc_text.pack(fill=tk.X, padx=8, pady=(0, 8))

        # Save
        btn_frame = DarkFrame(right)
        btn_frame.pack(fill=tk.X, padx=12, pady=6)
        DarkButton(btn_frame, text="💾  Save Changes", command=self._save,
                   color=BTN_SAVE, padx=20, pady=8).pack(side=tk.LEFT)
        self._status_lbl = tk.Label(btn_frame, text="", bg=BG_DARK, fg=FG_GREEN,
                                     font=("Segoe UI", 10))
        self._status_lbl.pack(side=tk.LEFT, padx=12)

    def _update_cat_badge(self):
        cat = self._cat_var.get()
        colors = {"PHYSICAL": ("#f08030", "⚔ PHYSICAL"),
                  "SPECIAL": ("#6890f0", "✨ SPECIAL"),
                  "STATUS": ("#78c850", "🔧 STATUS")}
        color, text = colors.get(cat, ("#888", cat))
        self._cat_badge.config(text=text, bg=color)

    def _update_power_bar(self):
        self._power_canvas.delete("all")
        try:
            val = int(self._move_vars['power'].get())
        except ValueError:
            return
        w = self._power_canvas.winfo_width()
        if w <= 1:
            return
        fill_w = max(1, int(w * min(val, 250) / 250))
        # Gradient color based on power
        if val == 0:
            color = "#888888"
        elif val < 60:
            color = "#78c850"
        elif val < 100:
            color = "#f08030"
        else:
            color = "#e74c3c"
        self._power_canvas.create_rectangle(0, 0, fill_w, 12, fill=color, outline="")

    def set_data(self, data, types):
        self._data = data
        self._type_cb['values'] = types
        self._list.set_items(sorted(data.keys()))

    def _load_move(self, name):
        self._current = name
        fields = self._data.get(name, {})
        self._name_var.set(fields.get('name', name))
        t = fields.get('type', 'NORMAL')
        self._type_var.set(t)
        self._type_badge.set_type(t)
        cat = fields.get('category', 'PHYSICAL')
        self._cat_var.set(cat)
        self._update_cat_badge()
        for field in ['power', 'accuracy', 'pp', 'priority']:
            self._move_vars[field].set(fields.get(field, '0'))
        self._desc_text.delete("1.0", tk.END)
        self._desc_text.insert("1.0", fields.get('description', ''))
        self._status_lbl.config(text="")
        self.after(50, self._update_power_bar)

    def _save(self):
        if not self._current:
            return
        fields = {
            'name': self._name_var.get(),
            'type': self._type_var.get(),
            'category': self._cat_var.get(),
        }
        for field in ['power', 'accuracy', 'pp', 'priority']:
            try:
                fields[field] = int(self._move_vars[field].get())
            except ValueError:
                pass
        source = self._data.get(self._current, {}).get('_source_file')
        try:
            writer.save_move(self._current, fields, source)
            self._data[self._current].update(fields)
            self._status_lbl.config(text="✓ Saved!", fg=FG_GREEN)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            self._status_lbl.config(text="✗ Error", fg=FG_ACCENT)


# ── Items Tab ──────────────────────────────────────────────────────────────────

class ItemsTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._data = {}
        self._current = None
        self._img_ref = None
        self._build_ui()

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                               sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(paned, bg=BG_MED, width=210)
        paned.add(left, minsize=180)
        tk.Label(left, text="ITEMS", bg=BG_MED, fg=FG_ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._list = SearchableList(left, on_select=self._load_item)
        self._list.pack(fill=tk.BOTH, expand=True)

        right = DarkFrame(paned)
        paned.add(right, minsize=500)

        # Header with icon + name
        header = CardFrame(right, title="Item Info")
        header.pack(fill=tk.X, padx=12, pady=10)

        top_row = tk.Frame(header, bg=BG_CARD)
        top_row.pack(fill=tk.X, padx=8, pady=8)

        # Item icon
        self._icon_lbl = tk.Label(top_row, bg=BG_CARD, width=6, height=4,
                                   text="?", fg=FG_DIM, font=("Segoe UI", 20))
        self._icon_lbl.pack(side=tk.LEFT, padx=(0, 16))

        name_col = tk.Frame(top_row, bg=BG_CARD)
        name_col.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Label(name_col, text="Item Name:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._name_var = tk.StringVar()
        DarkEntry(name_col, textvariable=self._name_var, width=24,
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=4)
        tk.Label(name_col, text="Constant:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(anchor="w")
        self._const_lbl = tk.Label(name_col, text="", bg=BG_CARD, fg=FG_DIM,
                                    font=("Consolas", 9))
        self._const_lbl.pack(anchor="w")

        # Properties
        props_card = CardFrame(right, title="Properties")
        props_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        props_inner = tk.Frame(props_card, bg=BG_CARD)
        props_inner.pack(fill=tk.X, padx=8, pady=8)

        self._prop_vars = {}
        for i, (label, field, tip) in enumerate([
            ("Price", "price", "Buy price (sell = half)"),
            ("Hold Effect", "holdEffect", "Effect when held"),
            ("Effect Param", "holdEffectParam", "Modifier value"),
            ("Pocket", "pocket", "Which bag pocket"),
        ]):
            cell = tk.Frame(props_inner, bg=BG_CARD)
            cell.grid(row=i // 2, column=i % 2, padx=12, pady=6, sticky="w")
            tk.Label(cell, text=label, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 9)).pack(anchor="w")
            var = tk.StringVar()
            self._prop_vars[field] = var
            DarkEntry(cell, textvariable=var, width=22).pack(anchor="w", pady=2)
            tk.Label(cell, text=tip, bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 7)).pack(anchor="w")

        # Description
        desc_card = CardFrame(right, title="Description")
        desc_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        self._desc_lbl = tk.Label(desc_card, text="", bg=BG_CARD, fg=FG_MAIN,
                                   font=("Segoe UI", 10), wraplength=450,
                                   justify="left", pady=4)
        self._desc_lbl.pack(anchor="w", padx=8, pady=(0, 8))

        # Save
        btn_frame = DarkFrame(right)
        btn_frame.pack(fill=tk.X, padx=12, pady=6)
        DarkButton(btn_frame, text="💾  Save Changes", command=self._save,
                   color=BTN_SAVE, padx=20, pady=8).pack(side=tk.LEFT)
        self._status_lbl = tk.Label(btn_frame, text="", bg=BG_DARK, fg=FG_GREEN,
                                     font=("Segoe UI", 10))
        self._status_lbl.pack(side=tk.LEFT, padx=12)

    def set_data(self, data):
        self._data = data
        self._list.set_items(sorted(data.keys()))

    def _load_item(self, name):
        self._current = name
        fields = self._data.get(name, {})
        self._name_var.set(fields.get('name', name))
        self._const_lbl.config(text=f"ITEM_{name}")
        for field in ['price', 'holdEffect', 'holdEffectParam', 'pocket']:
            self._prop_vars[field].set(fields.get(field, ''))
        self._desc_lbl.config(text=fields.get('description', ''))
        self._status_lbl.config(text="")

        # Load item icon in background
        threading.Thread(target=self._bg_load_icon, args=(name,), daemon=True).start()

    def _bg_load_icon(self, name):
        icon = img_util.get_item_icon(name, size=(64, 64))
        self.after(0, self._set_icon, icon)

    def _set_icon(self, icon):
        if icon:
            self._icon_lbl.configure(image=icon, text="", width=0, height=0)
            self._img_ref = icon
        else:
            self._icon_lbl.configure(image="", text="🎒", width=4, height=3)
            self._img_ref = None

    def _save(self):
        if not self._current:
            return
        fields = {'name': self._name_var.get()}
        for field in ['price', 'holdEffectParam']:
            try:
                fields[field] = int(self._prop_vars[field].get())
            except ValueError:
                pass
        source = self._data.get(self._current, {}).get('_source_file')
        try:
            writer.save_item(self._current, fields, source)
            self._data[self._current].update(fields)
            self._status_lbl.config(text="✓ Saved!", fg=FG_GREEN)
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
            self._status_lbl.config(text="✗ Error", fg=FG_ACCENT)


# ── Trainers Tab ───────────────────────────────────────────────────────────────

class TrainersTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._data = {}
        self._current = None
        self._img_ref = None
        self._build_ui()

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                               sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(paned, bg=BG_MED, width=210)
        paned.add(left, minsize=180)
        tk.Label(left, text="TRAINERS", bg=BG_MED, fg=FG_ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._list = SearchableList(left, on_select=self._load_trainer)
        self._list.pack(fill=tk.BOTH, expand=True)

        right = DarkFrame(paned)
        paned.add(right, minsize=500)

        # Trainer card: sprite + info
        header = CardFrame(right, title="Trainer Info")
        header.pack(fill=tk.X, padx=12, pady=10)
        header_row = tk.Frame(header, bg=BG_CARD)
        header_row.pack(fill=tk.X, padx=8, pady=8)

        # Sprite
        self._trainer_sprite = tk.Label(header_row, bg=BG_CARD, text="👤",
                                         font=("Segoe UI", 32), width=4, height=4)
        self._trainer_sprite.pack(side=tk.LEFT, padx=(0, 16))

        info_col = tk.Frame(header_row, bg=BG_CARD)
        info_col.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self._trainer_vars = {}
        for label, field in [
            ("Trainer Name", "trainerName"),
            ("Class", "trainerClass"),
            ("Pic", "trainerPic"),
        ]:
            row = tk.Frame(info_col, bg=BG_CARD)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=f"{label}:", bg=BG_CARD, fg=FG_DIM,
                     width=14, anchor="e", font=("Segoe UI", 9)).pack(side=tk.LEFT)
            var = tk.StringVar()
            self._trainer_vars[field] = var
            DarkEntry(row, textvariable=var, width=24).pack(side=tk.LEFT, padx=8)

        extra_row = tk.Frame(info_col, bg=BG_CARD)
        extra_row.pack(fill=tk.X, pady=3)
        for label, field in [("Gender", "gender"), ("Battle Type", "battleType")]:
            tk.Label(extra_row, text=f"{label}:", bg=BG_CARD, fg=FG_DIM,
                     font=("Segoe UI", 9)).pack(side=tk.LEFT)
            var = tk.StringVar()
            self._trainer_vars[field] = var
            DarkEntry(extra_row, textvariable=var, width=14).pack(side=tk.LEFT, padx=(4, 16))

        # Party
        party_card = CardFrame(right, title="Battle Party")
        party_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        style = ttk.Style()
        style.configure("Dark.Treeview", background=BG_INPUT, foreground=FG_MAIN,
                         fieldbackground=BG_INPUT, rowheight=28)
        style.configure("Dark.Treeview.Heading", background=BG_PANEL, foreground=FG_ACCENT,
                         font=("Segoe UI", 9, "bold"))
        style.map("Dark.Treeview", background=[("selected", BG_PANEL)])

        cols = ("Species", "Level", "Nature", "Item")
        self._party_tree = ttk.Treeview(party_card, columns=cols, show="headings",
                                         height=8, style="Dark.Treeview")
        for col in cols:
            self._party_tree.heading(col, text=col)
            self._party_tree.column(col, width=120)

        party_scroll = ttk.Scrollbar(party_card, orient=tk.VERTICAL,
                                      command=self._party_tree.yview)
        self._party_tree.configure(yscrollcommand=party_scroll.set)
        party_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=8)
        self._party_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Party icons row
        self._party_icon_frame = tk.Frame(right, bg=BG_DARK)
        self._party_icon_frame.pack(fill=tk.X, padx=12)
        self._party_icon_labels = []
        self._party_img_refs = []
        for _ in range(6):
            lbl = tk.Label(self._party_icon_frame, bg=BG_DARK, text="", width=2)
            lbl.pack(side=tk.LEFT, padx=4)
            self._party_icon_labels.append(lbl)
            self._party_img_refs.append(None)

    def set_data(self, data):
        self._data = data
        self._list.set_items(sorted(data.keys()))

    def _load_trainer(self, name):
        self._current = name
        fields = self._data.get(name, {})
        for field in ['trainerName', 'trainerClass', 'trainerPic', 'gender', 'battleType']:
            self._trainer_vars[field].set(fields.get(field, ''))

        # Party tree
        self._party_tree.delete(*self._party_tree.get_children())
        for mon in fields.get('party', []):
            self._party_tree.insert("", tk.END, values=(
                mon.get('species', '?'),
                mon.get('level', '?'),
                mon.get('nature', ''),
                mon.get('item', ''),
            ))

        # Trainer sprite
        trainer_pic = fields.get('trainerPic', '')
        threading.Thread(target=self._bg_load_trainer_sprite,
                         args=(trainer_pic,), daemon=True).start()

        # Party icons
        party = fields.get('party', [])
        for i, lbl in enumerate(self._party_icon_labels):
            if i < len(party):
                species = party[i].get('species', '')
                threading.Thread(target=self._bg_load_party_icon,
                                 args=(i, species), daemon=True).start()
            else:
                lbl.configure(image="", text="", width=2)
                self._party_img_refs[i] = None

    def _bg_load_trainer_sprite(self, trainer_pic):
        sprite = img_util.get_trainer_sprite(trainer_pic, size=(80, 80))
        self.after(0, self._set_trainer_sprite, sprite)

    def _set_trainer_sprite(self, sprite):
        if sprite:
            self._trainer_sprite.configure(image=sprite, text="", width=0, height=0)
            self._img_ref = sprite
        else:
            self._trainer_sprite.configure(image="", text="👤", width=4, height=4)
            self._img_ref = None

    def _bg_load_party_icon(self, idx, species):
        icon = img_util.get_pokemon_icon(species, size=(40, 40))
        self.after(0, self._set_party_icon, idx, icon, species)

    def _set_party_icon(self, idx, icon, species):
        lbl = self._party_icon_labels[idx]
        if icon:
            lbl.configure(image=icon, text="", width=0)
            self._party_img_refs[idx] = icon
        else:
            lbl.configure(image="", text="?", width=2)
            self._party_img_refs[idx] = None


# ── Types Tab ──────────────────────────────────────────────────────────────────

class TypesTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._types = []
        self._effectiveness = {}
        self._type_images = {}
        self._build_ui()

    def _build_ui(self):
        header = DarkFrame(self)
        header.pack(fill=tk.X, padx=12, pady=(10, 4))
        tk.Label(header, text="Type Effectiveness Chart", bg=BG_DARK, fg=FG_ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        tk.Label(header, text="Row = Attacker  ·  Column = Defender",
                 bg=BG_DARK, fg=FG_DIM, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=16)

        # Legend
        leg_frame = DarkFrame(self)
        leg_frame.pack(fill=tk.X, padx=12, pady=(0, 4))
        for text, color, fg in [
            ("2× Super effective", "#4ecca3", BG_DARK),
            ("1× Normal", "#555577", FG_MAIN),
            ("½× Not very effective", "#8B6914", FG_MAIN),
            ("0× Immune", "#333355", FG_DIM),
        ]:
            lbl = tk.Label(leg_frame, text=text, bg=color, fg=fg,
                           font=("Segoe UI", 8), padx=8, pady=2)
            lbl.pack(side=tk.LEFT, padx=4)

        # Canvas
        canvas_container = tk.Frame(self, bg=BG_DARK)
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self._canvas = tk.Canvas(canvas_container, bg=BG_MED, highlightthickness=0)
        hscroll = ttk.Scrollbar(canvas_container, orient=tk.HORIZONTAL, command=self._canvas.xview)
        vscroll = ttk.Scrollbar(canvas_container, orient=tk.VERTICAL, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tooltip
        self._tooltip = tk.Label(self, text="", bg="#ffffe0", fg="#333",
                                  font=("Segoe UI", 9), relief="solid", bd=1)
        self._canvas.bind("<Motion>", self._on_hover)

    def set_types(self, types, effectiveness):
        self._types = [t for t in types if t not in ('MYSTERY',)]
        self._effectiveness = effectiveness
        self.after(100, self._draw_chart)

    def _draw_chart(self):
        self._canvas.delete("all")
        types = self._types
        n = len(types)
        cell = 34
        header_w = 90
        header_h = 90

        total_w = header_w + n * cell
        total_h = header_h + n * cell

        # Draw defender headers (columns)
        for j, t in enumerate(types):
            x = header_w + j * cell
            color = TYPE_COLORS.get(t, "#555")
            self._canvas.create_rectangle(x, 0, x + cell, header_h,
                                           fill=color, outline=BG_DARK, width=1)
            # Draw type name vertically
            short = t[:3] if len(t) > 5 else t
            self._canvas.create_text(x + cell//2, header_h//2, text=short,
                                      font=("Segoe UI", 7, "bold"), fill="white",
                                      angle=90)

        # Draw attacker headers (rows)
        for i, t in enumerate(types):
            y = header_h + i * cell
            color = TYPE_COLORS.get(t, "#555")
            self._canvas.create_rectangle(0, y, header_w, y + cell,
                                           fill=color, outline=BG_DARK, width=1)
            name = t[:7]
            self._canvas.create_text(header_w//2, y + cell//2, text=name,
                                      font=("Segoe UI", 7, "bold"), fill="white")

        # Draw cells
        eff_colors = {
            2.0: "#4ecca3",   # super effective - green
            1.0: "#3a3a5a",   # normal - dark
            0.5: "#8B6914",   # not very effective - brown
            0.0: "#1a1a2e",   # immune - very dark
        }
        eff_texts = {2.0: "2", 1.0: "", 0.5: "½", 0.0: "✕"}

        for i, attacker in enumerate(types):
            for j, defender in enumerate(types):
                x = header_w + j * cell
                y = header_h + i * cell
                mult = self._effectiveness.get((attacker, defender), 1.0)
                color = eff_colors.get(mult, "#3a3a5a")
                self._canvas.create_rectangle(x+1, y+1, x+cell-1, y+cell-1,
                                               fill=color, outline="")
                text = eff_texts.get(mult, str(mult))
                if text:
                    fg = "white" if mult != 0.5 else "#ffcc00"
                    self._canvas.create_text(x + cell//2, y + cell//2, text=text,
                                              font=("Segoe UI", 8, "bold"), fill=fg)

        # Corner
        self._canvas.create_rectangle(0, 0, header_w, header_h, fill=BG_MED, outline="")
        self._canvas.create_text(header_w//2, header_h//2, text="ATK→\nDEF↓",
                                  font=("Segoe UI", 7), fill=FG_DIM, justify="center")

        self._canvas.configure(scrollregion=(0, 0, total_w, total_h))
        self._chart_meta = (header_w, header_h, cell, types)

    def _on_hover(self, event):
        if not hasattr(self, '_chart_meta'):
            return
        header_w, header_h, cell, types = self._chart_meta
        cx = self._canvas.canvasx(event.x)
        cy = self._canvas.canvasy(event.y)
        j = int((cx - header_w) // cell)
        i = int((cy - header_h) // cell)
        if 0 <= i < len(types) and 0 <= j < len(types):
            atk = types[i]
            dfn = types[j]
            mult = self._effectiveness.get((atk, dfn), 1.0)
            labels = {2.0: "Super Effective (2×)", 1.0: "Normal (1×)",
                      0.5: "Not Very Effective (½×)", 0.0: "Immune (0×)"}
            msg = f"{atk} → {dfn}: {labels.get(mult, str(mult))}"
            self._tooltip.config(text=msg)
            self._tooltip.place(x=event.x + 12, y=event.y - 20)
        else:
            self._tooltip.place_forget()


# ── Abilities Tab ──────────────────────────────────────────────────────────────

class AbilitiesTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._data = {}
        self._current = None
        self._build_ui()

    def _build_ui(self):
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=BG_DARK,
                               sashwidth=6, sashrelief=tk.FLAT)
        paned.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(paned, bg=BG_MED, width=210)
        paned.add(left, minsize=180)
        tk.Label(left, text="ABILITIES", bg=BG_MED, fg=FG_ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(pady=(10, 0))
        self._list = SearchableList(left, on_select=self._load_ability)
        self._list.pack(fill=tk.BOTH, expand=True)

        right = DarkFrame(paned)
        paned.add(right, minsize=500)

        info_card = CardFrame(right, title="Ability Info")
        info_card.pack(fill=tk.X, padx=12, pady=10)
        inner = tk.Frame(info_card, bg=BG_CARD)
        inner.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(inner, text="Name:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._name_lbl = tk.Label(inner, text="", bg=BG_CARD, fg=FG_MAIN,
                                   font=("Segoe UI", 16, "bold"))
        self._name_lbl.pack(anchor="w", pady=4)

        tk.Label(inner, text="Constant:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 8)).pack(anchor="w")
        self._const_lbl = tk.Label(inner, text="", bg=BG_CARD, fg=FG_DIM,
                                    font=("Consolas", 9))
        self._const_lbl.pack(anchor="w", pady=(0, 8))

        # AI rating stars
        rating_row = tk.Frame(inner, bg=BG_CARD)
        rating_row.pack(anchor="w", pady=4)
        tk.Label(rating_row, text="AI Rating:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self._rating_lbl = tk.Label(rating_row, text="", bg=BG_CARD, fg=FG_GOLD,
                                     font=("Segoe UI", 11, "bold"))
        self._rating_lbl.pack(side=tk.LEFT, padx=8)

        desc_card = CardFrame(right, title="Description")
        desc_card.pack(fill=tk.X, padx=12, pady=(0, 8))
        self._desc_lbl = tk.Label(desc_card, text="", bg=BG_CARD, fg=FG_MAIN,
                                   font=("Segoe UI", 11), wraplength=480,
                                   justify="left", pady=8)
        self._desc_lbl.pack(anchor="w", padx=8, pady=(0, 8))

        # Which pokemon have this ability
        users_card = CardFrame(right, title="Pokémon with this ability")
        users_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        style = ttk.Style()
        style.configure("Ability.Treeview", background=BG_INPUT, foreground=FG_MAIN,
                         fieldbackground=BG_INPUT, rowheight=24)
        style.configure("Ability.Treeview.Heading", background=BG_PANEL,
                         foreground=FG_ACCENT, font=("Segoe UI", 9, "bold"))
        style.map("Ability.Treeview", background=[("selected", BG_PANEL)])

        cols = ("Pokémon", "Slot", "Type 1", "Type 2")
        self._users_tree = ttk.Treeview(users_card, columns=cols, show="headings",
                                         height=10, style="Ability.Treeview")
        for col in cols:
            self._users_tree.heading(col, text=col)
            self._users_tree.column(col, width=120)
        ab_scroll = ttk.Scrollbar(users_card, orient=tk.VERTICAL,
                                   command=self._users_tree.yview)
        self._users_tree.configure(yscrollcommand=ab_scroll.set)
        ab_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 8), pady=8)
        self._users_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def set_data(self, abilities_data, species_data):
        self._data = abilities_data
        self._species_data = species_data
        self._list.set_items(sorted(abilities_data.keys()))

    def _load_ability(self, name):
        self._current = name
        fields = self._data.get(name, {})
        self._name_lbl.config(text=fields.get('name', name))
        self._const_lbl.config(text=f"ABILITY_{name}")
        rating = fields.get('aiRating', 0)
        stars = "★" * min(rating, 10) + "☆" * max(0, 10 - min(rating, 10))
        self._rating_lbl.config(text=f"{stars} ({rating}/10)")
        self._desc_lbl.config(text=fields.get('description', ''))

        # Find pokemon with this ability
        self._users_tree.delete(*self._users_tree.get_children())
        for sp_name, sp_fields in self._species_data.items():
            ab1 = sp_fields.get('ability1', '')
            ab2 = sp_fields.get('ability2', '')
            abh = sp_fields.get('abilityH', '')
            slot = None
            if ab1 == name:
                slot = "Ability 1"
            elif ab2 == name:
                slot = "Ability 2"
            elif abh == name:
                slot = "Hidden"
            if slot:
                display = sp_fields.get('speciesName', sp_name)
                self._users_tree.insert("", tk.END, values=(
                    display, slot,
                    sp_fields.get('type1', ''),
                    sp_fields.get('type2', ''),
                ))


# ── Build Tab ──────────────────────────────────────────────────────────────────

class BuildTab(DarkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Build ROM", bg=BG_DARK, fg=FG_ACCENT,
                 font=("Segoe UI", 16, "bold")).pack(pady=(16, 4), padx=16, anchor="w")
        tk.Label(self, text="Compile your modifications into a playable GBA ROM",
                 bg=BG_DARK, fg=FG_DIM, font=("Segoe UI", 10)).pack(padx=16, anchor="w")

        opts_card = CardFrame(self, title="Build Options")
        opts_card.pack(fill=tk.X, padx=16, pady=12)
        opts_inner = tk.Frame(opts_card, bg=BG_CARD)
        opts_inner.pack(fill=tk.X, padx=8, pady=8)

        tk.Label(opts_inner, text="Target:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self._target_var = tk.StringVar(value="(default)")
        ttk.Combobox(opts_inner, textvariable=self._target_var, width=14, state="readonly",
                     values=["(default)", "debug", "release", "check", "clean"]).pack(
            side=tk.LEFT, padx=8)

        tk.Label(opts_inner, text="Parallel Jobs:", bg=BG_CARD, fg=FG_DIM,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(16, 0))
        self._jobs_var = tk.StringVar(value="12")
        DarkEntry(opts_inner, textvariable=self._jobs_var, width=5,
                  justify="center").pack(side=tk.LEFT, padx=8)

        btn_row = DarkFrame(self)
        btn_row.pack(fill=tk.X, padx=16, pady=4)
        DarkButton(btn_row, text="▶  Build ROM", command=self._run_build,
                   color=BTN_BUILD, padx=24, pady=10,
                   font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        DarkButton(btn_row, text="🗑  Clean", command=self._run_clean,
                   color=BTN_CLEAN, padx=16, pady=10,
                   font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=8)

        self._status_var = tk.StringVar(value="Ready to build")
        self._status_lbl = tk.Label(self, textvariable=self._status_var,
                                     bg=BG_DARK, fg=FG_GREEN, font=("Segoe UI", 10),
                                     anchor="w")
        self._status_lbl.pack(fill=tk.X, padx=16, pady=4)

        # Output terminal
        output_card = CardFrame(self, title="Build Output")
        output_card.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))
        self._output = scrolledtext.ScrolledText(
            output_card, font=("Consolas", 9), bg="#0d0d1a", fg="#c8f0c0",
            wrap=tk.WORD, state="disabled", insertbackground=FG_MAIN,
            relief="flat", padx=4, pady=4)
        self._output.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Tag for errors
        self._output.tag_config("error", foreground="#ff6b6b")
        self._output.tag_config("success", foreground="#4ecca3")
        self._output.tag_config("warning", foreground="#f6c90e")

    def _append_output(self, text):
        self._output.config(state="normal")
        tag = None
        lo = text.lower()
        if "error" in lo or "failed" in lo or "stop." in lo:
            tag = "error"
        elif "succeeded" in lo or "warning: rwx" not in lo and "%" in lo:
            tag = "success"
        elif "warning" in lo:
            tag = "warning"
        self._output.insert(tk.END, text, tag or "")
        self._output.see(tk.END)
        self._output.config(state="disabled")

    def _run_build(self):
        self._start_build("build")

    def _run_clean(self):
        self._start_build("clean")

    def _start_build(self, mode):
        self._output.config(state="normal")
        self._output.delete("1.0", tk.END)
        self._output.config(state="disabled")

        script = ROOT / "build.ps1"
        jobs = self._jobs_var.get().strip()
        target = self._target_var.get()

        if mode == "clean":
            args = ["clean"]
        elif target == "(default)":
            args = [f"-j{jobs}"]
        else:
            args = [target]

        self._status_var.set("⏳ Building…")
        self._status_lbl.config(fg=FG_GOLD)
        threading.Thread(target=self._do_build, args=(script, args), daemon=True).start()

    def _do_build(self, script, args):
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)] + args
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, cwd=str(ROOT), bufsize=1)
            for line in proc.stdout:
                self.after(0, self._append_output, line)
            proc.wait()
            if proc.returncode == 0:
                self.after(0, self._status_var.set, "✅ Build succeeded!")
                self.after(0, self._status_lbl.config, {"fg": FG_GREEN})
                self.after(0, self._append_output, "\n✅ Build succeeded!\n")
            else:
                self.after(0, self._status_var.set, f"❌ Build failed (exit {proc.returncode})")
                self.after(0, self._status_lbl.config, {"fg": FG_ACCENT})
        except Exception as e:
            self.after(0, self._append_output, f"\n❌ Error: {e}\n")
            self.after(0, self._status_var.set, f"❌ Error: {e}")
            self.after(0, self._status_lbl.config, {"fg": FG_ACCENT})


# ── Main App ───────────────────────────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("pokeemerald-expansion Editor")
        self.geometry("1280x820")
        self.minsize(960, 640)
        self.configure(bg=BG_DARK)

        self._setup_styles()
        self._build_ui()

        # Load all data in background thread
        threading.Thread(target=self._load_data, daemon=True).start()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_MED, foreground=FG_DIM,
                         font=("Segoe UI", 10), padding=(14, 6))
        style.map("TNotebook.Tab",
                  background=[("selected", BG_DARK), ("active", BG_PANEL)],
                  foreground=[("selected", FG_ACCENT), ("active", FG_MAIN)])
        style.configure("TCombobox", fieldbackground=BG_INPUT, background=BG_INPUT,
                         foreground=FG_MAIN, selectbackground=BG_PANEL,
                         arrowcolor=FG_MAIN)
        style.configure("TScrollbar", background=BG_MED, troughcolor=BG_DARK,
                         arrowcolor=FG_DIM)

    def _build_ui(self):
        # Top header bar
        header = tk.Frame(self, bg="#0d0d1a", height=52)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🎮", bg="#0d0d1a", fg=FG_ACCENT,
                 font=("Segoe UI", 20)).pack(side=tk.LEFT, padx=(12, 4), pady=8)
        tk.Label(header, text="pokeemerald-expansion Editor",
                 bg="#0d0d1a", fg=FG_MAIN, font=("Segoe UI", 14, "bold")).pack(
            side=tk.LEFT, pady=8)

        self._loading_lbl = tk.Label(header, text="Loading data…",
                                      bg="#0d0d1a", fg=FG_DIM, font=("Segoe UI", 9))
        self._loading_lbl.pack(side=tk.RIGHT, padx=16)

        # Notebook
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill=tk.BOTH, expand=True)

        self._tabs = {
            'pokemon':   PokemonTab(self._nb, self),
            'moves':     MovesTab(self._nb, self),
            'items':     ItemsTab(self._nb, self),
            'trainers':  TrainersTab(self._nb, self),
            'types':     TypesTab(self._nb, self),
            'abilities': AbilitiesTab(self._nb, self),
            'build':     BuildTab(self._nb, self),
        }
        tab_labels = {
            'pokemon':   "  🔴 Pokémon  ",
            'moves':     "  ⚡ Moves  ",
            'items':     "  🎒 Items  ",
            'trainers':  "  🧢 Trainers  ",
            'types':     "  📊 Types  ",
            'abilities': "  ✨ Abilities  ",
            'build':     "  🔨 Build  ",
        }
        for key, tab in self._tabs.items():
            self._nb.add(tab, text=tab_labels[key])

    def _load_data(self):
        steps = [
            ("species", pparser.load_all_species),
            ("moves", pparser.load_all_moves),
            ("items", pparser.load_all_items),
            ("trainers", pparser.load_all_trainers),
            ("abilities", pparser.load_all_abilities),
        ]
        loaded = {}
        for name, fn in steps:
            self.after(0, self._loading_lbl.config,
                       {"text": f"Loading {name}…"})
            try:
                loaded[name] = fn()
            except Exception as e:
                loaded[name] = {}
                print(f"Error loading {name}: {e}")

        types = pparser.parse_types_list()
        abilities_list = pparser.parse_abilities_list()
        effectiveness = img_util.parse_type_effectiveness()

        self.after(0, self._apply_data, loaded, types, abilities_list, effectiveness)

    def _apply_data(self, loaded, types, abilities_list, effectiveness):
        species = loaded.get('species', {})
        moves = loaded.get('moves', {})
        items = loaded.get('items', {})
        trainers = loaded.get('trainers', {})
        abilities_data = loaded.get('abilities', {})

        self._tabs['pokemon'].set_data(species, types, abilities_list, abilities_data)
        self._tabs['moves'].set_data(moves, types)
        self._tabs['items'].set_data(items)
        self._tabs['trainers'].set_data(trainers)
        self._tabs['types'].set_types(types, effectiveness)
        self._tabs['abilities'].set_data(abilities_data, species)

        counts = (f"{len(species)} species, {len(moves)} moves, "
                  f"{len(items)} items, {len(trainers)} trainers, "
                  f"{len(abilities_data)} abilities")
        self._loading_lbl.config(text=f"✓ {counts}", fg=FG_GREEN)


if __name__ == "__main__":
    app = App()
    app.mainloop()
