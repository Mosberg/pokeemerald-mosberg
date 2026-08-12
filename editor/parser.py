"""
Parsers for pokeemerald-expansion C header data files.
Reads enum constants and structured data from .h files.
"""
import re
import os
from pathlib import Path


ROOT = Path(__file__).parent.parent


def parse_enum(filepath, prefix):
    """Parse a C enum file and return {NAME: value} dict, stripping the given prefix."""
    result = {}
    try:
        text = Path(filepath).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return result

    # Find enum block (handles __attribute__((packed)) between name and {)
    enum_match = re.search(r'enum\s+(?:\S+\s*)?(?:__attribute__[^{]*)?\{([^}]+)\}', text, re.DOTALL)
    if not enum_match:
        enum_match = re.search(r'enum\s*\{([^}]+)\}', text, re.DOTALL)
    if not enum_match:
        # Try #define pattern
        for m in re.finditer(rf'#define\s+({re.escape(prefix)}\w+)\s+(\d+)', text):
            name = m.group(1)[len(prefix):]
            result[name] = int(m.group(2))
        return result

    body = enum_match.group(1)
    current_val = 0
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith('//') or line.startswith('/*'):
            continue
        # Remove inline comment
        line = re.sub(r'//.*$', '', line).strip().rstrip(',')
        if not line:
            continue
        # Skip aliases (= OTHER_CONSTANT)
        if '=' in line:
            parts = line.split('=', 1)
            name = parts[0].strip()
            val_str = parts[1].strip()
            # Try to parse integer value
            try:
                if val_str.startswith('0x'):
                    current_val = int(val_str, 16)
                else:
                    current_val = int(val_str)
            except ValueError:
                # It's an alias to another constant — skip
                continue
        else:
            name = line.strip()

        if name.startswith(prefix):
            short = name[len(prefix):]
            result[short] = current_val
        current_val += 1

    return result


def parse_species_list():
    """Return list of species names (without SPECIES_ prefix) in enum order."""
    d = parse_enum(ROOT / "include/constants/species.h", "SPECIES_")
    # Sort by value, filter out aliases (duplicates)
    seen_vals = {}
    for name, val in d.items():
        if val not in seen_vals:
            seen_vals[val] = name
    return [seen_vals[v] for v in sorted(seen_vals)]


def parse_moves_list():
    d = parse_enum(ROOT / "include/constants/moves.h", "MOVE_")
    seen_vals = {}
    for name, val in d.items():
        if val not in seen_vals:
            seen_vals[val] = name
    return [seen_vals[v] for v in sorted(seen_vals)]


def parse_items_list():
    d = parse_enum(ROOT / "include/constants/items.h", "ITEM_")
    seen_vals = {}
    for name, val in d.items():
        if val not in seen_vals:
            seen_vals[val] = name
    return [seen_vals[v] for v in sorted(seen_vals)]


def parse_abilities_list():
    d = parse_enum(ROOT / "include/constants/abilities.h", "ABILITY_")
    seen_vals = {}
    for name, val in d.items():
        if val not in seen_vals:
            seen_vals[val] = name
    return [seen_vals[v] for v in sorted(seen_vals)]


def parse_types_list():
    """Return list of type names from constants/pokemon.h or types_info.h."""
    filepath = ROOT / "include/constants/pokemon.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    types = re.findall(r'#define\s+TYPE_(\w+)\s+\d+', text)
    return types if types else [
        "NONE", "NORMAL", "FIGHTING", "FLYING", "POISON", "GROUND",
        "ROCK", "BUG", "GHOST", "STEEL", "MYSTERY", "FIRE", "WATER",
        "GRASS", "ELECTRIC", "PSYCHIC", "ICE", "DRAGON", "DARK", "FAIRY", "STELLAR"
    ]


def parse_national_dex_map():
    """Return {NATIONAL_DEX_BULBASAUR: 1, ...} from the dex enum."""
    return parse_enum(ROOT / "include/constants/pokedex.h", "NATIONAL_DEX_")


# --- Species info parser ---

