"""Draws the mission stats card from GitHub data.
python3 stats.py --query            prints the GraphQL query (pass it to `gh api graphql -F login=...`)
python3 stats.py data.json out.svg  renders the card from the query's JSON result"""
import json, sys
from datetime import date

QUERY = """query($login: String!) { user(login: $login) {
  contributionsCollection { totalCommitContributions contributionCalendar { totalContributions } }
  repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) { nodes {
    name homepageUrl stargazerCount
    repositoryTopics(first: 20) { nodes { topic { name } } }
    languages(first: 10) { edges { size node { name color } } } } } } }"""

if sys.argv[1] == "--query":
    print(QUERY)
    sys.exit()

user = json.load(open(sys.argv[1]))["data"]["user"]
repos = [r for r in user["repositories"]["nodes"] if r["name"].lower() != "amritanshu-nirjhar"]
cc = user["contributionsCollection"]
tiles = [
    ("LIVE SITES", sum(1 for r in repos if r["homepageUrl"])),
    ("PUBLIC PROJECTS", len(repos)),
    ("3D / WEBGL BUILDS", sum(1 for r in repos if {"threejs", "webgl", "react-three-fiber"} & {t["topic"]["name"] for t in r["repositoryTopics"]["nodes"]})),
    ("COMMITS · 12 MO", cc["totalCommitContributions"]),
    ("CONTRIBUTIONS · 12 MO", cc["contributionCalendar"]["totalContributions"]),
    ("STARS EARNED", sum(r["stargazerCount"] for r in repos)),
]
langs = {}
for r in repos:
    for e in r["languages"]["edges"]:
        name = e["node"]["name"]
        size, colour = langs.get(name, (0, e["node"]["color"] or "#888"))
        langs[name] = (size + e["size"], colour)
top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:5]
total = sum(s for _, (s, _) in top) or 1

MONO = "SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
W, H = 860, 330
cells = []
for i, (label, value) in enumerate(tiles):
    x, y = 24 + (i % 3) * 276, 58 + (i // 3) * 92
    cells.append(f'''<g><rect x="{x}" y="{y}" width="260" height="80" rx="10" fill="#1c1208" stroke="#ff8c00" stroke-opacity="0.35"/>
<text x="{x + 18}" y="{y + 48}" font-size="34" font-weight="700" fill="#ffc300">{value:,}</text>
<text x="{x + 18}" y="{y + 68}" font-size="11" letter-spacing="1.5" fill="#ffb000" opacity="0.8">{label}</text></g>''')
bar, legend, x = [], [], 24
for i, (name, (size, colour)) in enumerate(top):
    w = 812 * size / total
    bar.append(f'<rect x="{x:.1f}" y="264" width="{w:.1f}" height="10" fill="{colour}"/>')
    legend.append(f'<circle cx="{30 + i * 165}" cy="298" r="5" fill="{colour}"/><text x="{42 + i * 165}" y="302" font-size="12" fill="#e6edf3">{name} <tspan fill="#ffb000">{100 * size / total:.0f}%</tspan></text>')
    x += w

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{MONO}">
<rect width="{W}" height="{H}" rx="12" fill="#0d0905" stroke="#ff8c00" stroke-opacity="0.45"/>
<circle cx="24" cy="22" r="6" fill="#ff5f57"/><circle cx="44" cy="22" r="6" fill="#febc2e"/><circle cx="64" cy="22" r="6" fill="#28c840"/>
<text x="{W / 2}" y="27" text-anchor="middle" font-size="12" fill="#ffb000" opacity="0.8">mission-stats — updated {date.today():%b %d, %Y}</text>
{''.join(cells)}
<text x="24" y="254" font-size="11" letter-spacing="1.5" fill="#ffb000" opacity="0.8">LANGUAGES ACROSS PUBLIC PROJECTS</text>
<clipPath id="bar"><rect x="24" y="264" width="812" height="10" rx="5"/></clipPath>
<g clip-path="url(#bar)">{''.join(bar)}</g>
{''.join(legend)}
</svg>'''
open(sys.argv[2], "w").write(svg)
