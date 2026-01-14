# stopgame.py

from utils import fetch, gen_uuid, now_utc, save_to_db
import re

def parse_stopgame_list(page: int):
    url = f"https://stopgame.ru/news/all/p{page}"
    soup = fetch(url)

    links = set()

    for a in soup.select("a[href*='/newsdata/']"):
        href = a.get("href")
        if not href:
            continue

        href = href.split("#")[0]  # ← УБРАЛИ #comments
        links.add("https://stopgame.ru" + href)

    for link in links:
        parse_stopgame_article(link)



def parse_stopgame_article(url: str):
    soup = fetch(url)

    title = soup.find("h1")
    body = soup.select("article p")

    published_meta = soup.find("meta", {"property": "og:article:published_time"})
    rating_tag = soup.select_one(".rating-value")

    # --- КОММЕНТАРИИ ---
    comments_count = None
    comments_a = soup.find("a", href="#comments")
    if comments_a:
        m = re.search(r"\d+", comments_a.get_text(strip=True))
        comments_count = int(m.group()) if m else 0

    if not title or not body:
        return

    item = {
        "guid": gen_uuid(),
        "title": title.text.strip(),
        "description": "\n".join(p.text.strip() for p in body),
        "url": url,
        "published_at": published_meta["content"] if published_meta else None,
        "comments_count": comments_count,
        "rating": int(rating_tag.text) if rating_tag else None,
        "created_at_utc": now_utc()
    }

    save_to_db(item)