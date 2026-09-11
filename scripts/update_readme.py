#!/usr/bin/env python3
"""Generate the daily cellular automaton and update its README caption."""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RULES = (30, 60, 90, 105, 110, 150)


def make_art(day, theme="dark"):
    rule = RULES[day.toordinal() % len(RULES)]
    seed = hashlib.sha256(f"Amirali-Amirifar:{day}".encode()).digest()
    width, height = 280, 84
    cells = [0] * width
    # Sparse starting points let the geometry emerge instead of filling the frame with noise.
    for i, position in enumerate((60, 140, 220)):
        cells[position + seed[i] % 17 - 8] = 1
    rows = []

    for y in range(height):
        segments = []
        for x, alive in enumerate(cells):
            if alive:
                segments.append(f"M{60 + x * 3} {65 + y * 3}h2.3v2.3h-2.3z")
        rows.append(f'<path d="{"".join(segments)}"/>')

        next_row = []
        for x in range(width):
            # The edges wrap around. Each three-cell neighborhood selects a rule bit.
            left = cells[(x - 1) % width]
            center = cells[x]
            right = cells[(x + 1) % width]
            neighborhood = (left << 2) | (center << 1) | right
            next_row.append((rule >> neighborhood) & 1)
        cells = next_row

    background, border, ink = {
        "dark": ("#141618", "#2c2f32", "#58a6ff"),
        "light": ("#f6f8fa", "#d1d9e0", "#0969da"),
    }[theme]
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 376">',
        f'<rect x=".5" y=".5" width="959" height="375" rx="8" fill="{background}" stroke="{border}"/>',
        f'<g fill="{ink}">',
        *rows,
        '</g>',
        '</svg>\n',
    ]
    return rule, "\n".join(svg)


def update_daily_art(readme, rule, day):
    headings = list(re.finditer(r"^### Daily Art[ \t]*$", readme, re.MULTILINE))
    if len(headings) != 1:
        raise ValueError("Expected one '### Daily Art' heading in README.md")

    start = headings[0].end()
    next_section = re.search(r"^#{1,3} ", readme[start:], re.MULTILINE)
    end = start + next_section.start() if next_section else len(readme)
    section = (
        "\n\nDaily patterns from [elementary cellular automata]"
        "(https://en.wikipedia.org/wiki/Elementary_cellular_automaton).\n\n"
        '<picture>\n'
        '  <source media="(prefers-color-scheme: dark)" srcset="assets/daily.svg">\n'
        '  <source media="(prefers-color-scheme: light)" srcset="assets/daily-light.svg">\n'
        '  <img src="assets/daily.svg" alt="Blue cellular automaton with branching geometric patterns" width="960">\n'
        '</picture>\n\n'
        f"<sub>Rule {rule} · {day} (UTC) · [Source](scripts/update_readme.py)</sub>\n"
    )
    return readme[:start] + section + ("\n" if next_section else "") + readme[end:]


def main():
    day = datetime.now(timezone.utc).date()
    rule, svg = make_art(day)
    _, light_svg = make_art(day, "light")
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text()

    readme = update_daily_art(readme, rule, day)

    (ROOT / "assets").mkdir(exist_ok=True)
    (ROOT / "assets/daily.svg").write_text(svg)
    (ROOT / "assets/daily-light.svg").write_text(light_svg)
    readme_path.write_text(readme)
    print(f"Generated rule {rule} for {day}.")


if __name__ == "__main__":
    main()
