import requests, json, os, sys
from urllib.parse import urljoin, urldefrag
from bs4 import BeautifulSoup

URL = "https://egy.voxcinemas.com/movies/whatson"
TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
FILE = "seen.json"
SKIP = {"whatson", "comingsoon"}

html = requests.get(URL, timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")


def get_name(a):
    h = a.find_parent("h3")
    if h:
        return h.get_text(strip=True)
    for p in a.parents:
        hs = p.find_all("h3")
        if len(hs) == 1:
            return hs[0].get_text(strip=True)
        if len(hs) > 1:
            break
    return None


movies = {}
for a in soup.select('a[href*="/movies/"]'):
    href = urldefrag(urljoin(URL, a["href"]))[0].rstrip("/")
    slug = href.split("/movies/")[-1]
    if not slug or "/" in slug or "?" in slug or slug in SKIP:
        continue
    name = get_name(a)
    if name or href not in movies:
        movies[href] = name or slug.replace("-", " ").title()

print("لقيت", len(movies), "فيلم")

if not movies:
    print("مفيش أفلام اتقرأت")
    sys.exit()

seen = set(json.load(open(FILE))) if os.path.exists(FILE) else None

if seen is not None:
    for href in movies.keys() - seen:
        requests.get(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": f"فيلم جديد نزل:\n{movies[href]}\n{href}",
            },
        )

json.dump(sorted((seen or set()) | set(movies)), open(FILE, "w"), ensure_ascii=False)
