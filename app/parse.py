import csv
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def get_single_quote(quote):
    tags_list = [tag.text.strip() for tag in quote.select(".tags a.tag")]
    return Quote(
        text=quote.select_one(".text").text.strip(),
        author=quote.select_one(".author").text.strip(),
        tags=tags_list,
    )


def get_quotes_from_page(page_soup):
    quotes = page_soup.select(".quote")
    return [get_single_quote(quote) for quote in quotes]


def has_next_page(page_soup):
    next_button = page_soup.select_one(".pager .next")
    if next_button is not None:
        return next_button
    return None


def get_all_quotes():

    all_quotes = []
    start_page = 1

    while True:
        if start_page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{start_page}/"

        response = requests.get(url)
        page_soup = BeautifulSoup(response.content, "html.parser")

        page_quotes = get_quotes_from_page(page_soup)
        all_quotes.extend(page_quotes)

        if not has_next_page(page_soup):
            break

        start_page += 1

    return all_quotes


def get_file():
    parse_quotes = get_all_quotes()

    with open("quotes.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])

        for quote in parse_quotes:
            writer.writerow([quote.text, quote.author, ", ".join(quote.tags)])


def main(output_csv_path: str) -> None:
    get_file()


if __name__ == "__main__":
    main("quotes.csv")
