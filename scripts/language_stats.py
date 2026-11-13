import os
import json
import urllib.request
from collections import Counter

token = os.environ["LANGUAGES_TOKEN"]
headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "User-Agent": "profile-language-stats"}
def get(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        return json.load(response)

totals = Counter()
page = 1
while True:
    repos = get(f"https://api.github.com/user/repos?affiliation=owner&per_page=100&page={page}")
    if not repos:
        break
    for repo in repos:
        if repo["owner"]["login"].lower() != "victor-llantoy" or repo["fork"]:
            continue
        totals.update(get(repo["languages_url"]))
    page += 1

if not totals:
    raise SystemExit("No se encontraron datos de lenguajes; no se modifica el README.")
total = sum(totals.values())
rows = ["| Lenguaje | Código | Proporción |", "| :--- | ---: | :--- |"]
for name, size in totals.most_common():
    percent = size / total * 100
    bars = round(percent / 5)
    name = name.replace("|", "&#124;").replace("\n", " ")
    rows.append(f"| {name} | {percent:.1f} % | {'🟩' * bars}{'⬜' * (20-bars)} |")

path = "README.md"
with open(path, encoding="utf-8") as f:
    readme = f.read()
start, end = "<!-- LANGUAGES:START -->", "<!-- LANGUAGES:END -->"
if start not in readme or end not in readme:
    raise SystemExit("No se encontraron los marcadores en README.md")
before, rest = readme.split(start, 1)
_, after = rest.split(end, 1)
with open(path, "w", encoding="utf-8") as f:
    f.write(before + start + "\n\n" + "\n".join(rows) + "\n\n" + end + after)