def _extract_species_blocks(gen_file):
    """Extract {SPECIES_NAME: {field: value}} from a gen_X_families.h file."""
    text = gen_file.read_text(encoding="utf-8", errors="replace")
    results = {}

    # Find all [SPECIES_XXX] = { ... } blocks
    pattern = re.compile(r'\[SPECIES_(\w+)\]\s*=\s*\{', re.MULTILINE)
    starts = [(m.start(), m.group(1)) for m in pattern.finditer(text)]

    for i, (start, name) in enumerate(starts):
        # Find the matching closing brace
        brace_start = text.index('{', start)
        depth = 0
        pos = brace_start
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = text[brace_start+1:pos]
        results[name] = _parse_species_block(block)

    return results


def _parse_species_block(block):
    """Parse the contents of a species info struct block."""
    fields = {}

    # Simple integer/identifier fields
    for field, pattern in [
        ('baseHP', r'\.baseHP\s*=\s*(\d+)'),
        ('baseAttack', r'\.baseAttack\s*=\s*(\d+)'),
        ('baseDefense', r'\.baseDefense\s*=\s*(\d+)'),
        ('baseSpeed', r'\.baseSpeed\s*=\s*(\d+)'),
        ('baseSpAttack', r'\.baseSpAttack\s*=\s*(\d+)'),
        ('baseSpDefense', r'\.baseSpDefense\s*=\s*(\d+)'),
        ('catchRate', r'\.catchRate\s*=\s*(\d+)'),
        ('expYield', r'\.expYield\s*=\s*(?:[^,]+?,\s*)?(\d+)'),
        ('friendship', r'\.friendship\s*=\s*(\w+)'),
        ('height', r'\.height\s*=\s*(\d+)'),
        ('weight', r'\.weight\s*=\s*(\d+)'),
        ('genderRatio', r'\.genderRatio\s*=\s*([\w().,\s]+?)(?:,|\n)'),
        ('growthRate', r'\.growthRate\s*=\s*(GROWTH_\w+)'),
        ('bodyColor', r'\.bodyColor\s*=\s*(BODY_COLOR_\w+)'),
    ]:
        m = re.search(pattern, block)
        if m:
            fields[field] = m.group(1).strip()

    # Types: MON_TYPES(TYPE_X, TYPE_Y) or MON_TYPES(TYPE_X)
    m = re.search(r'\.types\s*=\s*MON_TYPES\(([^)]+)\)', block)
    if m:
        types = [t.strip().replace('TYPE_', '') for t in m.group(1).split(',')]
        fields['type1'] = types[0] if len(types) > 0 else 'NONE'
        fields['type2'] = types[1] if len(types) > 1 else types[0]

    # Abilities
    m = re.search(r'\.abilities\s*=\s*\{([^}]+)\}', block)
    if m:
        abilities = [a.strip().replace('ABILITY_', '') for a in m.group(1).split(',')]
        fields['ability1'] = abilities[0] if len(abilities) > 0 else 'NONE'
        fields['ability2'] = abilities[1] if len(abilities) > 1 else 'NONE'
        fields['abilityH'] = abilities[2] if len(abilities) > 2 else 'NONE'

    # Species name
    m = re.search(r'\.speciesName\s*=\s*_\("([^"]+)"\)', block)
    if m:
        fields['speciesName'] = m.group(1)

    # Category
    m = re.search(r'\.categoryName\s*=\s*_\("([^"]+)"\)', block)
    if m:
        fields['categoryName'] = m.group(1)

    # Description
    m = re.search(r'\.description\s*=\s*COMPOUND_STRING\(([^)]+)\)', block, re.DOTALL)
    if m:
        raw = m.group(1)
        desc = re.sub(r'"\s*\n\s*"', '', raw)
        desc = re.sub(r'^"', '', desc.strip())
        desc = re.sub(r'"$', '', desc)
        desc = desc.replace('\\n', '\n')
        fields['description'] = desc

    # natDexNum: map enum constant to numeric national dex position.
    m = re.search(r'\.natDexNum\s*=\s*(NATIONAL_DEX_\w+)', block)
    if m:
        dex_const = m.group(1)
        fields['natDexNum'] = parse_national_dex_map().get(dex_const.replace('NATIONAL_DEX_', ''), 99999)

    # Egg groups
    m = re.search(r'\.eggGroups\s*=\s*MON_EGG_GROUPS\(([^)]+)\)', block)
    if m:
        groups = [g.strip().replace('EGG_GROUP_', '') for g in m.group(1).split(',')]
        fields['eggGroup1'] = groups[0] if len(groups) > 0 else 'NONE'
        fields['eggGroup2'] = groups[1] if len(groups) > 1 else groups[0]

    return fields


