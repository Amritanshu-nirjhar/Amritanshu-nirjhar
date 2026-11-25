"""Rewrites the RECENT block in README.md with the owner's most recently pushed public repos.
usage: python3 recent.py repos.json README.md   (repos.json = GET /users/{owner}/repos?sort=pushed)"""
import json, re, sys
from datetime import datetime

repos_file, readme = sys.argv[1], sys.argv[2]
repos = [r for r in json.load(open(repos_file)) if not r["fork"] and r["name"].lower() != r["owner"]["login"].lower()][:5]
rows = []
for r in repos:
    when = datetime.strptime(r["pushed_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%b\u00a0%d")
    desc = (r["description"] or "").strip(" .") or "new mission in progress"
    live = f' · [live ↗]({r["homepage"]})' if r["homepage"] else ""
    rows.append(f'| `{when}` | **[{r["name"]}]({r["html_url"]})** | {desc}{live} |')
table = "| pushed | project | what it is |\n|:--|:--|:--|\n" + "\n".join(rows)
text = open(readme).read()
new = re.sub(r"(<!--RECENT:START-->).*?(<!--RECENT:END-->)", lambda m: f"{m[1]}\n{table}\n{m[2]}", text, flags=re.S)
open(readme, "w").write(new)
