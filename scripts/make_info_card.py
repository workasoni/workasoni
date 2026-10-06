#!/usr/bin/env python3
"""
Hand-authored neofetch-style info card that sits beside akash-ascii.svg.

Same 840 x 880 terminal window as the portrait so the two line up when the
README shows them side by side at equal widths. Each line fades and slides in
on a short stagger, so the panel looks like it's printing next to the portrait.
Pure CSS keyframes inside the SVG (GitHub runs those in <img>, never JS).

    python scripts/make_info_card.py             # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py    # frozen frame for previews

Edit CARD below when your details change.
"""
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

USER_HOST = "akash@github"

# (key, value) rows. key None = continuation line, ("", "") = blank spacer,
# ("#", text) = section heading
CARD = [
    ("Name", "Akash Soni"),
    ("Location", "Calgary, Alberta, Canada"),
    ("", ""),
    ("#", "experience"),
    ("Now", "Youth Worker @ CBFY"),
    (None, "Peace and Justice Program"),
    ("Prev", "Data Analyst @ WE Excel Software"),
    (None, "Marketing Ops Analyst @ SA Technologies"),
    (None, "Team Leader, Analytics @ Flipkart"),
    ("", ""),
    ("#", "education"),
    ("M.Ed.", "Leadership"),
    ("BCA", "Sikkim Manipal University"),
    ("Cert", "Microsoft Power BI"),
    ("", ""),
    ("#", "toolbox"),
    ("Data", "Python · SQL · Power BI · Excel"),
    ("AI", "Claude · agents · automation"),
    ("Builds", "FRIDAY voice assistant"),
    (None, "multi agent crews · second brain"),
    ("", ""),
    ("Focus", "youth · community · data for good"),
]

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
KEY = "#39d353"        # neon green, matches the heatmap's top end
HEAD = "#58a6ff"
SECTION = "#d2a8ff"

W, H = 840, 880        # == akash-ascii.svg canvas
PAD = 20
TITLEBAR_H = 30
LEFT = PAD + 24
KEY_W = 150
FS = 24
LINE_H = 30

STAGGER = 0.16
DUR = 0.45

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<style>'
    + ('' if STATIC else
       f'.l{{opacity:0;animation:in {DUR}s ease-out both}}'
       '@keyframes in{0%{opacity:0;transform:translateX(-12px)}100%{opacity:1;transform:translateX(0)}}'
       '.cur{animation:blink 1s steps(1) infinite}'
       '@keyframes blink{50%{opacity:0}}'
       '@media (prefers-reduced-motion: reduce){.l{opacity:1!important;transform:none!important;animation:none!important}}')
    + '</style>',
    f'<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">{USER_HOST}: ~$ neofetch</text>')

n = 0


def line(inner, y):
    global n
    delay = 0.2 + n * STAGGER
    n += 1
    style = '' if STATIC else f' style="animation-delay:{delay:.2f}s"'
    parts.append(f'<g class="l"{style}><text x="{LEFT}" y="{y:.1f}" font-size="{FS}" xml:space="preserve">'
                 f'{inner}</text></g>')


y = TITLEBAR_H + 52
# prompt + header, like real neofetch output
line(f'<tspan fill="{KEY}">$</tspan><tspan fill="{INK}"> neofetch</tspan>', y)
y += LINE_H * 1.25
line(f'<tspan fill="{HEAD}" font-weight="700">akash</tspan><tspan fill="{INK}">@</tspan>'
     f'<tspan fill="{HEAD}" font-weight="700">github</tspan>', y)
y += LINE_H * 0.85
line(f'<tspan fill="{MUTED}">{"-" * 30}</tspan>', y)
y += LINE_H

for key, val in CARD:
    if key == "" and val == "":
        y += LINE_H * 0.45
        continue
    k = html.escape(key or "")
    v = html.escape(val)
    if key == "#":
        line(f'<tspan fill="{SECTION}"># {v}</tspan>', y)
    elif key is None:
        line(f'<tspan x="{LEFT + KEY_W}" fill="{INK}">{v}</tspan>', y)
    else:
        line(f'<tspan fill="{KEY}" font-weight="700">{k}</tspan>'
             f'<tspan fill="{MUTED}">:</tspan>'
             f'<tspan x="{LEFT + KEY_W}" fill="{INK}">{v}</tspan>', y)
    y += LINE_H

# neofetch colour blocks
y += LINE_H * 0.2
blocks_delay = 0.2 + n * STAGGER
palette = ["#161b22", "#ff5f56", "#27c93f", "#ffbd2e", "#58a6ff", "#d2a8ff", "#39d353", "#e6edf3"]
style = '' if STATIC else f' style="animation-delay:{blocks_delay:.2f}s"'
parts.append(f'<g class="l"{style}>')
for i, c in enumerate(palette):
    parts.append(f'<rect x="{LEFT + i*36}" y="{y - 22:.1f}" width="32" height="24" rx="3" fill="{c}"/>')
parts.append('</g>')

# trailing prompt with a blinking block cursor
y = H - PAD - 6
cur_delay = blocks_delay + 0.3
style = '' if STATIC else f' style="animation-delay:{cur_delay:.2f}s"'
parts.append(f'<g class="l"{style}><text x="{LEFT}" y="{y:.1f}" font-size="{FS}" fill="{KEY}">$</text>'
             f'<rect class="cur" x="{LEFT + 24}" y="{y - 20:.1f}" width="13" height="24" fill="{INK}"/></g>')

parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}: {W} x {H}, {n} lines, {len(svg)//1024} KB")
