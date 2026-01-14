import logging
from utils import fetch, gen_uuid, now_utc, save_to_db, clean_text

def parse_e1_list(page: int):
    logging.info(f"E1 | page {page}")

    url = f"https://www.e1.ru/text/page-{page}/"
    soup = fetch(url)

    for a in soup.select("a[href*='/text/']"):
        href = a.get("href")
        if not href:
            continue

        if not href.startswith("http"):
            href = "https://www.e1.ru" + href

        parse_e1_article(href)


def parse_e1_article(url: str):
    logging.info(f"E1 | article {url}")
    soup = fetch(url)

    title = soup.find("h1")
    body = soup.select("article p")
    time_tag = soup.find("time")

    if not title or not body:
        logging.warning(f"E1 | skip {url}")
        return

    item = {
        "guid": gen_uuid(),
        "title": title.get_text(strip=True),
        "description": "\n".join(p.get_text(" ", strip=True) for p in body),
        "url": url,
        "published_at": time_tag.get("datetime") if time_tag else None,
        "comments_count": None,
        "rating": None,
        "created_at_utc": now_utc()
    }

    save_to_db(item)
    logging.info(f"E1 | saved {url}")

