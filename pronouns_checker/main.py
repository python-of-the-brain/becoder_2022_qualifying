import argparse
import re
from collections import Counter
from dataclasses import dataclass
from typing import Tuple

from bs4 import BeautifulSoup
from bs4.element import Comment
import requests


@dataclass(frozen=True)
class Pronouns:
    first: list[str]
    other: list[str]


PRONOUNS = {
    "ru": Pronouns(
        first=[  # список личных местоимений первого лица
            "я",
            "меня",
            "мне",
            "меня",
            "мной",
            "мною",
            "мне",
            "мы",
            "нас",
            "нам",
            "нами",
            "нами",
        ],
        other=[  # список остальных личных местоимений
            "ты",
            "тебя",
            "тебе",
            "тобой",
            "вы",
            "вас",
            "вам",
            "вами",
            "он",
            "оно",
            "его",
            "ему",
            "им",
            "нем",
            "нём",
            "она",
            "ее",
            "её",
            "ей",
            "ею",
            "ней",
            "они",
            "их",
            "им",
            "ими",
            "них",
        ],
    ),
    "en": Pronouns(first=[], other=[]),
}

reg = re.compile(r"[^A-Za-zА-Яа-я]")

EN, RU = "en", "ru"


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Calculate pronouns by url")
    parser.add_argument(
        "--url",
        metavar="url",
        type=str,
        help="Url of page for scrapping",
    )
    parser.add_argument(
        "--lang",
        metavar="lang",
        type=str,
        nargs="?",
        default=None,
        help="Lang of site. Default - set from site by tag",
    )
    parser.add_argument(
        "--with-stat",
        action="store_true",
        help="Print full stat by pronouns",
    )
    return parser


def tag_visible(element) -> bool:
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def parse_html(body) -> Tuple[str, str]:
    soup = BeautifulSoup(body, "html.parser")
    lang: str = soup.html.get("lang", EN)
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return (" ".join(t.strip() for t in visible_texts), lang)


def clean_text(text) -> list[str]:
    words = filter(
        lambda w: bool(w), map(lambda w: reg.sub("", w.lower()), text.split())
    )
    return list(words)


def get_pronouns(arg_lang: str, lang: str) -> Pronouns:
    if arg_lang not in [RU, EN, None]:
        raise Exception("Lang is not recognized")
    return PRONOUNS[arg_lang or lang]


def print_counter(c: Counter):
    print("Местоимение | Кол-во")
    print("-" * 20)
    for word, count in sorted(c.items(), key=lambda x: x[1], reverse=True):
        print(f"{word:<11} | {count}")
    print()


def print_result(first: Counter, other: Counter, with_stat: bool):
    f, o = first.total(), other.total()
    print("Всего местоимений 1-го лица на странице:", f)
    print("Всего других местоимений на странице:\t", o)

    if with_stat:
        print("\nСтатистика местоимений 1-го лица:")
        print_counter(first)
        print("Статистика остальных местоимений:")
        print_counter(other)

    print(
        f"Местоимений 1-го лица "
        f"{'БОЛЬШЕ' if f > o else 'МЕНЬШЕ'} остальных личных местоимений на странице"
    )


def calculate(pronouns: Pronouns, words: list[str]) -> tuple[Counter, Counter]:
    first_counter = Counter(filter(lambda w: w in pronouns.first, words))
    other_counter = Counter(filter(lambda w: w in pronouns.other, words))
    return first_counter, other_counter


def main():
    parser = get_parser()
    args = parser.parse_args()
    try:
        response = requests.get(args.url, allow_redirects=True)
        if not response.ok:
            raise Exception
    except Exception:
        print(f"Can't get page from url: {args.url}")
        return
    text, lang = parse_html(response.text)
    words = clean_text(text)
    pronouns = get_pronouns(arg_lang=args.lang, lang=lang)
    first, other = calculate(pronouns=pronouns, words=words)

    print_result(
        first=first,
        other=other,
        with_stat=args.with_stat,
    )


if __name__ == "__main__":
    main()
