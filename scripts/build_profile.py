import json
import math
import os
import re
import urllib.request
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "anubrr21")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ASSETS = Path(__file__).resolve().parent.parent / "assets"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"

THEMES = {
    "dark": dict(bg0="#0d1117", bg1="#161b22", line="#30363d", text="#e6edf3", muted="#8b949e",
                 a="#58a6ff", b="#a371f7", c="#3fb950", dot="#21262d"),
    "light": dict(bg0="#ffffff", bg1="#f6f8fa", line="#d0d7de", text="#1f2328", muted="#656d76",
                  a="#0969da", b="#8250df", c="#1a7f37", dot="#eaeef2"),
}
LANG_COLOURS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#663399", "Kotlin": "#A97BFF", "Java": "#b07219", "C": "#555555", "C++": "#f34b7d",
    "Dockerfile": "#384d54", "Shell": "#89e051", "Jupyter Notebook": "#DA5B0B",
}
LINES = ["Computer vision and speech interfaces", "Full-stack web and Android", "Software you can wave at and talk to"]


def fetch(url, raw=False):
    headers = {"User-Agent": "profile-builder", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        headers["Authorization"] = "Bearer " + TOKEN
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    return body if raw else json.loads(body)


def collect():
    user = fetch(f"https://api.github.com/users/{USER}")
    repos = [r for r in fetch(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
    languages = {}
    for repo in repos:
        try:
            for name, size in fetch(repo["languages_url"]).items():
                languages[name] = languages.get(name, 0) + size
        except Exception:
            continue
    contributions = None
    try:
        page = fetch(f"https://github.com/users/{USER}/contributions", raw=True)
        found = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
        if found:
            contributions = int(found.group(1).replace(",", ""))
    except Exception:
        pass
    return {
        "repos": user.get("public_repos", len(repos)),
        "stars": sum(r["stargazers_count"] for r in repos),
        "language_count": len(languages),
        "contributions": contributions,
        "languages": sorted(languages.items(), key=lambda item: -item[1]),
    }


def hand_points():
    wrist = (0.50, 0.95)
    thumb = [(0.37, 0.83), (0.25, 0.73), (0.17, 0.63), (0.11, 0.53)]
    fingers = [((0.37, 0.56), (-0.12, -1.0), 0.34), ((0.48, 0.53), (0.0, -1.0), 0.38),
               ((0.58, 0.55), (0.10, -1.0), 0.34), ((0.67, 0.61), (0.24, -1.0), 0.27)]
    points = [wrist] + thumb
    for (mx, my), (dx, dy), length in fingers:
        norm = math.hypot(dx, dy)
        dx, dy = dx / norm, dy / norm
        points += [(mx + dx * length * k, my + dy * length * k) for k in (0.0, 0.45, 0.75, 1.0)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 10), (10, 11),
             (11, 12), (9, 13), (13, 14), (14, 15), (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17)]
    return points, edges


def header(theme):
    t = THEMES[theme]
    width, height = 1200, 340
    points, edges = hand_points()
    ox, oy, scale = 800, 26, 300
    px = [(ox + x * scale, oy + y * scale) for x, y in points]
    bones = "".join(
        f'<line x1="{px[a][0]:.1f}" y1="{px[a][1]:.1f}" x2="{px[b][0]:.1f}" y2="{px[b][1]:.1f}"/>' for a, b in edges)
    joints = "".join(
        f'<circle class="joint" cx="{x:.1f}" cy="{y:.1f}" r="{7 if i in (4, 8, 12, 16, 20) else 5}" '
        f'style="animation-delay:{i * 0.09:.2f}s"/>' for i, (x, y) in enumerate(px))
    tip = px[8]
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.4"/>' for x in range(40, width, 40) for y in range(40, height, 40))
    bars = "".join(
        f'<rect class="bar" x="{72 + i * 13}" y="262" width="7" height="34" rx="3.5" '
        f'style="animation-delay:{(i * 0.37) % 1.3:.2f}s"/>' for i in range(22))
    span = len(LINES) * 4
    typed = "".join(
        f'<text class="line" x="72" y="196" style="animation-delay:{i * 4}s">{text}</text>' for i, text in enumerate(LINES))
    visible = 100 / len(LINES)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Anubrata Bhattacharyya">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['a']}"/><stop offset="1" stop-color="{t['b']}"/></linearGradient>
<linearGradient id="bone" gradientUnits="userSpaceOnUse" x1="{ox}" y1="{oy + scale}" x2="{ox + scale}" y2="{oy}"><stop offset="0" stop-color="{t['a']}"/><stop offset="1" stop-color="{t['b']}"/></linearGradient>
<clipPath id="card"><rect width="{width}" height="{height}" rx="18"/></clipPath>
</defs>
<style>
.name{{font:700 54px {FONT};fill:{t['text']};letter-spacing:-1px}}
.role{{font:500 19px {MONO};fill:{t['muted']}}}
.line{{font:600 25px {FONT};fill:url(#accent);opacity:0;animation:show {span}s infinite}}
.tag{{font:500 15px {MONO};fill:{t['muted']}}}
.bones line{{stroke:url(#bone);stroke-width:3;stroke-linecap:round;opacity:.85}}
.joint{{fill:{t['bg0']};stroke:{t['a']};stroke-width:2.5;animation:pulse 2.8s ease-in-out infinite}}
.ring{{fill:none;stroke:{t['c']};stroke-width:2.5;opacity:0;transform-origin:{tip[0]:.1f}px {tip[1]:.1f}px;animation:tap 2.8s ease-out infinite}}
.bar{{fill:url(#accent);transform-box:fill-box;transform-origin:center;animation:speak 1.3s ease-in-out infinite}}
.hand{{animation:float 6s ease-in-out infinite}}
@keyframes show{{0%{{opacity:0;transform:translateY(8px)}}4%{{opacity:1;transform:translateY(0)}}{visible - 5:.1f}%{{opacity:1}}{visible:.1f}%{{opacity:0}}100%{{opacity:0}}}}
@keyframes pulse{{0%,100%{{stroke-opacity:.55}}50%{{stroke-opacity:1;stroke:{t['b']}}}}}
@keyframes tap{{0%{{opacity:.9;transform:scale(.4)}}70%{{opacity:0;transform:scale(3.2)}}100%{{opacity:0}}}}
@keyframes speak{{0%,100%{{transform:scaleY(.25)}}50%{{transform:scaleY(1)}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-7px)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.line:first-of-type{{opacity:1}}}}
</style>
<g clip-path="url(#card)">
<rect width="{width}" height="{height}" fill="url(#bg)"/>
<g fill="{t['dot']}">{dots}</g>
<rect x="0" y="0" width="6" height="{height}" fill="url(#accent)"/>
</g>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" fill="none" stroke="{t['line']}"/>
<text class="role" x="72" y="76">anubrr21 / B.Tech CSE, VIT-AP University</text>
<text class="name" x="70" y="140">Anubrata Bhattacharyya</text>
{typed}
<text class="tag" x="72" y="242">voice in</text>
{bars}
<g class="hand">
<g class="bones">{bones}</g>
{joints}
<circle class="ring" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="12"/>
</g>
</svg>
'''


def number(value):
    if value is None:
        return "-"
    return f"{value / 1000:.1f}k" if value >= 1000 else str(value)


def stats(theme, data):
    t = THEMES[theme]
    width, height = 1200, 250
    tiles = [("Public repositories", data["repos"]), ("Contributions, last year", data["contributions"]),
             ("Languages used", data["language_count"]), ("Stars earned", data["stars"])]
    tile_w = (width - 72 * 2 - 3 * 20) / 4
    parts = []
    for i, (label, value) in enumerate(tiles):
        x = 72 + i * (tile_w + 20)
        parts.append(
            f'<rect x="{x:.0f}" y="34" width="{tile_w:.0f}" height="92" rx="12" fill="{t["bg0"]}" stroke="{t["line"]}"/>'
            f'<text class="num" x="{x + 22:.0f}" y="82">{number(value)}</text>'
            f'<text class="lab" x="{x + 22:.0f}" y="108">{label}</text>')
    top = data["languages"][:6]
    total = sum(size for _, size in top) or 1
    bar_x, bar_w, x = 72, width - 144, 72.0
    segments, legend = [], []
    for i, (name, size) in enumerate(top):
        w = bar_w * size / total
        colour = LANG_COLOURS.get(name, t["muted"])
        segments.append(f'<rect x="{x:.1f}" y="158" width="{max(w, 2):.1f}" height="12" fill="{colour}"/>')
        lx = bar_x + i * (bar_w / len(top))
        legend.append(
            f'<circle cx="{lx + 6:.0f}" cy="204" r="6" fill="{colour}"/>'
            f'<text class="leg" x="{lx + 20:.0f}" y="209">{name} <tspan class="pct">{100 * size / total:.0f}%</tspan></text>')
        x += w
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="GitHub activity for {USER}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t['bg0']}"/><stop offset="1" stop-color="{t['bg1']}"/></linearGradient>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t['a']}"/><stop offset="1" stop-color="{t['b']}"/></linearGradient>
<clipPath id="bar"><rect x="{bar_x}" y="158" width="{bar_w}" height="12" rx="6"/></clipPath>
</defs>
<style>
.num{{font:700 36px {FONT};fill:url(#accent)}}
.lab{{font:500 15px {FONT};fill:{t['muted']}}}
.leg{{font:500 15px {FONT};fill:{t['text']}}}
.pct{{fill:{t['muted']}}}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="18" fill="url(#bg)" stroke="{t['line']}"/>
{"".join(parts)}
<g clip-path="url(#bar)">{"".join(segments)}</g>
{"".join(legend)}
</svg>
'''


def main():
    ASSETS.mkdir(exist_ok=True)
    data = collect()
    for theme in THEMES:
        (ASSETS / f"header-{theme}.svg").write_text(header(theme), encoding="utf-8")
        (ASSETS / f"stats-{theme}.svg").write_text(stats(theme, data), encoding="utf-8")
    print(json.dumps({k: v for k, v in data.items() if k != "languages"}), data["languages"][:6])


if __name__ == "__main__":
    main()
