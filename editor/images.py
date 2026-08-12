"""
Image utilities for pokeemerald-expansion Editor.
Handles loading, converting, scaling, and caching PNG sprites from the repo.
"""
import re
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).parent.parent
GRAPHICS = ROOT / "graphics"
POKEMON_GFX = GRAPHICS / "pokemon"
TYPES_GFX = GRAPHICS / "types"
ITEMS_GFX = GRAPHICS / "items" / "icons"
TRAINERS_FRONT = GRAPHICS / "trainers" / "front_pics"

# Cache to avoid reloading
_cache: dict = {}


def _species_to_folder(species_name: str) -> Path:
    """Convert SPECIES_MR_MIME -> graphics/pokemon/mr_mime"""
    name = species_name.lower()
    # Common remappings
    remaps = {
        "nidoran_f": "nidoran_f",
        "nidoran_m": "nidoran_m",
        "farfetchd": "farfetchd",
        "sirfetchd": "sirfetchd",
    }
    name = remaps.get(name, name)
    return POKEMON_GFX / name


def get_pokemon_icon(species_name: str, size=(48, 48), shiny=False) -> "tk.PhotoImage | None":
    """Load the 32x32 icon for a species, upscaled to size."""
    key = f"icon_{species_name}_{size}_{shiny}"
    if key in _cache:
        return _cache[key]

    folder = _species_to_folder(species_name)
    icon_file = folder / "icon.png"
    if not icon_file.exists():
        _cache[key] = None
        return None

    try:
        img = Image.open(icon_file).convert("RGBA")
        # icon.png is 32x64: top half = normal, bottom half = shiny
        half = img.height // 2
        frame = img.crop((0, half if shiny else 0, 32, (half * 2) if shiny else half))
        frame = frame.resize(size, Image.NEAREST)
        result = ImageTk.PhotoImage(frame)
        _cache[key] = result
        return result
    except Exception:
        _cache[key] = None
        return None


def get_pokemon_front(species_name: str, size=(128, 128), shiny=False) -> "tk.PhotoImage | None":
    """Load the front sprite for a species."""
    key = f"front_{species_name}_{size}_{shiny}"
    if key in _cache:
        return _cache[key]

    folder = _species_to_folder(species_name)
    # Try anim_front first, fallback to front
    for fname in ["anim_front.png", "front.png"]:
        sprite_file = folder / fname
        if sprite_file.exists():
            break
    else:
        _cache[key] = None
        return None

    try:
        img = Image.open(sprite_file).convert("RGBA")
        # anim_front.png is 64x128: top half = frame 1
        half = img.height // 2
        frame = img.crop((0, 0, img.width, half))

        if shiny:
            # Load shiny palette and apply if available
            pal_file = folder / "shiny.pal"
            if pal_file.exists():
                frame = _apply_shiny_tint(frame)

        frame = frame.resize(size, Image.NEAREST)
        result = ImageTk.PhotoImage(frame)
        _cache[key] = result
        return result
    except Exception:
        _cache[key] = None
        return None


def _apply_shiny_tint(img: Image.Image) -> Image.Image:
    """Apply a golden tint to simulate shiny coloring when palette isn't loaded."""
    # Simple approach: shift hue slightly
    import colorsys
    data = list(img.getdata())
    out = []
    for r, g, b, a in data:
        if a > 0:
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            h = (h + 0.08) % 1.0
            s = min(1.0, s * 1.3)
            r2, g2, b2 = colorsys.hsv_to_rgb(h, s, v)
            out.append((int(r2*255), int(g2*255), int(b2*255), a))
        else:
            out.append((r, g, b, a))
    result = img.copy()
    result.putdata(out)
    return result


def get_type_icon(type_name: str, size=(64, 24)) -> "tk.PhotoImage | None":
    """Load the type badge icon PNG."""
    key = f"type_{type_name}_{size}"
    if key in _cache:
        return _cache[key]

    name_map = {"FIGHTING": "fight"}
    filename = name_map.get(type_name, type_name.lower()) + ".png"
    type_file = TYPES_GFX / filename
    if not type_file.exists():
        _cache[key] = None
        return None

    try:
        img = Image.open(type_file).convert("RGBA")
        # Type icons are 32x16 (2 frames stacked in some, or just single)
        # Take the top frame
        frame = img.crop((0, 0, img.width, min(16, img.height)))
        frame = frame.resize(size, Image.NEAREST)
        result = ImageTk.PhotoImage(frame)
        _cache[key] = result
        return result
    except Exception:
        _cache[key] = None
        return None


def get_item_icon(item_name: str, size=(48, 48)) -> "tk.PhotoImage | None":
    """Load item icon by item constant name (e.g. POKE_BALL)."""
    key = f"item_{item_name}_{size}"
    if key in _cache:
        return _cache[key]

    # Convert ITEM constant to filename: POKE_BALL -> poke_ball.png
    filename = item_name.lower() + ".png"
    item_file = ITEMS_GFX / filename
    if not item_file.exists():
        _cache[key] = None
        return None

    try:
        img = Image.open(item_file).convert("RGBA")
        img = img.resize(size, Image.NEAREST)
        result = ImageTk.PhotoImage(img)
        _cache[key] = result
        return result
    except Exception:
        _cache[key] = None
        return None


