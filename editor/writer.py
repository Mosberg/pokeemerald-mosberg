"""
Writers for pokeemerald-expansion C header files.
Patches specific fields in-place without rewriting unrelated content.
"""
import re
from pathlib import Path


ROOT = Path(__file__).parent.parent


def _patch_field_in_block(text, block_start, block_end, field_name, new_value):
    """
    Replace the value of a .field_name = ... line within a block range.
    Returns the modified text.
    """
    block = text[block_start:block_end]
    pattern = re.compile(rf'(\.{re.escape(field_name)}\s*=\s*)([^\n,}}]+)')
    m = pattern.search(block)
    if m:
        new_block = block[:m.start(2)] + new_value + block[m.end(2):]
        return text[:block_start] + new_block + text[block_end:]
    return text


def _find_block_range(text, key_pattern):
    """Find the char range {start, end} of the struct block for a given key pattern."""
    m = re.search(key_pattern, text)
    if not m:
        return None, None
    brace_start = text.index('{', m.start())
    depth = 0
    pos = brace_start
    while pos < len(text):
        if text[pos] == '{':
            depth += 1
        elif text[pos] == '}':
            depth -= 1
            if depth == 0:
                return brace_start, pos + 1
        pos += 1
    return None, None


def save_species(species_name, fields, source_file=None):
    """
    Save modified species fields back to the appropriate gen_X_families.h file.
    Only patches the fields that are editable (stats, types, abilities, name, description).
    """
    if source_file:
        filepath = Path(source_file)
    else:
        # Find which file contains this species
        species_dir = ROOT / "src/data/pokemon/species_info"
        filepath = None
        for gen_file in sorted(species_dir.glob("gen_*.h")):
            text = gen_file.read_text(encoding="utf-8", errors="replace")
            if f'[SPECIES_{species_name}]' in text:
                filepath = gen_file
                break
        if not filepath:
            raise FileNotFoundError(f"SPECIES_{species_name} not found in any gen file")

    text = filepath.read_text(encoding="utf-8", errors="replace")
    key_pattern = rf'\[SPECIES_{re.escape(species_name)}\]\s*='
    start, end = _find_block_range(text, key_pattern)
    if start is None:
        raise ValueError(f"Could not find block for SPECIES_{species_name}")

    # Patch simple integer stats
    for field in ['baseHP', 'baseAttack', 'baseDefense', 'baseSpeed', 'baseSpAttack', 'baseSpDefense',
                  'catchRate', 'height', 'weight', 'friendship']:
        if field in fields:
            text = _patch_field_in_block(text, start, end, field, str(fields[field]))
            # Re-find block after modification (offsets may shift)
            start, end = _find_block_range(text, key_pattern)

    # Patch speciesName
    if 'speciesName' in fields:
        block = text[start:end]
        new_block = re.sub(
            r'(\.speciesName\s*=\s*_\(")[^"]*(")',
            rf'\g<1>{fields["speciesName"]}\2',
            block
        )
        text = text[:start] + new_block + text[end:]
        start, end = _find_block_range(text, key_pattern)

    # Patch categoryName
    if 'categoryName' in fields:
        block = text[start:end]
        new_block = re.sub(
            r'(\.categoryName\s*=\s*_\(")[^"]*(")',
            rf'\g<1>{fields["categoryName"]}\2',
            block
        )
        text = text[:start] + new_block + text[end:]
        start, end = _find_block_range(text, key_pattern)

    # Patch types
    if 'type1' in fields or 'type2' in fields:
        block = text[start:end]
        m = re.search(r'\.types\s*=\s*MON_TYPES\(([^)]+)\)', block)
        if m:
            existing = [t.strip() for t in m.group(1).split(',')]
            t1 = f"TYPE_{fields.get('type1', existing[0].replace('TYPE_', ''))}"
            t2 = f"TYPE_{fields.get('type2', existing[1].replace('TYPE_', '') if len(existing) > 1 else existing[0].replace('TYPE_', ''))}"
            if t1 == t2:
                new_types = f"MON_TYPES({t1})"
            else:
                new_types = f"MON_TYPES({t1}, {t2})"
            new_block = block[:m.start()] + f".types = {new_types}" + block[m.end():]
            text = text[:start] + new_block + text[end:]
            start, end = _find_block_range(text, key_pattern)

    # Patch abilities
    if 'ability1' in fields or 'ability2' in fields or 'abilityH' in fields:
        block = text[start:end]
        m = re.search(r'(\.abilities\s*=\s*\{)([^}]+)(\})', block)
        if m:
            existing = [a.strip() for a in m.group(2).split(',')]
            a1 = f"ABILITY_{fields.get('ability1', existing[0].replace('ABILITY_', '') if len(existing) > 0 else 'NONE')}"
            a2 = f"ABILITY_{fields.get('ability2', existing[1].replace('ABILITY_', '') if len(existing) > 1 else 'NONE')}"
            ah = f"ABILITY_{fields.get('abilityH', existing[2].replace('ABILITY_', '') if len(existing) > 2 else 'NONE')}"
            new_block = block[:m.start(2)] + f" {a1}, {a2}, {ah} " + block[m.end(2):]
            text = text[:start] + new_block + text[end:]

    filepath.write_text(text, encoding="utf-8")


