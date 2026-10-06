import datetime
import json
import math
import os
import re
import urllib.request
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "anubrr21")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ASSETS = Path(__file__).resolve().parent.parent / "assets"
CACHE = ASSETS / "data.json"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

BG, PANEL, EDGE = "#070a12", "#0d1220", "#1d2740"
TEXT, MUTED = "#eef2ff", "#8d99b8"
CYAN, VIOLET, PINK, GREEN = "#00d4ff", "#8b5cf6", "#ff2d95", "#3dffa2"
LEVELS = ["#1b2540", "#0e7fa6", "#00d4ff", "#8b5cf6", "#ff2d95"]
LANG_COLOURS = {
    "Python": "#4b8bbe", "JavaScript": "#f7df1e", "TypeScript": "#3178c6", "HTML": "#ff6a3d",
    "CSS": "#b072ff", "Kotlin": "#c08bff", "Java": "#f89820", "C": "#9aa4b8", "C++": "#f34b7d",
    "Dockerfile": "#4aa3c7", "Shell": "#89e051",
}
TAGLINES = ["I build software you can wave at and talk to", "Computer vision, speech and full-stack",
            "Turning real-world signals into working products"]
PROJECTS = [
    dict(slug="handsfree", icon="hand", title="Hands Free Computer", accent=(CYAN, VIOLET),
         lines=["Control a laptop with one hand in the air and", "your voice. Gesture mouse, per-finger",
                "classifiers and a voice assistant."],
         tags=["Python", "MediaPipe", "scikit-learn", "OpenCV"]),
    dict(slug="weathergpt", icon="cloud", title="WeatherGPT", accent=(VIOLET, PINK),
         lines=["Weather assistant for India: official warnings,", "blended forecast models and live stations,",
                "explained in 13 Indian languages."],
         tags=["Python", "TypeScript", "Docker"]),
    dict(slug="itantra", icon="radio", title="iTantra", accent=(GREEN, CYAN),
         lines=["A digital walkie-talkie for low-bandwidth links:", "speech to text, sent over WiFi Direct or",
                "Bluetooth, spoken back in 10 languages."],
         tags=["Kotlin", "Android", "Python"]),
    dict(slug="weatherroute", icon="route", title="WeatherRoute", accent=(PINK, VIOLET),
         lines=["Plans a journey around the weather: live", "conditions, forecast, air quality and risk alerts",
                "on the route, with a chat interface."],
         tags=["React", "Node.js", "Express", "MongoDB"]),
    dict(slug="studybud", icon="chat", title="StudyBud", accent=(CYAN, GREEN),
         lines=["Real-time study groups for students, with", "instant messaging, profiles and verified",
                "sign-in. Deployed and running."],
         tags=["Python", "JavaScript", "HTML/CSS"]),
    dict(slug="neetcode", icon="code", title="NeetCode Log", accent=(VIOLET, CYAN),
         lines=["My running log of data-structures and", "algorithms problems, solved in Java and",
                "pushed as I go."],
         tags=["Java", "DSA"]),
]
ICONS = {
    "hand": '<path d="M9 30V14a3 3 0 0 1 6 0v10M15 22V9a3 3 0 0 1 6 0v13M21 22V11a3 3 0 0 1 6 0v13M27 24v-8a3 3 0 0 1 6 0v14c0 8-5 13-12 13-6 0-9-3-12-8l-5-9a3 3 0 0 1 5-3l3 4"/>',
    "cloud": '<path d="M12 30a8 8 0 0 1 1-16 11 11 0 0 1 21 3 7 7 0 0 1-1 13z"/><path d="M15 36l-2 5M22 36l-2 5M29 36l-2 5"/>',
    "radio": '<circle cx="22" cy="24" r="4"/><path d="M13 15a13 13 0 0 0 0 18M31 15a13 13 0 0 1 0 18M7 9a21 21 0 0 0 0 30M37 9a21 21 0 0 1 0 30"/>',
    "route": '<circle cx="10" cy="36" r="4"/><path d="M34 22c0-5-4-9-4-9s-4 4-4 9a4 4 0 0 0 8 0z" transform="translate(4 -6)"/><path d="M14 36h10a6 6 0 0 0 0-12h-4a6 6 0 0 1 0-12h8"/>',
    "chat": '<path d="M6 10h24v16H16l-7 6v-6H6z"/><path d="M34 18h6v14h-3v5l-6-5h-9"/>',
    "code": '<path d="M16 12L5 23l11 11M30 12l11 11-11 11M26 8l-6 30"/>',
}


