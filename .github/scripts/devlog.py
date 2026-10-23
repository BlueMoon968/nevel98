#==============================================================================
# NEVEL-98 - Devlog Feed
# devlog.py
#
# reads the itch.io devlog RSS and writes devlog.json for the landing page.
# GitHub Pages is static and itch sends no CORS headers, so the page can't
# read the feed itself: a scheduled action does it and commits the result.
#
#   python .github/scripts/devlog.py <rss url> devlog.json
#==============================================================================
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

MAX_POSTS = 3


def clean(text, limit=180):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + "…"


def first_image(text):
    m = re.search(r'<img[^>]+src="([^"]+)"', text or "")
    return m.group(1) if m else None


def read(url):
    req = urllib.request.Request(url, headers={"User-Agent": "nevel98-devlog"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def parse(data):
    posts = []
    for item in ET.fromstring(data).iter("item"):
        desc = item.findtext("description") or ""
        date = item.findtext("pubDate")
        try:
            date = parsedate_to_datetime(date).strftime("%Y-%m-%d")
        except (TypeError, ValueError):
            date = None
        posts.append({
            "title": (item.findtext("title") or "").strip(),
            "link": (item.findtext("link") or "").strip(),
            "date": date,
            "summary": clean(desc),
            "image": first_image(desc),
        })
    posts.sort(key=lambda p: p["date"] or "", reverse=True)
    return posts[:MAX_POSTS]


if __name__ == "__main__":
    url, out = sys.argv[1], sys.argv[2]
    try:
        posts = parse(read(url))
    except Exception as e:  # no devlog yet (404), itch down...: keep what we have
        print("devlog: feed not read:", e)
        sys.exit(0)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=1)
    print(f"devlog: {len(posts)} posts")
