import json
import logging
from utils import fetch, gen_uuid, now_utc, save_to_db, clean_text, parse_banki_date
from datetime import datetime
import re

BANKI_STOP_PHRASES = [
    "подписываясь, вы даете согласие",
    "согласие на обработку персональных данных",
    "получение рекламы",
    "откройте первый вклад",
    "получите бонус",
    "посмотреть полный рейтинг",
]


def parse_banki_list(page: int):
    logging.info(f"BANKI | page {page}")

    url = f"https://www.banki.ru/news/lenta/?page={page}"
    soup = fetch(url)

    for a in soup.select("a[href]"):
        href = a.get("href")

        if not href:
            continue

        # ТОЛЬКО реальные статьи Banki
        if not href.startswith("/news/lenta/?id="):
            continue

        full_url = "https://www.banki.ru" + href
        parse_banki_article(full_url)

def clean_banki_body(paragraphs: list[str]) -> str:
    result = []

    for text in paragraphs:
        t = text.lower()

        # если встретили стоп-фразу — дальше статья закончилась
        if any(stop in t for stop in BANKI_STOP_PHRASES):
            break

        result.append(text)

    return "\n".join(result).strip()


def parse_comments_count(text: str) -> int | None:
    """
    '1 комментарий', '12 комментариев'
    """
    if not text:
        return None

    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None


def parse_banki_article(url: str):
    logging.info(f"BANKI | article {url}")

    soup = fetch(url)

    title = soup.find("h1")
    body_nodes = soup.select("main p")

    # --- ДАТА ---
    published_at = None
    date_div = soup.find("div", string=re.compile(r"\d{4}\s*г\."))
    if date_div:
        published_at = parse_banki_date(date_div.get_text(strip=True))

    # --- КОММЕНТАРИИ ---
    comments_count = None
    comments_div = soup.find("div", string=re.compile(r"коммент"))
    if comments_div:
        comments_count = parse_comments_count(comments_div.get_text(strip=True))

    if not title or not body_nodes:
        logging.warning(f"BANKI | skip {url}")
        return

    paragraphs = [
        clean_text(p.get_text(" ", strip=True))
        for p in body_nodes
        if clean_text(p.get_text(" ", strip=True))
    ]

    description = clean_banki_body(paragraphs)

    item = {
        "guid": gen_uuid(),
        "title": clean_text(title.get_text(strip=True)),
        "description": description,
        "url": url,
        "published_at": published_at,
        "comments_count": comments_count,
        "rating": None,
        "created_at_utc": now_utc()
    }

    save_to_db(item)

    logging.info(
        f"BANKI | saved {url} | published_at={published_at} | comments={comments_count}"
    )