def load_all_species():
    """Load all species info from all gen files. Returns {SPECIES_NAME: fields}."""
    species_dir = ROOT / "src/data/pokemon/species_info"
    all_species = {}
    for gen_file in sorted(species_dir.glob("gen_*.h")):
        blocks = _extract_species_blocks(gen_file)
        all_species.update(blocks)
        for name, fields in blocks.items():
            fields['_source_file'] = str(gen_file)
    return all_species


# --- Move info parser ---

def load_all_moves():
    """Load move data from moves_info.h. Returns {MOVE_NAME: fields}."""
    filepath = ROOT / "src/data/moves_info.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    results = {}

    pattern = re.compile(r'\[MOVE_(\w+)\]\s*=\s*\{', re.MULTILINE)
    starts = [(m.start(), m.group(1)) for m in pattern.finditer(text)]

    for i, (start, name) in enumerate(starts):
        brace_start = text.index('{', start)
        depth = 0
        pos = brace_start
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = text[brace_start+1:pos]
        fields = _parse_move_block(block)
        fields['_source_file'] = str(filepath)
        results[name] = fields

    return results


def _parse_move_block(block):
    fields = {}

    m = re.search(r'\.name\s*=\s*COMPOUND_STRING\("([^"]+)"\)', block)
    if m:
        fields['name'] = m.group(1)

    m = re.search(r'\.effect\s*=\s*(EFFECT_\w+)', block)
    if m:
        fields['effect'] = m.group(1).replace('EFFECT_', '')

    m = re.search(r'\.power\s*=\s*(\d+)', block)
    if m:
        fields['power'] = m.group(1)

    m = re.search(r'\.type\s*=\s*(?:[^?]+\?\s*)?TYPE_(\w+)', block)
    if m:
        fields['type'] = m.group(1)

    m = re.search(r'\.accuracy\s*=\s*(\d+)', block)
    if m:
        fields['accuracy'] = m.group(1)

    m = re.search(r'\.pp\s*=\s*(\d+)', block)
    if m:
        fields['pp'] = m.group(1)

    m = re.search(r'\.priority\s*=\s*(-?\d+)', block)
    if m:
        fields['priority'] = m.group(1)

    m = re.search(r'\.category\s*=\s*DAMAGE_CATEGORY_(\w+)', block)
    if m:
        fields['category'] = m.group(1)

    # Description
    m = re.search(r'\.description\s*=\s*COMPOUND_STRING\(([^)]+)\)', block, re.DOTALL)
    if m:
        raw = m.group(1)
        desc = re.sub(r'"\s*\n\s*"', '', raw)
        desc = re.sub(r'^"', '', desc.strip())
        desc = re.sub(r'"$', '', desc)
        desc = desc.replace('\\n', '\n')
        fields['description'] = desc

    return fields


# --- Item parser ---

def load_all_items():
    """Load item data from items.h. Returns {ITEM_NAME: fields}."""
    filepath = ROOT / "src/data/items.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    results = {}

    pattern = re.compile(r'\[ITEM_(\w+)\]\s*=\s*\{', re.MULTILINE)
    starts = [(m.start(), m.group(1)) for m in pattern.finditer(text)]

    for i, (start, name) in enumerate(starts):
        brace_start = text.index('{', start)
        depth = 0
        pos = brace_start
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = text[brace_start+1:pos]
        fields = _parse_item_block(block)
        fields['_source_file'] = str(filepath)
        results[name] = fields

    return results


def _parse_item_block(block):
    fields = {}

    m = re.search(r'\.name\s*=\s*ITEM_NAME\("([^"]+)"\)', block)
    if m:
        fields['name'] = m.group(1)

    m = re.search(r'\.price\s*=\s*(\d+)', block)
    if m:
        fields['price'] = m.group(1)

    m = re.search(r'\.holdEffect\s*=\s*(HOLD_EFFECT_\w+)', block)
    if m:
        fields['holdEffect'] = m.group(1).replace('HOLD_EFFECT_', '')

    m = re.search(r'\.holdEffectParam\s*=\s*(\d+)', block)
    if m:
        fields['holdEffectParam'] = m.group(1)

    m = re.search(r'\.pocket\s*=\s*(POCKET_\w+)', block)
    if m:
        fields['pocket'] = m.group(1).replace('POCKET_', '')

    m = re.search(r'\.type\s*=\s*(ITEM_USE_\w+)', block)
    if m:
        fields['type'] = m.group(1).replace('ITEM_USE_', '')

    # Description (static var reference or inline)
    m = re.search(r'\.description\s*=\s*(s\w+Desc)', block)
    if m:
        fields['description'] = f"[{m.group(1)}]"
    else:
        m = re.search(r'\.description\s*=\s*_\("([^"]+)"\)', block)
        if m:
            fields['description'] = m.group(1)

    return fields


