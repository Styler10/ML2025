# main.py
import logging
from banki import parse_banki_list
from e1 import parse_e1_list
from auto import parse_autoru_list
from stopgame import parse_stopgame_list
from db import init_db

def main():
    logging.info("START PARSER")
    init_db()

    SOURCES = [
        ("BANKI", parse_banki_list, 150),
        
    ]

    for name, func, pages in SOURCES:
        logging.info(f"SOURCE START {name}")
        for page in range(80, pages + 1):
            func(page)

    logging.info("FINISH PARSER")


if __name__ == "__main__":
    main()