def save_move(move_name, fields, source_file=None):
    """Save modified move fields back to moves_info.h."""
    filepath = Path(source_file) if source_file else ROOT / "src/data/moves_info.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    key_pattern = rf'\[MOVE_{re.escape(move_name)}\]\s*='
    start, end = _find_block_range(text, key_pattern)
    if start is None:
        raise ValueError(f"Could not find block for MOVE_{move_name}")

    for field in ['power', 'accuracy', 'pp', 'priority']:
        if field in fields:
            text = _patch_field_in_block(text, start, end, field, str(fields[field]))
            start, end = _find_block_range(text, key_pattern)

    if 'type' in fields:
        block = text[start:end]
        # Replace TYPE_X in the .type = line
        new_block = re.sub(
            r'(\.type\s*=\s*)(?:[^?]+\?\s*)?TYPE_\w+',
            rf'\g<1>TYPE_{fields["type"]}',
            block
        )
        text = text[:start] + new_block + text[end:]
        start, end = _find_block_range(text, key_pattern)

    if 'category' in fields:
        block = text[start:end]
        new_block = re.sub(
            r'(\.category\s*=\s*)DAMAGE_CATEGORY_\w+',
            rf'\g<1>DAMAGE_CATEGORY_{fields["category"]}',
            block
        )
        text = text[:start] + new_block + text[end:]
        start, end = _find_block_range(text, key_pattern)

    if 'name' in fields:
        block = text[start:end]
        new_block = re.sub(
            r'(\.name\s*=\s*COMPOUND_STRING\(")[^"]*(")',
            rf'\g<1>{fields["name"]}\2',
            block
        )
        text = text[:start] + new_block + text[end:]

    filepath.write_text(text, encoding="utf-8")


def save_item(item_name, fields, source_file=None):
    """Save modified item fields back to items.h."""
    filepath = Path(source_file) if source_file else ROOT / "src/data/items.h"
    text = filepath.read_text(encoding="utf-8", errors="replace")
    key_pattern = rf'\[ITEM_{re.escape(item_name)}\]\s*='
    start, end = _find_block_range(text, key_pattern)
    if start is None:
        raise ValueError(f"Could not find block for ITEM_{item_name}")

    for field in ['price', 'holdEffectParam']:
        if field in fields:
            text = _patch_field_in_block(text, start, end, field, str(fields[field]))
            start, end = _find_block_range(text, key_pattern)

    if 'name' in fields:
        block = text[start:end]
        new_block = re.sub(
            r'(\.name\s*=\s*ITEM_NAME\(")[^"]*(")',
            rf'\g<1>{fields["name"]}\2',
            block
        )
        text = text[:start] + new_block + text[end:]

    filepath.write_text(text, encoding="utf-8")