def get_trainer_sprite(trainer_pic: str, size=(80, 80)) -> "tk.PhotoImage | None":
    """Load trainer front pic by TRAINER_PIC_ constant name."""
    key = f"trainer_{trainer_pic}_{size}"
    if key in _cache:
        return _cache[key]

    filename = trainer_pic.lower() + ".png"
    trainer_file = TRAINERS_FRONT / filename
    if not trainer_file.exists():
        _cache[key] = None
        return None

    try:
        img = Image.open(trainer_file).convert("RGBA")
        # Front pics are 64x64 per frame, may be stacked
        frame = img.crop((0, 0, img.width, min(64, img.height)))
        frame = frame.resize(size, Image.NEAREST)
        result = ImageTk.PhotoImage(frame)
        _cache[key] = result
        return result
    except Exception:
        _cache[key] = None
        return None


def make_type_badge_image(type_name: str, width=72, height=22) -> "tk.PhotoImage":
    """Create a colored type badge with text (fallback when no icon exists)."""
    key = f"badge_{type_name}_{width}_{height}"
    if key in _cache:
        return _cache[key]

    TYPE_COLORS = {
        "NORMAL": "#A8A878", "FIGHTING": "#C03028", "FLYING": "#A890F0",
        "POISON": "#A040A0", "GROUND": "#E0C068", "ROCK": "#B8A038",
        "BUG": "#A8B820", "GHOST": "#705898", "STEEL": "#B8B8D0",
        "MYSTERY": "#68A090", "FIRE": "#F08030", "WATER": "#6890F0",
        "GRASS": "#78C850", "ELECTRIC": "#F8D030", "PSYCHIC": "#F85888",
        "ICE": "#98D8D8", "DRAGON": "#7038F8", "DARK": "#705848",
        "FAIRY": "#EE99AC", "STELLAR": "#40B5A5", "NONE": "#888888",
    }

    color = TYPE_COLORS.get(type_name, "#888888")
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    dark = (max(0, r-40), max(0, g-40), max(0, b-40))

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, width-1, height-1], radius=4,
                            fill=color, outline=f"#{dark[0]:02x}{dark[1]:02x}{dark[2]:02x}")
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()
    text = type_name[:8]
    bbox = draw.textbbox((0, 0), text, font=font)
    tx = (width - (bbox[2] - bbox[0])) // 2
    ty = (height - (bbox[3] - bbox[1])) // 2
    draw.text((tx, ty), text, fill="white", font=font)

    result = ImageTk.PhotoImage(img)
    _cache[key] = result
    return result


def make_stat_bar_image(value: int, max_val: int, color: str, width: int, height=14) -> "tk.PhotoImage":
    """Create a stat bar image."""
    key = f"bar_{value}_{max_val}_{color}_{width}_{height}"
    if key in _cache:
        return _cache[key]

    img = Image.new("RGBA", (width, height), "#2a2a2a")
    draw = ImageDraw.Draw(img)

    fill_w = max(1, int(width * min(value, max_val) / max_val))

    # Gradient-like bar
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    bright = f"#{min(255,r+40):02x}{min(255,g+40):02x}{min(255,b+40):02x}"
    draw.rectangle([0, 0, fill_w, height//2], fill=bright)
    draw.rectangle([0, height//2, fill_w, height], fill=color)

    result = ImageTk.PhotoImage(img)
    _cache[key] = result
    return result


def parse_type_effectiveness() -> dict:
    """
    Parse the type effectiveness table from types_info.h.
    Returns {(attacker_type, defender_type): multiplier}.
    """
    filepath = ROOT / "src/data/types_info.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")

    type_order = ["NONE", "NORMAL", "FIGHTING", "FLYING", "POISON", "GROUND",
                  "ROCK", "BUG", "GHOST", "STEEL", "MYSTERY", "FIRE", "WATER",
                  "GRASS", "ELECTRIC", "PSYCHIC", "ICE", "DRAGON", "DARK", "FAIRY", "STELLAR"]

    table_match = re.search(r'gTypeEffectivenessTable\[.*?\]\[.*?\]\s*=\s*\{(.+?)\};',
                            text, re.DOTALL)
    if not table_match:
        return {}

    table_text = table_match.group(1)
    result = {}

    for m in re.finditer(r'\[TYPE_(\w+)\]\s*=\s*\{([^}]+)\}', table_text):
        attacker = m.group(1)
        row_text = m.group(2)

        # Extract all X(n.n) and ______ values
        values = []
        for token in re.finditer(r'X\(([\d.]+)\)|______', row_text):
            if token.group(0) == "______":
                values.append(1.0)
            else:
                values.append(float(token.group(1)))

        for i, mult in enumerate(values):
            if i < len(type_order):
                defender = type_order[i]
                result[(attacker, defender)] = mult

    return result


def clear_cache():
    _cache.clear()
