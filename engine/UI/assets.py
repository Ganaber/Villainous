"""Asset registry.

Art is referenced by logical key, never by path, so snapshots stay portable and the
renderer never does filename logic. Per-card art lives at

    cards/<villain>/<card_slug>.webp

and every card in a villain's deck is expected to have a file there. A missing file is
not fatal: ``exists()`` reports it and the renderer draws a labelled tile instead.
"""
from __future__ import annotations

import re
from pathlib import Path

ASSET_ROOT = Path(__file__).parent / "assets"

# Villain art namespace, e.g. assets/cards/wtia_prince_john/.
PRINCE_JOHN = "wtia_prince_john"

# Logical key -> path relative to ASSET_ROOT. Only real art belongs here; anything
# drawn procedurally by the renderer needs no asset entry.
MANIFEST: dict[str, str] = {
    f"board.{PRINCE_JOHN}": f"boards/{PRINCE_JOHN}.webp",
    "card.back.villain": f"cards/{PRINCE_JOHN}/card_back.webp",
    "card.back.fate": f"cards/{PRINCE_JOHN}/fate_card_back.webp",
}

# Conventional per-card face key, e.g. "card.face:Sheriff of Nottingham".
CARD_FACE_PREFIX = "card.face:"


def slug(name: str) -> str:
    """Filename-safe form of a card name. Apostrophes are dropped, not doubled.

    "King Richard's Crown" -> "king_richards_crown", matching the art filenames.
    """
    cleaned = re.sub(r"['\u2019`\u00b4]", "", name)
    return re.sub(r"[^a-z0-9]+", "_", cleaned.lower()).strip("_")


def card_face_key(card_name: str) -> str:
    return f"{CARD_FACE_PREFIX}{card_name}"


def villain_art_dir(villain: str = PRINCE_JOHN) -> Path:
    return ASSET_ROOT / "cards" / villain


def candidate_paths(key: str) -> list[Path]:
    """Every file that could satisfy a key, most preferred first."""
    if key.startswith(CARD_FACE_PREFIX):
        stem = slug(key[len(CARD_FACE_PREFIX):])
        directory = villain_art_dir()
        return [directory / f"{stem}.webp", directory / f"{stem}.png"]
    if key in MANIFEST:
        return [ASSET_ROOT / MANIFEST[key]]
    return []


def path(key: str) -> Path:
    """Best available file for an asset key, or the preferred path if none exist."""
    candidates = candidate_paths(key)
    if not candidates:
        raise KeyError(f"unknown asset key {key!r}")
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def exists(key: str) -> bool:
    try:
        return any(candidate.is_file() for candidate in candidate_paths(key))
    except KeyError:
        return False


def face_key(card_name: str, card_type: str = "") -> str:
    """Asset key for a card face. ``card_type`` is accepted for call-site symmetry."""
    return card_face_key(card_name)


def missing() -> list[str]:
    """Manifest entries whose file has not been supplied."""
    return [key for key in MANIFEST if not exists(key)]


def villain_cards(villain: str = PRINCE_JOHN) -> dict[str, Path]:
    """Every per-card art file present for a villain, keyed by card slug."""
    directory = villain_art_dir(villain)
    if not directory.is_dir():
        return {}
    return {
        file.stem: file
        for file in sorted(directory.iterdir())
        if file.suffix.lower() in {".webp", ".png"}
    }


def missing_cards(card_names: list[str], villain: str = PRINCE_JOHN) -> list[str]:
    """Card names whose art file is absent."""
    return [name for name in card_names if not exists(card_face_key(name))]
