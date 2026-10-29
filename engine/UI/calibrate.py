"""Interactive layout calibrator.

Turn a screenshot into a realm layout once, by dragging a box over each named region.
Re-run it whenever the art or the arrangement changes.

    python -m engine.UI.calibrate                     # calibrate the placeholder art
    python -m engine.UI.calibrate assets/boards/pj.png
    python -m engine.UI.calibrate shot.png --box 0,0,0.5,1   # only the left realm

Controls
    drag           set the current region
    Backspace      undo the last region
    Space / Enter  skip the current region (leaves its previous value)
    S              save and keep going
    Esc            quit (you are asked to save if there are unsaved changes)

Regions are stored normalized to the calibrated box, so the same template works at
any window size. Everything the renderer needs is in the *realm* template; the screen
arrangement (which player sits where) lives in dual_board_screen.json.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from engine.UI import assets
from engine.UI.layout import (
    LAYOUT_DIR,
    REQUIRED_REALM_REGIONS,
    Rect,
    RealmLayout,
    load_json,
    save_json,
)

WINDOW_SIZE = (1280, 800)
BACKGROUND = (24, 24, 28)
DONE_COLOUR = (60, 190, 120)
CURRENT_COLOUR = (250, 200, 60)
TEXT_COLOUR = (235, 235, 235)
SKIPPED_COLOUR = (90, 90, 110)

DEFAULT_OUT = LAYOUT_DIR / "prince_john_realm.json"


def synthetic_reference(width: int = 1600, height: int = 900):
    """Stand-in 'screenshot' so the tool is usable before real art lands."""
    import pygame

    surf = pygame.Surface((width, height))
    surf.fill((40, 44, 52))
    for i in range(1, 4):
        x = round(width * (0.170 + i * 0.2075))
        pygame.draw.line(surf, (80, 86, 96), (x, 0), (x, height), 2)
    pygame.draw.rect(surf, (60, 66, 78), (0, 0, round(width * 0.165), round(height * 0.79)))
    pygame.draw.rect(surf, (60, 66, 78), (0, round(height * 0.79), width, round(height * 0.21)))
    return surf


def load_reference(path: Path | None):
    import pygame

    if path is None or not path.is_file():
        print(f"no reference image at {path}; using a synthetic grid", file=sys.stderr)
        return synthetic_reference()
    return pygame.image.load(str(path))


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def parse_box(text: str) -> Rect:
    try:
        x, y, w, h = (float(part) for part in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError("--box expects x,y,w,h in 0..1") from None
    return Rect(x, y, w, h)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("image", nargs="?", type=Path,
                        default=assets.path("board.wtia_prince_john"),
                        help="screenshot to calibrate against (default: the Prince John board asset)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help=f"layout to write (default {DEFAULT_OUT.name})")
    parser.add_argument("--box", type=parse_box, default=Rect(0.0, 0.0, 1.0, 1.0),
                        help="sub-rectangle of the image that is one realm, as x,y,w,h")
    args = parser.parse_args(argv)

    import pygame

    pygame.init()
    pygame.display.set_caption("Layout calibrator")

    reference = load_reference(args.image)
    image_w, image_h = reference.get_size()

    existing = RealmLayout.from_dict(load_json(args.out)) if args.out.is_file() else None
    located: dict[str, Rect] = {}
    if existing:
        located = {name: region.rect for name, region in existing.regions.items()}

    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 16)
    small = pygame.font.SysFont("consolas", 13)

    # Fit the *realm box* of the image into the window.
    box_px_w = args.box.w * image_w
    box_px_h = args.box.h * image_h
    scale = min(WINDOW_SIZE[0] / box_px_w, (WINDOW_SIZE[1] - 70) / box_px_h)
    drawn_w, drawn_h = round(box_px_w * scale), round(box_px_h * scale)
    offset = ((WINDOW_SIZE[0] - drawn_w) // 2, 70 + (WINDOW_SIZE[1] - 70 - drawn_h) // 2)

    def to_image(pos: tuple[int, int]) -> tuple[float, float] | None:
        """Window pixel -> normalized position inside the calibrated box."""
        nx = (pos[0] - offset[0]) / drawn_w
        ny = (pos[1] - offset[1]) / drawn_h
        if not (0.0 <= nx <= 1.0 and 0.0 <= ny <= 1.0):
            return None
        return clamp01(nx), clamp01(ny)

    def to_window(nx: float, ny: float) -> tuple[int, int]:
        return offset[0] + round(nx * drawn_w), offset[1] + round(ny * drawn_h)

    index = 0
    start: tuple[float, float] | None = None
    drag: tuple[float, float] | None = None
    dirty = False
    message = ""

    def current_name() -> str | None:
        return REQUIRED_REALM_REGIONS[index] if index < len(REQUIRED_REALM_REGIONS) else None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    save(located, existing, args.out)
                    dirty = False
                    message = f"saved {len(located)} regions to {args.out.name}"
                elif event.key == pygame.K_BACKSPACE and index > 0:
                    index -= 1
                    located.pop(REQUIRED_REALM_REGIONS[index], None)
                    dirty = True
                    message = ""
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if current_name():
                        message = f"skipped {current_name()}"
                        index += 1
                elif event.key == pygame.K_HOME:
                    index = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                start = to_image(event.pos)
                drag = start
            elif event.type == pygame.MOUSEMOTION and start:
                drag = to_image(event.pos) or drag
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and start and drag:
                name = current_name()
                if name:
                    x0, x1 = sorted((start[0], drag[0]))
                    y0, y1 = sorted((start[1], drag[1]))
                    if x1 - x0 > 0.002 and y1 - y0 > 0.002:
                        located[name] = Rect(round(x0, 4), round(y0, 4), round(x1 - x0, 4), round(y1 - y0, 4))
                        dirty = True
                        index += 1
                        message = ""
                start = drag = None

        # ---- draw
        screen.fill(BACKGROUND)
        realm_px = pygame.Rect(
            round(args.box.x * image_w),
            round(args.box.y * image_h),
            round(box_px_w),
            round(box_px_h),
        )
        realm_px = realm_px.clip(reference.get_rect())
        scaled = pygame.transform.smoothscale(reference.subsurface(realm_px), (drawn_w, drawn_h))
        screen.blit(scaled, offset)

        for name, rect in located.items():
            colour = DONE_COLOUR if name == current_name() else SKIPPED_COLOUR
            pygame.draw.rect(screen, colour, (*to_window(rect.x, rect.y), round(rect.w * drawn_w), round(rect.h * drawn_h)), 2)
            screen.blit(small.render(name, True, colour), (to_window(rect.x, rect.y)[0] + 3, to_window(rect.x, rect.y)[1] + 2))

        if start and drag:
            x0, x1 = sorted((start[0], drag[0]))
            y0, y1 = sorted((start[1], drag[1]))
            preview = pygame.Rect(*to_window(x0, y0), round((x1 - x0) * drawn_w), round((y1 - y0) * drawn_h))
            pygame.draw.rect(screen, CURRENT_COLOUR, preview, 2)

        name = current_name()
        progress = f"{index + 1}/{len(REQUIRED_REALM_REGIONS)}"
        header = f"[{progress}] drag: {name}" if name else f"[{progress}] all regions set - S to save, Esc to quit"
        screen.blit(font.render(header, True, TEXT_COLOUR), (12, 10))
        hint = "drag=set   Backspace=undo   Space=skip   S=save   Esc=quit" + ("   *unsaved*" if dirty else "")
        screen.blit(small.render(hint, True, (170, 170, 180)), (12, 32))
        if message:
            screen.blit(small.render(message, True, DONE_COLOUR), (12, 50))
        if existing and existing.cards:
            screen.blit(small.render(
                f"cards {existing.cards.width:.3f} x {existing.cards.height:.3f} (edit JSON to change)",
                True, (170, 170, 180)), (WINDOW_SIZE[0] - 340, 32))

        pygame.display.flip()
        clock.tick(60)

    if dirty:
        print(f"unsaved changes; writing {args.out}", file=sys.stderr)
        save(located, existing, args.out)

    pygame.quit()
    return 0


def save(located: dict[str, Rect], existing: RealmLayout | None, out: Path) -> None:
    """Merge the dragged rects into the layout file, preserving cards/background."""
    if existing:
        data = existing.to_dict()
    else:
        data = RealmLayout(
            name=out.stem,
            canvas=(1600, 900),
            regions={},
            background="board.wtia_prince_john",
        ).to_dict()

    for name, rect in located.items():
        previous = data["regions"].get(name, {})
        data["regions"][name] = {**previous, "rect": rect.to_dict()}

    save_json(out, data)
    print(f"saved {len(located)}/{len(REQUIRED_REALM_REGIONS)} regions to {out}")


if __name__ == "__main__":
    raise SystemExit(main())
