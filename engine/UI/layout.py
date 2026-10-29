"""Declarative layout specs.

A layout holds *geometry only*. Content is supplied separately by a GameSnapshot.
Everything is expressed in normalized 0..1 coordinates on a fixed virtual canvas, so
a layout survives window resizing and can be re-calibrated against a new screenshot
without touching render code.

This module is deliberately pygame-free: layouts can be loaded, validated and
hit-tested headlessly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

LAYOUT_DIR = Path(__file__).parent / "layouts"

NUM_LOCATIONS = 4

# Regions every realm template must define.
LOCATION_PARTS: tuple[str, ...] = (
    "panel",
    "title",
    "top_actions",
    "bottom_actions",
    "top_cards",
    "bottom_cards",
    "mover",
)

REQUIRED_REALM_REGIONS: tuple[str, ...] = (
    "board.power",
    "board.villain_draw",
    "board.fate_draw",
    "board.villain_discard",
    "board.fate_discard",
    "board.hand",
    "board.portrait",
    "board.mover",
) + tuple(
    f"location.{i}.{part}" for i in range(NUM_LOCATIONS) for part in LOCATION_PARTS
)

REQUIRED_SCREEN_REGIONS: tuple[str, ...] = ("event_log", "winner_banner", "turn_header")


@dataclass(frozen=True)
class Rect:
    """A rectangle in normalized (0..1) canvas space."""

    x: float
    y: float
    w: float
    h: float

    def pixels(self, canvas_width: int, canvas_height: int) -> tuple[int, int, int, int]:
        return (
            round(self.x * canvas_width),
            round(self.y * canvas_height),
            round(self.w * canvas_width),
            round(self.h * canvas_height),
        )

    def contains(self, nx: float, ny: float) -> bool:
        return self.x <= nx < self.x + self.w and self.y <= ny < self.y + self.h

    def to_dict(self) -> dict[str, float]:
        return {"x": round(self.x, 4), "y": round(self.y, 4), "w": round(self.w, 4), "h": round(self.h, 4)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Rect:
        return cls(float(data["x"]), float(data["y"]), float(data["w"]), float(data["h"]))

    def inset(self, amount: float) -> Rect:
        return Rect(self.x + amount, self.y + amount, max(0.0, self.w - 2 * amount), max(0.0, self.h - 2 * amount))


@dataclass(frozen=True)
class Region:
    """A named rectangle plus how content is laid out inside it."""

    name: str
    rect: Rect
    align: str = "center"  # start | center | end  (along the region's main axis)
    capacity: int | None = None  # how many items fit before overlaying/shrinking

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"rect": self.rect.to_dict(), "align": self.align}
        if self.capacity is not None:
            data["capacity"] = self.capacity
        return data

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> Region:
        return cls(
            name=name,
            rect=Rect.from_dict(data["rect"]),
            align=str(data.get("align", "center")),
            capacity=data.get("capacity"),
        )


@dataclass(frozen=True)
class CardMetrics:
    """Card geometry as fractions of the virtual canvas (width of canvas width, height of canvas height)."""

    width: float = 0.105
    height: float = 0.235
    gap: float = 0.006
    fan_angle: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "width": self.width,
            "height": self.height,
            "gap": self.gap,
            "fan_angle": self.fan_angle,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> CardMetrics:
        if not data:
            return cls()
        return cls(
            width=float(data.get("width", 0.105)),
            height=float(data.get("height", 0.235)),
            gap=float(data.get("gap", 0.006)),
            fan_angle=float(data.get("fan_angle", 0.0)),
        )


@dataclass(frozen=True)
class ActionSlots:
    """Where the board art paints its action icons, as fractions of a column's width.

    The real board has the icons baked into the artwork, so the renderer highlights
    them instead of drawing chips on top. Keyed by icon count per row.
    """

    centers: dict[str, list[float]] = field(default_factory=dict)
    diameter: float = 0.24

    def centers_for(self, count: int) -> list[float]:
        return list(self.centers.get(str(count), []))

    def supports(self, count: int) -> bool:
        return str(count) in self.centers

    def to_dict(self) -> dict[str, Any]:
        return {"centers": {k: list(v) for k, v in self.centers.items()}, "diameter": self.diameter}

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ActionSlots:
        if not data:
            return cls()
        return cls(
            centers={str(k): [float(v) for v in values] for k, values in data.get("centers", {}).items()},
            diameter=float(data.get("diameter", 0.24)),
        )


@dataclass
class RealmLayout:
    """Geometry of a single villain realm board (the template, not its screen position)."""

    name: str
    canvas: tuple[int, int]
    regions: dict[str, Region]
    cards: CardMetrics = field(default_factory=CardMetrics)
    background: str | None = None
    board_aspect: float | None = None
    board_fraction: float = 1.0
    action_slots: ActionSlots = field(default_factory=ActionSlots)

    def region(self, name: str) -> Region:
        try:
            return self.regions[name]
        except KeyError:
            raise KeyError(f"{self.name!r} has no region {name!r}") from None

    def region_at(self, nx: float, ny: float) -> Region | None:
        # Smallest matching region wins, so a card row inside a location panel is
        # targetable rather than the whole panel.
        matches = [r for r in self.regions.values() if r.rect.contains(nx, ny)]
        if not matches:
            return None
        return min(matches, key=lambda r: r.rect.w * r.rect.h)

    def board_rect(self, slot_box: Rect) -> Rect:
        """The part of the realm box occupied by the board art."""
        return Rect(slot_box.x, slot_box.y, slot_box.w, slot_box.h * self.board_fraction)

    def validate(self) -> list[str]:
        problems = [f"missing region {name!r}" for name in REQUIRED_REALM_REGIONS if name not in self.regions]
        for region in self.regions.values():
            r = region.rect
            if r.w <= 0 or r.h <= 0:
                problems.append(f"region {region.name!r} has zero area")
            if r.x < -0.001 or r.y < -0.001 or r.x + r.w > 1.001 or r.y + r.h > 1.001:
                problems.append(f"region {region.name!r} falls outside the canvas: {r.to_dict()}")
        for count, centers in self.action_slots.centers.items():
            if not centers:
                problems.append(f"action_slots[{count!r}] is empty")
            if any(not (0.0 < c < 1.0) for c in centers):
                problems.append(f"action_slots[{count!r}] centres outside 0..1: {centers}")
            if list(centers) != sorted(centers):
                problems.append(f"action_slots[{count!r}] centres not left-to-right: {centers}")
        return problems

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "canvas": {"width": self.canvas[0], "height": self.canvas[1]},
            "background": self.background,
            "board_aspect": self.board_aspect,
            "board_fraction": self.board_fraction,
            "cards": self.cards.to_dict(),
            "action_slots": self.action_slots.to_dict(),
            "regions": {k: v.to_dict() for k, v in self.regions.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RealmLayout:
        canvas = data.get("canvas", {})
        return cls(
            name=data["name"],
            canvas=(int(canvas.get("width", 1600)), int(canvas.get("height", 900))),
            regions={k: Region.from_dict(k, v) for k, v in data.get("regions", {}).items()},
            cards=CardMetrics.from_dict(data.get("cards")),
            background=data.get("background"),
            board_aspect=data.get("board_aspect"),
            board_fraction=float(data.get("board_fraction", 1.0)),
            action_slots=ActionSlots.from_dict(data.get("action_slots")),
        )


@dataclass(frozen=True)
class RealmSlot:
    """Where one player's realm sits on screen, and which player it shows."""

    player_index: int
    box: Rect

    def to_dict(self) -> dict[str, Any]:
        return {"player_index": self.player_index, "box": self.box.to_dict()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RealmSlot:
        return cls(player_index=int(data["player_index"]), box=Rect.from_dict(data["box"]))


@dataclass
class ScreenLayout:
    """Arranges realm slots plus screen-wide chrome (log, banner, header)."""

    name: str
    canvas: tuple[int, int]
    realms: list[RealmSlot]
    regions: dict[str, Region]

    def region(self, name: str) -> Region:
        try:
            return self.regions[name]
        except KeyError:
            raise KeyError(f"{self.name!r} has no region {name!r}") from None

    def validate(self) -> list[str]:
        problems = [f"missing region {name!r}" for name in REQUIRED_SCREEN_REGIONS if name not in self.regions]
        seen: set[int] = set()
        for slot in self.realms:
            if slot.player_index in seen:
                problems.append(f"duplicate realm slot for player {slot.player_index}")
            seen.add(slot.player_index)
            box = slot.box
            if box.x < -0.001 or box.y < -0.001 or box.x + box.w > 1.001 or box.y + box.h > 1.001:
                problems.append(f"player {slot.player_index} realm box outside canvas: {box.to_dict()}")
        if not self.realms:
            problems.append("no realm slots defined")
        return problems

    def slot_for(self, player_index: int) -> RealmSlot:
        for slot in self.realms:
            if slot.player_index == player_index:
                return slot
        raise KeyError(f"no realm slot for player {player_index}")

    def resolve(self, realm: RealmLayout, player_index: int, region_name: str) -> Rect:
        """Absolute normalized rect of a realm region once placed on screen."""
        slot = self.slot_for(player_index)
        local = realm.region(region_name).rect
        box = slot.box
        return Rect(
            x=box.x + local.x * box.w,
            y=box.y + local.y * box.h,
            w=local.w * box.w,
            h=local.h * box.h,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "canvas": {"width": self.canvas[0], "height": self.canvas[1]},
            "realms": [slot.to_dict() for slot in self.realms],
            "regions": {k: v.to_dict() for k, v in self.regions.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScreenLayout:
        canvas = data.get("canvas", {})
        return cls(
            name=data["name"],
            canvas=(int(canvas.get("width", 1600)), int(canvas.get("height", 900))),
            realms=[RealmSlot.from_dict(slot) for slot in data.get("realms", [])],
            regions={k: Region.from_dict(k, v) for k, v in data.get("regions", {}).items()},
        )


@dataclass
class LayoutBundle:
    """A screen arrangement plus the realm template it repeats."""

    screen: ScreenLayout
    realms: dict[str, RealmLayout]

    def realm_for_villain(self, villain: str) -> RealmLayout:
        key = villain.strip().lower().replace(" ", "_")
        for name, realm in self.realms.items():
            if name == key:
                return realm
        raise KeyError(f"no realm layout for villain {villain!r} (have {sorted(self.realms)})")

    def validate(self) -> list[str]:
        problems = list(self.screen.validate())
        for name, realm in self.realms.items():
            problems.extend(f"[{name}] {p}" for p in realm.validate())
        return problems


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_json(path: str | Path, data: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_screen(path: str | Path) -> ScreenLayout:
    return ScreenLayout.from_dict(load_json(path))


def load_realm(path: str | Path) -> RealmLayout:
    return RealmLayout.from_dict(load_json(path))


def load_bundle(screen_path: str | Path, realm_paths: dict[str, str | Path]) -> LayoutBundle:
    return LayoutBundle(
        screen=load_screen(screen_path),
        realms={name: load_realm(path) for name, path in realm_paths.items()},
    )
