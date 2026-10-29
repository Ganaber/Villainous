"""Screenshot renderer: draw a GameSnapshot fixture as a board image.

Renders straight from engine/UI/example_screenshots.json, so it works while the engine
is still mid-refactor. The renderer is a pure function of (snapshot, layout, assets):
no state is kept between frames and nothing is mutated.

    python -m engine.UI.render                  # window, arrow keys cycle fixtures
    python -m engine.UI.render --all --out out  # write one PNG per fixture
    python -m engine.UI.render --index 2        # just the mid-game example
    python -m engine.UI.render --list           # fixture names

Everything is drawn on a fixed virtual canvas and then scaled into the window, so
layout coordinates never depend on the window size.

The real board art already paints the action icons and the location names, so this
renderer *highlights* that artwork instead of drawing chips over it: legal actions get
a gold ring, and only dynamic content (cards, power, deck counts, mover) is drawn on top.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from engine.UI import assets
from engine.UI.layout import LAYOUT_DIR, LayoutBundle, Rect, load_bundle

CANVAS = (1600, 1100)
EXAMPLES_PATH = Path(__file__).parent / "example_screenshots.json"

# Card art is portrait (1000x1413); the renderer fits every card to this aspect.
CARD_ASPECT = 1000 / 1413
CARD_INSET = 4

BG = (10, 11, 16)
PANEL = (26, 28, 36)
ACCENT = (255, 198, 66)
INK = (240, 240, 248)
DIM_INK = (150, 154, 168)
GREEN = (94, 200, 140)
MOVE_ACCENT = (120, 190, 255)
SHADE = (6, 7, 12, 92)

_pygame = None


def pg():
    """Import pygame lazily so SDL env vars can be set first."""
    global _pygame
    if _pygame is None:
        import pygame

        _pygame = pygame
    return _pygame


# ===== fixtures =====
def load_examples(path: str | Path = EXAMPLES_PATH) -> list[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["examples"]


def load_layout() -> LayoutBundle:
    return load_bundle(
        LAYOUT_DIR / "dual_board_screen.json",
        {"wtia_prince_john": LAYOUT_DIR / "prince_john_realm.json"},
    )


def short_name(example: dict) -> str:
    return example.get("name", "example")


# ===== renderer =====
class Renderer:
    def __init__(self, bundle: LayoutBundle, canvas: tuple[int, int] | None = None) -> None:
        self.p = pg()
        self.p.font.init()
        self.bundle = bundle
        self.screen = bundle.screen
        self.realm = bundle.realm_for_villain("WTIA Prince John")
        self.canvas = canvas or self.screen.canvas
        self._images: dict[tuple[str, int, int], object] = {}
        self._fonts: dict[int, object] = {}

    # ---- primitives
    def font(self, size: int):
        size = max(8, int(size))
        if size not in self._fonts:
            self._fonts[size] = self.p.font.Font(None, size)
        return self._fonts[size]

    def image(self, key: str, size: tuple[int, int]):
        size = (max(1, size[0]), max(1, size[1]))
        cached = self._images.get((key, *size))
        if cached is not None:
            return cached
        path = assets.path(key)
        if path.is_file():
            surface = self.p.image.load(str(path))
            surface = self.p.transform.smoothscale(surface, size)
        else:
            surface = self.p.Surface(size)
            surface.fill((70, 40, 40))
            self.text(surface, key.split(":")[-1], surface.get_rect(), size=14, colour=INK)
        self._images[(key, *size)] = surface
        return surface

    def rect(self, normalized: Rect):
        x, y, w, h = normalized.pixels(*self.canvas)
        return self.p.Rect(x, y, w, h)

    def text(self, surf, body: str, box, size: int = 18, colour=INK, align: str = "center",
             min_size: int = 9) -> None:
        """Shrink to fit, then ellipsize."""
        width = box.width
        chosen = None
        for candidate in range(int(size), min_size - 1, -1):
            f = self.font(candidate)
            if f.size(body)[0] <= width:
                chosen = (f, body)
                break
        if chosen is None:
            f = self.font(min_size)
            chosen = (f, self._ellipsize(body, f, width))
        f, body = chosen
        image = f.render(body, True, colour)
        if align == "left":
            pos = (box.x, box.y + (box.height - image.get_height()) // 2)
        elif align == "right":
            pos = (box.right - image.get_width(), box.y + (box.height - image.get_height()) // 2)
        else:
            pos = (box.x + (box.width - image.get_width()) // 2,
                   box.y + (box.height - image.get_height()) // 2)
        surf.blit(image, pos)

    def _ellipsize(self, body: str, f, max_width: int) -> str:
        if f.size(body)[0] <= max_width:
            return body
        ellipsis = "..."
        low, high = 0, len(body)
        while low < high:
            mid = (low + high + 1) // 2
            if f.size(body[:mid].rstrip() + ellipsis)[0] <= max_width:
                low = mid
            else:
                high = mid - 1
        return (body[:low].rstrip() + ellipsis) if low else ellipsis

    def panel(self, surf, rect, fill=PANEL, border=None, radius: int = 6, width: int = 1) -> None:
        self.p.draw.rect(surf, fill, rect, border_radius=radius)
        if border:
            self.p.draw.rect(surf, border, rect, width=width, border_radius=radius)

    # ---- tokens (drawn, not images: no art dependency)
    def draw_power_token(self, surf, rect) -> None:
        self.p.draw.ellipse(surf, (196, 158, 62), rect)
        self.p.draw.ellipse(surf, (120, 94, 32), rect, width=max(1, rect.width // 12))
        self.text(surf, "P", rect, size=max(10, int(rect.height * 0.78)),
                  colour=(52, 40, 12), min_size=8)

    def draw_mover(self, surf, rect, label: str, labelled: bool = True) -> None:
        self.p.draw.ellipse(surf, (58, 96, 168), rect)
        self.p.draw.ellipse(surf, (226, 232, 244), rect, width=max(1, rect.width // 14))
        if labelled:
            self.text(surf, label, rect, size=max(8, int(rect.height * 0.62)),
                      colour=(238, 240, 248), min_size=7)

    # ---- cards
    def draw_cards(self, surf, region: Rect, cards: list[dict], highlight: set[str],
                   max_height: int | None = None) -> None:
        if not cards:
            return
        box = self.rect(region)
        metrics = self.realm.cards
        cap_h = round(metrics.height * self.canvas[1])
        if max_height is not None:
            cap_h = min(cap_h, max_height)
        height = max(14, min(cap_h, box.height - 2 * CARD_INSET))
        width = max(10, round(height * CARD_ASPECT))
        gap = max(2, round(metrics.gap * self.canvas[0]))

        count = len(cards)
        step = width + gap
        if count > 1 and width + step * (count - 1) > box.width:
            step = max(6, (box.width - width) // (count - 1))
        total = width + step * (count - 1)
        x = box.x + (box.width - total) // 2
        y = box.y + (box.height - height) // 2

        for index, card in enumerate(cards):
            destination = self.p.Rect(x + index * step, y, width, height)
            key = assets.face_key(card["name"], card["type"])
            surf.blit(self.image(key, (width, height)), destination)
            if card["id"] in highlight:
                self.p.draw.rect(surf, ACCENT, destination.inflate(6, 6), width=3, border_radius=4)

    # ---- action icons (painted on the board; we only highlight)
    def draw_action_highlights(self, surf, region: Rect, slots: list[dict],
                               veil_others: bool) -> None:
        if not slots:
            return
        centers = self.realm.action_slots.centers_for(len(slots))
        box = self.rect(region)
        if not centers:
            step = 1.0 / (len(slots) + 1)
            centers = [step * (i + 1) for i in range(len(slots))]

        for center, slot in zip(centers, slots):
            cx = box.x + center * box.width
            cy = box.y + box.height // 2
            diameter = self.realm.action_slots.diameter * box.width
            ring = self.p.Rect(round(cx - diameter / 2), round(cy - diameter / 2),
                               round(diameter), round(diameter))
            if slot.get("legal"):
                glow = self.p.Surface(ring.inflate(14, 14).size, self.p.SRCALPHA)
                self.p.draw.ellipse(glow, (255, 198, 66, 70), glow.get_rect())
                surf.blit(glow, ring.inflate(14, 14).topleft)
                self.p.draw.ellipse(surf, ACCENT, ring, width=4)
            elif veil_others:
                # Only dim the rest once something is actually chooseable, otherwise
                # an idle board just looks murky.
                veil = self.p.Surface(ring.size, self.p.SRCALPHA)
                self.p.draw.ellipse(veil, (0, 0, 0, 95), veil.get_rect())
                surf.blit(veil, ring.topleft)

    # ---- one realm
    def draw_realm(self, surf, snapshot: dict, slot) -> None:
        player = next((p for p in snapshot["players"] if p["index"] == slot.player_index), None)
        if player is None:
            return
        active = slot.player_index == snapshot["current_player_index"]

        board = self.rect(self.realm.board_rect(slot.box))
        surf.blit(self.image(self.realm.background, (board.width, board.height)), board)

        if not active:
            shade = self.p.Surface((board.width, board.height), self.p.SRCALPHA)
            shade.fill(SHADE)
            surf.blit(shade, board)
        else:
            self.p.draw.rect(surf, ACCENT, board.inflate(2, 2), width=2)

        def region(name: str) -> Rect:
            return self.screen.resolve(self.realm, slot.player_index, name)

        self._draw_locations(surf, snapshot, player, region, active)
        self._draw_hud(surf, player, region)
        self._draw_hand(surf, snapshot, player, region, active)

    def _draw_locations(self, surf, snapshot: dict, player: dict, region, active: bool) -> None:
        legal = (snapshot.get("legal_actions") or []) if active else []
        playable = {a["card_id"] for a in legal
                    if a.get("card_id") and a.get("intent") == "PLAY_CARD"}
        move_targets = {a["location_index"] for a in legal if a.get("intent") == "MOVE"}
        # Only dim un-chosen icons while the player is picking a location action.
        veil_others = snapshot.get("turn_stage") == "PERFORMING_ACTION" and any(
            a.get("intent") not in ("MOVE", None) for a in legal)

        for location in player["locations"]:
            index = location["index"]
            panel = self.rect(region(f"location.{index}.panel"))
            occupied = bool(location.get("is_occupied"))

            if index in move_targets:
                self.p.draw.rect(surf, MOVE_ACCENT, panel.inflate(4, 4), width=3, border_radius=10)
            if occupied:
                self.p.draw.rect(surf, ACCENT, panel.inflate(4, 4), width=3, border_radius=10)

            self.draw_action_highlights(surf, region(f"location.{index}.top_actions"),
                                        location["top_actions"], veil_others)
            self.draw_action_highlights(surf, region(f"location.{index}.bottom_actions"),
                                        location["bottom_actions"], veil_others)

            self.draw_cards(surf, region(f"location.{index}.top_cards"),
                            location["top_cards"], playable)
            self.draw_cards(surf, region(f"location.{index}.bottom_cards"),
                            location["bottom_cards"], playable)

            if occupied:
                badge = self.rect(region(f"location.{index}.mover"))
                self.p.draw.ellipse(surf, (18, 20, 28), badge)
                self.p.draw.ellipse(surf, ACCENT, badge, width=2)
                self.text(surf, f"P{player['index']}", badge, size=badge.height - 4,
                          colour=ACCENT, min_size=8)

    def _draw_hud(self, surf, player: dict, region) -> None:
        power = self.rect(region("board.power"))
        self.panel(surf, power, fill=(30, 26, 14), border=(150, 122, 44), radius=8, width=2)
        token_size = max(10, min(power.height - 8, 40))
        token = self.p.Rect(power.x + 5, power.y + (power.height - token_size) // 2,
                            token_size, token_size)
        self.draw_power_token(surf, token)
        self.text(surf, str(player["power"]),
                  self.p.Rect(token.right + 6, power.y, 60, power.height),
                  size=power.height - 8, colour=ACCENT, align="left", min_size=10)
        self.text(surf, "POWER",
                  self.p.Rect(token.right + 66, power.y,
                              power.right - token.right - 70, power.height),
                  size=15, colour=(206, 182, 120), align="left", min_size=8)

        self._draw_deck(surf, self.rect(region("board.villain_draw")),
                        player["villain_deck"], "card.back.villain")
        self._draw_deck(surf, self.rect(region("board.fate_draw")),
                        player["fate_deck"], "card.back.fate")
        self._draw_discard(surf, self.rect(region("board.villain_discard")),
                           player["villain_deck"]["discard"])
        self._draw_discard(surf, self.rect(region("board.fate_discard")),
                           player["fate_deck"]["discard"])

        if player["mover_loc"] == -1:
            self.draw_mover(surf, self.rect(region("board.mover")), "PJ")

    def _hud_row(self, surf, box, back_key, value: str, label: str, dim: bool = False) -> None:
        self.panel(surf, box, fill=(18, 19, 26), border=(72, 74, 92), radius=5)
        thumb_h = box.height - 4
        x = box.x + 3
        if back_key:
            thumb_w = max(6, round(thumb_h * CARD_ASPECT))
            surf.blit(self.image(back_key, (thumb_w, thumb_h)), (x, box.y + 2))
            x += thumb_w + 6
        self.text(surf, value, self.p.Rect(x, box.y, 40, box.height),
                  size=box.height - 6, colour=DIM_INK if dim else INK, align="left", min_size=8)
        self.text(surf, label, self.p.Rect(x + 36, box.y, box.right - x - 40, box.height),
                  size=13, colour=DIM_INK, align="right", min_size=6)

    def _draw_deck(self, surf, box, deck: dict, back_key: str) -> None:
        self._hud_row(surf, box, back_key, str(deck["draw_count"]), "DECK")

    def _draw_discard(self, surf, box, cards: list[dict]) -> None:
        if not cards:
            self._hud_row(surf, box, None, "0", "DISCARD", dim=True)
            return
        top_card = cards[-1]
        key = assets.face_key(top_card["name"], top_card["type"])
        self.panel(surf, box, fill=(18, 19, 26), border=(72, 74, 92), radius=5)
        thumb_h = box.height - 4
        thumb_w = max(6, round(thumb_h * CARD_ASPECT))
        surf.blit(self.image(key, (thumb_w, thumb_h)), (box.x + 3, box.y + 2))
        x = box.x + thumb_w + 9
        self.text(surf, f"x{len(cards)}", self.p.Rect(x, box.y, 40, box.height),
                  size=box.height - 6, colour=INK, align="left", min_size=8)
        self.text(surf, "DISCARD", self.p.Rect(x + 36, box.y, box.right - x - 40, box.height),
                  size=13, colour=DIM_INK, align="right", min_size=6)

    def _draw_hand(self, surf, snapshot: dict, player: dict, region, active: bool) -> None:
        playable = {a["card_id"] for a in (snapshot.get("legal_actions") or [])
                    if active and a.get("card_id") and a.get("intent") == "PLAY_CARD"}
        box = self.rect(region("board.hand"))
        self.panel(surf, box, fill=(20, 21, 28), border=(70, 74, 92), radius=8)
        self.text(surf, f"P{player['index']} HAND",
                  self.p.Rect(box.x + 6, box.y + 2, 80, 14), size=13, colour=DIM_INK, align="left")
        self.draw_cards(surf, region("board.hand"), player["hand"], playable,
                        max_height=box.height - 14)

    # ---- screen chrome
    def draw_header(self, surf, snapshot: dict) -> None:
        box = self.rect(self.screen.region("turn_header").rect)
        self.panel(surf, box, fill=(16, 17, 24), border=(60, 64, 80), radius=0)
        left = (f"VILLAINOUS  |  PRINCE JOHN MIRROR  |  TURN {snapshot['turn_num']}"
                f"  |  PLAYER {snapshot['current_player_index']}"
                f"  |  {snapshot['turn_stage']}")
        self.text(surf, left, self.p.Rect(box.x + 12, box.y, box.width - 24, box.height),
                  size=22, colour=INK, align="left")

    def draw_event_log(self, surf, snapshot: dict) -> None:
        box = self.rect(self.screen.region("event_log").rect)
        if snapshot.get("winner") is not None:
            self.draw_winner(surf, snapshot)
            return
        self.panel(surf, box, fill=(14, 15, 22), border=(52, 56, 72), radius=0)
        self.text(surf, "LAST EVENT", self.p.Rect(box.x + 14, box.y + 4, 140, 16),
                  size=14, colour=DIM_INK, align="left")
        self.text(surf, snapshot.get("last_event") or "-",
                  self.p.Rect(box.x + 14, box.y + 20, box.width - 28, 32),
                  size=26, colour=INK, align="left")
        legal = snapshot.get("legal_actions") or []
        summary = f"{len(legal)} legal action(s) for player {snapshot['current_player_index']}"
        self.text(surf, summary, self.p.Rect(box.x + 14, box.bottom - 24, box.width - 28, 20),
                  size=16, colour=DIM_INK, align="left")

    def draw_winner(self, surf, snapshot: dict) -> None:
        winner = snapshot.get("winner")
        if winner is None:
            return
        box = self.rect(self.screen.region("winner_banner").rect)
        self.panel(surf, box, fill=(16, 44, 30), border=GREEN, radius=0, width=3)
        self.text(surf, f"PLAYER {winner} WINS",
                  self.p.Rect(box.x + 18, box.y + 2, 300, box.height - 4),
                  size=box.height - 14, colour=GREEN, align="left")
        self.text(surf, snapshot.get("last_event") or "",
                  self.p.Rect(box.x + 330, box.y + 2, box.width - 350, box.height - 4),
                  size=22, colour=(186, 226, 202), align="left")

    def render(self, fixture: dict):
        snapshot = fixture["snapshot"]
        surf = self.p.Surface(self.canvas)
        surf.fill(BG)
        self.draw_header(surf, snapshot)
        for slot in self.screen.realms:
            self.draw_realm(surf, snapshot, slot)
        self.draw_event_log(surf, snapshot)
        return surf


# ===== window / cli =====
def scaled(surf, size: tuple[int, int]):
    p = pg()
    scale = min(size[0] / surf.get_width(), size[1] / surf.get_height())
    target = (max(1, round(surf.get_width() * scale)), max(1, round(surf.get_height() * scale)))
    image = p.transform.smoothscale(surf, target)
    frame = p.Surface(size)
    frame.fill((0, 0, 0))
    frame.blit(image, ((size[0] - target[0]) // 2, (size[1] - target[1]) // 2))
    return frame


def write_all(renderer: Renderer, fixtures: list[dict], out_dir: Path, start: int = 1) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for offset, fixture in enumerate(fixtures):
        destination = out_dir / f"{start + offset}_{short_name(fixture)}.png"
        renderer.p.image.save(renderer.render(fixture), str(destination))
        written.append(destination)
    return written


def run_window(renderer: Renderer, fixtures: list[dict], start: int, out_dir: Path) -> None:
    p = pg()
    p.display.init()
    info = p.display.Info()
    size = (min(1600, max(800, info.current_w - 80)), min(1100, max(600, info.current_h - 140)))
    screen = p.display.set_mode(size, p.RESIZABLE)
    p.display.set_caption("Villainous - UI fixtures")
    clock = p.time.Clock()

    index = start
    status = ""

    running = True
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    running = False
                elif event.key in (p.K_RIGHT, p.K_DOWN, p.K_SPACE):
                    index = (index + 1) % len(fixtures)
                elif event.key in (p.K_LEFT, p.K_UP):
                    index = (index - 1) % len(fixtures)
                elif event.key == p.K_s:
                    written = write_all(renderer, [fixtures[index]], out_dir, start=index + 1)
                    status = f"wrote {written[0].name}"
                elif event.key == p.K_a:
                    written = write_all(renderer, fixtures, out_dir)
                    status = f"wrote {len(written)} files"
            elif event.type == p.VIDEORESIZE:
                screen = p.display.set_mode((event.w, event.h), p.RESIZABLE)

        frame = scaled(renderer.render(fixtures[index]), screen.get_size())
        screen.blit(frame, (0, 0))
        if status:
            p.display.set_caption(f"Villainous - UI fixtures - {status}")
        p.display.flip()
        clock.tick(30)

    p.quit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--examples", type=Path, default=EXAMPLES_PATH, help="fixture file to render")
    parser.add_argument("--out", type=Path, default=Path("out"), help="directory for PNG output")
    parser.add_argument("--all", action="store_true", help="write every fixture and exit")
    parser.add_argument("--index", type=int, default=1, help="1-based fixture to show first (default 1)")
    parser.add_argument("--list", action="store_true", help="list fixtures and exit")
    parser.add_argument("--window", action="store_true", help="open the interactive viewer")
    args = parser.parse_args(argv)

    if not args.window:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

    fixtures = load_examples(args.examples)
    if not fixtures:
        print("no fixtures found")
        return 1

    if args.list:
        for index, fixture in enumerate(fixtures, start=1):
            print(f"{index}. {short_name(fixture)}")
        return 0

    renderer = Renderer(load_layout())

    if args.window:
        start = min(max(args.index - 1, 0), len(fixtures) - 1)
        run_window(renderer, fixtures, start, args.out)
        return 0

    if args.all:
        written = write_all(renderer, fixtures, args.out)
    else:
        picked = min(max(args.index, 1), len(fixtures))
        written = write_all(renderer, [fixtures[picked - 1]], args.out, start=picked)

    for path in written:
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
