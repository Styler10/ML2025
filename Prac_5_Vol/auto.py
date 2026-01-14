from urllib.parse import urljoin
from utils import fetch, gen_uuid, now_utc, save_to_db
import logging

def parse_autoru_list(page: int):
    url = f"https://auto.ru/mag/theme/news/?page={page}"
    soup = fetch(url)

    links = set()

    for a in soup.select("a[href^='/mag/article/'], a[href^='https://auto.ru/mag/article/']"):
        href = a.get("href")
        if not href:
            continue

        full_url = urljoin("https://auto.ru", href)
        links.add(full_url)

    for link in links:
        parse_autoru_article(link)


def parse_autoru_article(url: str):
    soup = fetch(url)
    
    title_elem = soup.find("h1")
    title = title_elem.get_text(strip=True) if title_elem else None
    
    article_content = None
    article_body_div = soup.select_one("div[itemprop='articleBody']")
    
    if article_body_div:
        for elem in article_body_div.select("script, style, .ad, .banner, .social, .survey, .PollBlock, .NewsCarousel, .SmallPostPreview, .PostBlock, .Tags, vertisads"):
            elem.decompose()
        
        article_content = article_body_div.get_text(separator="\n", strip=True)
    
    if not title or not article_content:
        logging.warning(f"AUTO | skip {url}")
        return
    
    published_at = None
    date_selectors = [
        "time[datetime]",
        "meta[property='article:published_time']",
        "meta[property='og:published_time']",
        "meta[name='article:published_time']"
    ]
    
    for selector in date_selectors:
        elem = soup.select_one(selector)
        if elem:
            if selector.startswith("meta"):
                published_at = elem.get("content")
            else:
                published_at = elem.get("datetime") or elem.get_text(strip=True)
            break

    item = {
        "guid": gen_uuid(),
        "title": title,
        "description": article_content,
        "url": url,
        "published_at": published_at,
        "comments_count": None,
        "rating": None,
        "created_at_utc": now_utc()
    }

    logging.info(f"AUTO | save {url}")
    save_to_db(item)