# --- Trainer parser ---

def load_all_trainers():
    """Parse trainers.party for trainer data. Returns list of trainer dicts."""
    filepath = ROOT / "src/data/trainers.h"
    if not filepath.exists():
        filepath = ROOT / "src/data/trainers.party"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    results = {}

    pattern = re.compile(r'\[DIFFICULTY_\w+\]\[TRAINER_(\w+)\]\s*=\s*\{', re.MULTILINE)
    starts = [(m.start(), m.group(1)) for m in pattern.finditer(text)]

    for i, (start, name) in enumerate(starts):
        brace_start = text.index('{', start)
        depth = 0
        pos = brace_start
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = text[brace_start+1:pos]
        fields = _parse_trainer_block(block)
        fields['_source_file'] = str(filepath)
        results[name] = fields

    return results


def _parse_trainer_block(block):
    fields = {}

    m = re.search(r'\.trainerName\s*=\s*_\("([^"]+)"\)', block)
    if m:
        fields['trainerName'] = m.group(1)

    m = re.search(r'\.trainerClass\s*=\s*(TRAINER_CLASS_\w+)', block)
    if m:
        fields['trainerClass'] = m.group(1).replace('TRAINER_CLASS_', '')

    m = re.search(r'\.trainerPic\s*=\s*(TRAINER_PIC_\w+)', block)
    if m:
        fields['trainerPic'] = m.group(1).replace('TRAINER_PIC_', '')

    m = re.search(r'\.gender\s*=\s*(TRAINER_GENDER_\w+)', block)
    if m:
        fields['gender'] = m.group(1).replace('TRAINER_GENDER_', '')

    m = re.search(r'\.battleType\s*=\s*(TRAINER_BATTLE_TYPE_\w+)', block)
    if m:
        fields['battleType'] = m.group(1).replace('TRAINER_BATTLE_TYPE_', '')

    m = re.search(r'\.aiFlags\s*=\s*([^\n,]+)', block)
    if m:
        fields['aiFlags'] = m.group(1).strip()

    # Party
    party = []
    party_pattern = re.compile(r'\.species\s*=\s*SPECIES_(\w+)', re.MULTILINE)
    lvl_pattern = re.compile(r'\.lvl\s*=\s*(\d+)')
    for j, pm in enumerate(party_pattern.finditer(block)):
        mon = {'species': pm.group(1)}
        # find level nearby
        context = block[pm.start():pm.start()+500]
        lm = lvl_pattern.search(context)
        if lm:
            mon['level'] = lm.group(1)
        party.append(mon)
    fields['party'] = party

    return fields


def load_all_abilities():
    """Load ability data from abilities.h. Returns {ABILITY_NAME: {name, description, aiRating}}."""
    filepath = ROOT / "src/data/abilities.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    results = {}

    pattern = re.compile(r'\[ABILITY_(\w+)\]\s*=\s*\{', re.MULTILINE)
    starts = [(m.start(), m.group(1)) for m in pattern.finditer(text)]

    for start, name in starts:
        brace_start = text.index('{', start)
        depth = 0
        pos = brace_start
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    break
            pos += 1
        block = text[brace_start+1:pos]

        fields = {}
        m = re.search(r'\.name\s*=\s*_\("([^"]+)"\)', block)
        if m:
            fields['name'] = m.group(1)
        m = re.search(r'\.description\s*=\s*COMPOUND_STRING\("([^"]+)"\)', block)
        if m:
            fields['description'] = m.group(1)
        m = re.search(r'\.aiRating\s*=\s*(-?\d+)', block)
        if m:
            fields['aiRating'] = int(m.group(1))
        results[name] = fields

    return results