def fetch(url, raw=False):
    headers = {"User-Agent": "profile-builder", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        headers["Authorization"] = "Bearer " + TOKEN
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
    return body if raw else json.loads(body)


def calendar():
    page = fetch(f"https://github.com/users/{USER}/contributions", raw=True)
    counts = {}
    for target, label in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', page):
        found = re.match(r"\s*(\d+|No)\s+contribution", label)
        if found:
            counts[target] = 0 if found.group(1) == "No" else int(found.group(1))
    days = []
    for cell in re.findall(r"<td[^>]*data-date=[^>]*>", page):
        date = re.search(r'data-date="([^"]+)"', cell).group(1)
        level = int(re.search(r'data-level="(\d)"', cell).group(1))
        ident = re.search(r'id="([^"]+)"', cell)
        days.append({"date": date, "level": level, "count": counts.get(ident.group(1) if ident else "", level)})
    days.sort(key=lambda d: d["date"])
    total = re.search(r"([\d,]+)\s+contributions?\s+in the last year", page)
    return days, int(total.group(1).replace(",", "")) if total else sum(d["count"] for d in days)


def collect():
    cached = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    data = dict(cached)
    try:
        days, total = calendar()
        if days:
            data["days"], data["contributions"] = days, total
    except Exception:
        pass
    try:
        user = fetch(f"https://api.github.com/users/{USER}")
        repos = [r for r in fetch(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
        languages = {}
        for repo in repos:
            for name, size in fetch(repo["languages_url"]).items():
                languages[name] = languages.get(name, 0) + size
        data.update(repos=user.get("public_repos", len(repos)), stars=sum(r["stargazers_count"] for r in repos),
                    languages=sorted(languages.items(), key=lambda item: -item[1]))
    except Exception:
        pass
    CACHE.write_text(json.dumps(data), encoding="utf-8")
    return data


def streaks(days):
    today = datetime.date.today().isoformat()
    past = [d for d in days if d["date"] <= today]
    longest = run = 0
    for d in past:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    for d in reversed(past):
        if d["count"]:
            current += 1
        elif d["date"] != today:
            break
    best = max(past, key=lambda d: d["count"]) if past else {"count": 0, "date": today}
    active = sum(1 for d in past if d["count"])
    return current, longest, best, active


def defs(extra=""):
    return f'''<defs>
<linearGradient id="neon" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{PANEL}"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
{extra}</defs>'''


def svg(width, height, label, body, style, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            f'role="img" aria-label="{label}">\n{defs(extra_defs)}\n<style>\n{style}\n'
            f'@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}\n</style>\n{body}\n</svg>\n')


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


def hero():
    width, height = 1200, 430
    points, edges = hand_points()
    ox, oy, scale = 770, 44, 340
    px = [(ox + x * scale, oy + y * scale) for x, y in points]
    cx, cy = ox + 0.42 * scale, oy + 0.56 * scale
    bones = "".join(f'<line x1="{px[a][0]:.1f}" y1="{px[a][1]:.1f}" x2="{px[b][0]:.1f}" y2="{px[b][1]:.1f}"/>'
                    for a, b in edges)
    joints = "".join(f'<circle class="joint" cx="{x:.1f}" cy="{y:.1f}" r="{7.5 if i in (4, 8, 12, 16, 20) else 5.5}" '
                     f'style="animation-delay:{i * 0.11:.2f}s"/>' for i, (x, y) in enumerate(px))
    tip = px[8]
    stars = "".join(
        f'<circle class="star" cx="{(i * 197) % width}" cy="{(i * 131) % height}" r="{1 + (i % 3) * 0.6:.1f}" '
        f'style="animation-delay:{(i * 0.37) % 4:.2f}s"/>' for i in range(46))
    bars = "".join(f'<rect class="bar" x="{74 + i * 12}" y="356" width="6" height="34" rx="3" '
                   f'style="animation-delay:{(i * 0.29) % 1.2:.2f}s"/>' for i in range(30))
    cycle = len(TAGLINES) * 5
    share = 100 / len(TAGLINES)
    typed = ""
    for i, line in enumerate(TAGLINES):
        w = len(line) * 15.1
        typed += (f'<g class="slot" style="animation-delay:{i * 5}s">'
                  f'<clipPath id="t{i}"><rect class="reveal" style="animation-delay:{i * 5}s" x="74" y="236" '
                  f'width="{w:.0f}" height="40"/></clipPath>'
                  f'<text class="typed" x="74" y="264" clip-path="url(#t{i})">{line}</text></g>')
    chips, x = "", 74
    for label in ("Computer Vision", "Speech", "Full-stack", "Android"):
        w = len(label) * 9.6 + 30
        chips += (f'<rect x="{x}" y="296" width="{w:.0f}" height="32" rx="16" fill="none" stroke="{EDGE}" stroke-width="1.5"/>'
                  f'<text class="chip" x="{x + w / 2:.0f}" y="317" text-anchor="middle">{label}</text>')
        x += w + 12
    style = f'''
.kicker{{font:600 17px {MONO};fill:{CYAN};letter-spacing:2px}}
.name{{font:800 66px {FONT};fill:{TEXT};letter-spacing:-1.5px}}
.typed{{font:600 25px {MONO};fill:url(#neon)}}
.chip{{font:600 14px {FONT};fill:{MUTED}}}
.cap{{font:600 13px {MONO};fill:{MUTED};letter-spacing:1.5px}}
.slot{{opacity:0;animation:slot {cycle}s infinite}}
.reveal{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:type {cycle}s steps(34) infinite}}
.blob{{animation:drift 14s ease-in-out infinite alternate}}
.star{{fill:{TEXT};opacity:.15;animation:twinkle 4s ease-in-out infinite}}
.bones line{{stroke:url(#bone);stroke-width:3.4;stroke-linecap:round}}
.joint{{fill:{BG};stroke:{CYAN};stroke-width:2.6;animation:pulse 2.6s ease-in-out infinite}}
.ring{{fill:none;stroke:{GREEN};stroke-width:3;opacity:0;transform-box:fill-box;transform-origin:center;animation:tap 2.6s ease-out infinite}}
.orbit{{fill:none;stroke:url(#neon);stroke-width:1.6;stroke-dasharray:3 13;opacity:.75;transform-origin:{cx:.0f}px {cy:.0f}px;animation:spin 40s linear infinite}}
.orbit2{{stroke-dasharray:60 26;opacity:.3;animation-duration:26s;animation-direction:reverse}}
.scan{{stroke:{CYAN};stroke-width:2;opacity:.0;animation:scan 5s ease-in-out infinite}}
.bar{{fill:url(#neon);transform-box:fill-box;transform-origin:center;animation:speak 1.2s ease-in-out infinite}}
.hand{{animation:float 6s ease-in-out infinite}}
.underline{{transform-box:fill-box;transform-origin:left;animation:grow 5s ease-in-out infinite alternate}}
@keyframes slot{{0%{{opacity:1}}{share - 1.5:.1f}%{{opacity:1}}{share:.1f}%{{opacity:0}}100%{{opacity:0}}}}
@keyframes type{{0%{{transform:scaleX(0)}}{share * 0.45:.1f}%{{transform:scaleX(1)}}{share:.1f}%{{transform:scaleX(1)}}100%{{transform:scaleX(1)}}}}
@keyframes drift{{0%{{transform:translate(0,0)}}100%{{transform:translate(90px,-40px)}}}}
@keyframes twinkle{{0%,100%{{opacity:.08}}50%{{opacity:.6}}}}
@keyframes pulse{{0%,100%{{stroke:{CYAN}}}50%{{stroke:{PINK}}}}}
@keyframes tap{{0%{{opacity:1;transform:scale(.3)}}70%{{opacity:0;transform:scale(3.4)}}100%{{opacity:0}}}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
@keyframes scan{{0%{{opacity:0;transform:translateY(0)}}15%{{opacity:.7}}85%{{opacity:.7}}100%{{opacity:0;transform:translateY({scale * 0.86:.0f}px)}}}}
@keyframes speak{{0%,100%{{transform:scaleY(.2)}}50%{{transform:scaleY(1)}}}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-9px)}}}}
@keyframes grow{{0%{{transform:scaleX(.35)}}100%{{transform:scaleX(1)}}}}'''
    body = f'''<clipPath id="frame"><rect width="{width}" height="{height}" rx="22"/></clipPath>
<g clip-path="url(#frame)">
<rect width="{width}" height="{height}" fill="{BG}"/>
<g filter="url(#blur)" opacity=".5">
<circle class="blob" cx="210" cy="60" r="170" fill="{VIOLET}"/>
<circle class="blob" cx="980" cy="380" r="190" fill="{CYAN}" style="animation-delay:-5s"/>
<circle class="blob" cx="640" cy="470" r="150" fill="{PINK}" style="animation-delay:-9s"/>
</g>
<rect width="{width}" height="{height}" fill="{BG}" opacity=".58"/>
{stars}
</g>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="21" fill="none" stroke="url(#neon)" stroke-width="2" opacity=".75"/>
<text class="kicker" x="74" y="92">B.TECH CSE / VIT-AP UNIVERSITY</text>
<text class="name" x="70" y="168">Anubrata Bhattacharyya</text>
<rect class="underline" x="74" y="190" width="430" height="5" rx="2.5" fill="url(#neon)"/>
{typed}
{chips}
<text class="cap" x="74" y="348">VOICE IN</text>
{bars}
<g class="hand">
<circle class="orbit" cx="{cx:.0f}" cy="{cy:.0f}" r="{scale * 0.56:.0f}"/>
<circle class="orbit orbit2" cx="{cx:.0f}" cy="{cy:.0f}" r="{scale * 0.63:.0f}"/>
<line class="scan" x1="{ox - 10}" y1="{oy + 28}" x2="{ox + scale * 0.86:.0f}" y2="{oy + 28}"/>
<g class="bones" filter="url(#glow)">{bones}</g>
{joints}
<circle class="ring" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="13"/>
<circle class="ring" cx="{tip[0]:.1f}" cy="{tip[1]:.1f}" r="13" style="animation-delay:.5s"/>
</g>
<text class="cap" x="{cx:.0f}" y="{height - 26}" text-anchor="middle">21 LANDMARKS TRACKED</text>'''
    bone = (f'<linearGradient id="bone" gradientUnits="userSpaceOnUse" x1="{ox}" y1="{oy + scale}" x2="{ox + scale}" y2="{oy}">'
            f'<stop offset="0" stop-color="{CYAN}"/><stop offset=".55" stop-color="{VIOLET}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>')
    return svg(width, height, "Anubrata Bhattacharyya", body, style, bone)


def terminal(data):
    width, height = 1200, 330
    current, longest, best, active = streaks(data.get("days", []))
    script = [
        ("$ whoami", TEXT),
        ("anubrata  /  computer science undergraduate, VIT-AP University", MUTED),
        ("$ cat focus.txt", TEXT),
        ("vision + speech interfaces, full-stack web, Android", CYAN),
        ("$ git log --since=1.year --oneline | wc -l", TEXT),
        (f"{data.get('contributions', 0)} contributions, {active} active days, longest streak {longest} days", GREEN),
        ("$ echo $STATUS", TEXT),
        ("building: Hands Free Computer, WeatherGPT", PINK),
    ]
    step, lines = 1.25, ""
    total = len(script) * step + 5
    for i, (text, colour) in enumerate(script):
        y = 96 + i * 27
        start = 100 * i * step / total
        end = 100 * (i * step + step * 0.8) / total
        w = len(text) * 10.3
        lines += (f'<clipPath id="l{i}"><rect class="k{i}" x="46" y="{y - 20}" width="{w:.0f}" height="28"/></clipPath>'
                  f'<text x="46" y="{y}" fill="{colour}" clip-path="url(#l{i})">{text}</text>')
        lines += (f'<style>.k{i}{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);'
                  f'animation:k{i} {total:.1f}s steps({max(len(text), 2)}) infinite}}'
                  f'@keyframes k{i}{{0%,{start:.2f}%{{transform:scaleX(0)}}{end:.2f}%,96%{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}</style>')
    style = f'''
text{{font:500 17px {MONO}}}
.title{{font:600 14px {FONT};fill:{MUTED}}}
.caret{{fill:{CYAN};animation:blink 1s steps(2) infinite}}
@keyframes blink{{50%{{opacity:0}}}}'''
    body = f'''<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#panel)" stroke="{EDGE}" stroke-width="1.5"/>
<rect x="1" y="1" width="{width - 2}" height="44" rx="18" fill="{EDGE}" opacity=".55"/>
<circle cx="32" cy="23" r="6.5" fill="#ff5f57"/><circle cx="54" cy="23" r="6.5" fill="#febc2e"/><circle cx="76" cy="23" r="6.5" fill="#28c840"/>
<text class="title" x="{width / 2}" y="28" text-anchor="middle">anubrata@github: ~</text>
{lines}
<rect class="caret" x="46" y="{96 + len(script) * 27 - 17}" width="10" height="20"/>'''
    return svg(width, height, "Terminal introduction", body, style)


def card(project):
    width, height = 590, 250
    a, b = project["accent"]
    text = "".join(f'<text class="desc" x="34" y="{128 + i * 25}">{line}</text>' for i, line in enumerate(project["lines"]))
    tags, x = "", 34
    for tag in project["tags"]:
        w = len(tag) * 8.4 + 22
        tags += (f'<rect x="{x}" y="204" width="{w:.0f}" height="26" rx="13" fill="{a}" opacity=".13"/>'
                 f'<text class="tag" x="{x + w / 2:.0f}" y="222" text-anchor="middle" fill="{a}">{tag}</text>')
        x += w + 8
    style = f'''
.title{{font:800 27px {FONT};fill:{TEXT};letter-spacing:-.4px}}
.desc{{font:500 16.5px {FONT};fill:{MUTED}}}
.tag{{font:700 12.5px {MONO}}}
.edge{{fill:none;stroke:url(#g);stroke-width:2;stroke-dasharray:240 1340;animation:run 7s linear infinite}}
.icon{{fill:none;stroke:url(#g);stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round;animation:beat 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
.halo{{animation:halo 5s ease-in-out infinite alternate}}
.arrow{{fill:none;stroke:{MUTED};stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}}
@keyframes run{{to{{stroke-dashoffset:-1580}}}}
@keyframes beat{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.08)}}}}
@keyframes halo{{0%{{opacity:.16}}100%{{opacity:.36}}}}'''
    grad = f'<linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient>'
    body = f'''<clipPath id="c"><rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18"/></clipPath>
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#panel)" stroke="{EDGE}" stroke-width="1.5"/>
<g clip-path="url(#c)"><circle class="halo" cx="{width - 60}" cy="30" r="150" fill="{a}" filter="url(#blur)"/></g>
<rect class="edge" x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18"/>
<rect x="34" y="30" width="60" height="60" rx="16" fill="{a}" opacity=".10"/>
<g transform="translate(42 37)"><g class="icon">{ICONS[project["icon"]]}</g></g>
<text class="title" x="112" y="70">{project["title"]}</text>
<path class="arrow" d="M{width - 62} 70 l20 -20 M{width - 58} 50 h16 v16"/>
{text}
{tags}'''
    return svg(width, height, project["title"], body, style, grad)


def stats(data):
    width, height = 1200, 300
    languages = data.get("languages", [])[:6]
    total = sum(size for _, size in languages) or 1
    current, longest, best, active = streaks(data.get("days", []))
    tiles = [("Contributions", data.get("contributions", 0), "in the last year", CYAN),
             ("Repositories", data.get("repos", 0), "public", VIOLET),
             ("Longest streak", longest, "days in a row", PINK),
             ("Best day", best["count"], best["date"], GREEN)]
    parts = ""
    for i, (label, value, note, colour) in enumerate(tiles):
        x, y = 36 + (i % 2) * 290, 36 + (i // 2) * 118
        parts += (f'<rect x="{x}" y="{y}" width="270" height="100" rx="14" fill="{BG}" stroke="{EDGE}" stroke-width="1.5"/>'
                  f'<rect x="{x}" y="{y + 22}" width="4" height="56" rx="2" fill="{colour}"/>'
                  f'<text class="num" x="{x + 24}" y="{y + 52}" fill="{colour}">{value}</text>'
                  f'<text class="lab" x="{x + 24}" y="{y + 78}">{label} <tspan class="note">{note}</tspan></text>')
    cx, cy, r = 760, 150, 88
    circumference = 2 * math.pi * r
    offset, ring, legend = 0.0, "", ""
    for i, (name, size) in enumerate(languages):
        frac = size / total
        colour = LANG_COLOURS.get(name, MUTED)
        ring += (f'<circle class="arc" cx="{cx}" cy="{cy}" r="{r}" stroke="{colour}" '
                 f'stroke-dasharray="{max(frac * circumference - 3, 1):.1f} {circumference:.1f}" '
                 f'stroke-dashoffset="{-offset:.1f}" style="animation-delay:{i * 0.5:.2f}s"/>')
        offset += frac * circumference
        y = 62 + i * 34
        legend += (f'<rect x="900" y="{y - 11}" width="14" height="14" rx="4" fill="{colour}"/>'
                   f'<text class="leg" x="926" y="{y + 1}">{name}</text>'
                   f'<text class="pct" x="1160" y="{y + 1}" text-anchor="end">{100 * frac:.0f}%</text>'
                   f'<rect x="1020" y="{y - 7}" width="96" height="6" rx="3" fill="{EDGE}"/>'
                   f'<rect class="fill" x="1020" y="{y - 7}" width="{max(96 * frac / (languages[0][1] / total), 3):.0f}" height="6" rx="3" '
                   f'fill="{colour}" style="animation-delay:{i * 0.15:.2f}s"/>')
    style = f'''
.num{{font:800 38px {FONT}}}
.lab{{font:600 15px {FONT};fill:{TEXT}}}
.note{{font-weight:500;fill:{MUTED}}}
.leg{{font:600 15px {FONT};fill:{TEXT}}}
.pct{{font:600 14px {MONO};fill:{MUTED}}}
.mid{{font:800 30px {FONT};fill:{TEXT}}}
.sub{{font:600 12px {MONO};fill:{MUTED};letter-spacing:1.5px}}
.arc{{fill:none;stroke-width:20;transform:rotate(-90deg);transform-origin:{cx}px {cy}px;animation:arc 8s ease-in-out infinite}}
.fill{{transform-box:fill-box;transform-origin:left;animation:fill 8s ease-out infinite}}
@keyframes arc{{0%,20%,100%{{stroke-width:20}}10%{{stroke-width:27}}}}
@keyframes fill{{0%,14%,100%{{transform:scaleX(1)}}3%{{transform:scaleX(.08)}}}}'''
    body = f'''<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#panel)" stroke="{EDGE}" stroke-width="1.5"/>
{parts}
<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{EDGE}" stroke-width="20" opacity=".5"/>
{ring}
<text class="mid" x="{cx}" y="{cy + 4}" text-anchor="middle">{len(data.get("languages", []))}</text>
<text class="sub" x="{cx}" y="{cy + 26}" text-anchor="middle">LANGUAGES</text>
{legend}'''
    return svg(width, height, "GitHub statistics", body, style)


def mix(colour, other, amount):
    a = [int(colour[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(other[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * amount):02x}" for x, y in zip(a, b))


def skyline(data):
    width, height = 1200, 470
    days = data.get("days", [])
    if not days:
        return svg(width, height, "Contribution skyline", "", "")
    first = datetime.date.fromisoformat(days[0]["date"])
    start = first - datetime.timedelta(days=(first.weekday() + 1) % 7)
    a, b, unit = 9.6, 5.0, 15.0
    ox, oy = 150, 128
    cells = []
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        week, dow = (date - start).days // 7, (date.weekday() + 1) % 7
        cells.append((week, dow, d))
    cells.sort(key=lambda c: (c[0] + c[1], c[0]))
    weeks = max(c[0] for c in cells) + 1
    peak = max(d["count"] for _, _, d in cells) or 1
    blocks = ""
    for week, dow, d in cells:
        x = ox + (week - dow) * a + 7 * a
        y = oy + (week + dow) * b
        level = d["level"]
        h = 3 if not d["count"] else 10 + 86 * (d["count"] / peak) ** 0.62
        colour = LEVELS[level]
        top = f"{x:.1f},{y - h:.1f} {x + a:.1f},{y + b - h:.1f} {x:.1f},{y + 2 * b - h:.1f} {x - a:.1f},{y + b - h:.1f}"
        left = f"{x - a:.1f},{y + b - h:.1f} {x:.1f},{y + 2 * b - h:.1f} {x:.1f},{y + 2 * b:.1f} {x - a:.1f},{y + b:.1f}"
        right = f"{x + a:.1f},{y + b - h:.1f} {x:.1f},{y + 2 * b - h:.1f} {x:.1f},{y + 2 * b:.1f} {x + a:.1f},{y + b:.1f}"
        cls = "b lit" if level >= 3 else "b"
        blocks += (f'<g class="{cls}" style="animation-delay:{week * 0.06:.2f}s">'
                   f'<polygon points="{left}" fill="{mix(colour, BG, .55)}"/>'
                   f'<polygon points="{right}" fill="{mix(colour, BG, .3)}"/>'
                   f'<polygon points="{top}" fill="{colour}"/></g>')
    current, longest, best, active = streaks(days)
    month_labels, seen = "", set()
    for week, dow, d in cells:
        date = datetime.date.fromisoformat(d["date"])
        if dow == 6 and date.day <= 7 and (date.year, date.month) not in seen:
            seen.add((date.year, date.month))
            x = ox + (week - 6) * a + 7 * a - 26
            y = oy + (week + 6) * b + 26
            month_labels += f'<text class="mon" x="{x:.0f}" y="{y:.0f}">{date.strftime("%b").upper()}</text>'
    style = f'''
.h{{font:800 30px {FONT};fill:{TEXT};letter-spacing:-.4px}}
.s{{font:600 13px {MONO};fill:{MUTED};letter-spacing:1.5px}}
.v{{font:800 26px {FONT}}}
.mon{{font:600 11px {MONO};fill:{MUTED};letter-spacing:1px}}
.b{{animation:wave 7s ease-in-out infinite}}
@keyframes wave{{0%,12%,100%{{transform:translateY(0)}}6%{{transform:translateY(-7px)}}}}'''
    facts = [("TOTAL", data.get("contributions", 0), CYAN), ("ACTIVE DAYS", active, VIOLET),
             ("LONGEST STREAK", f"{longest}d", PINK), ("BEST DAY", best["count"], GREEN)]
    side = "".join(f'<text class="s" x="{width - 250}" y="{92 + i * 78}">{label}</text>'
                   f'<text class="v" x="{width - 250}" y="{124 + i * 78}" fill="{colour}">{value}</text>'
                   for i, (label, value, colour) in enumerate(facts))
    legend = "".join(f'<rect x="{60 + i * 22}" y="{height - 44}" width="16" height="16" rx="4" fill="{c}"/>'
                     for i, c in enumerate(LEVELS))
    body = f'''<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#panel)" stroke="{EDGE}" stroke-width="1.5"/>
<text class="h" x="46" y="60">A year of commits, as a city</text>
<text class="s" x="46" y="86">EVERY BLOCK IS ONE DAY. TALLER MEANS MORE CONTRIBUTIONS.</text>
{blocks}
{month_labels}
{side}
<text class="s" x="46" y="{height - 54}">LESS</text>
{legend}
<text class="s" x="{60 + len(LEVELS) * 22 + 6}" y="{height - 31}">MORE</text>'''
    return svg(width, height, "Contribution skyline", body, style)


def divider():
    width, height = 1200, 14
    style = '''.run{animation:run 5s linear infinite}
@keyframes run{to{transform:translateX(480px)}}'''
    body = f'''<clipPath id="d"><rect x="0" y="5" width="{width}" height="4" rx="2"/></clipPath>
<rect x="0" y="5" width="{width}" height="4" rx="2" fill="{EDGE}"/>
<g clip-path="url(#d)"><g class="run">''' + "".join(
        f'<rect x="{-480 + i * 480}" y="5" width="170" height="4" fill="url(#neon)"/>' for i in range(5)) + "</g></g>"
    return svg(width, height, "", body, style)


def main():
    ASSETS.mkdir(exist_ok=True)
    data = collect()
    outputs = {"hero.svg": hero(), "terminal.svg": terminal(data), "stats.svg": stats(data),
               "skyline.svg": skyline(data), "divider.svg": divider()}
    for project in PROJECTS:
        outputs[f"card-{project['slug']}.svg"] = card(project)
    for name, content in outputs.items():
        (ASSETS / name).write_text(content, encoding="utf-8")
    print({k: data.get(k) for k in ("repos", "stars", "contributions")}, len(data.get("days", [])), "days")


if __name__ == "__main__":
    main()
