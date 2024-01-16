import argparse
import os
import time
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
import logging


logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def check_for_redirect(response):
    if response.history:
        print(f'HTTPError: {response.history}')
        raise requests.exceptions.HTTPError


def download_txt(url, filename, book_id, folder='books/'):
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)

    filepath = os.path.join(path, f'{sanitize_filename(filename)}.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(url, folder='images/'):
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    parsed_url = urlsplit(url)
    decoded_filename = unquote(parsed_url.path.split('/')[-1])
    filepath = os.path.join(path, decoded_filename)

    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(soup, base_url):
    page_title = soup.find('td', class_='ow_px_td').find('h1')
    page_title_text = page_title.text
    page_title_splited_text = page_title_text.split('::')
    book_title, author = map(str.strip, page_title_splited_text[:2])

    page_comments = soup.find_all('div', class_='texts')
    comments_text = '; '.join(
        [comment.get_text().split(')', 1)[1].strip()
            for comment in page_comments])

    image_path = soup.find('div', class_='bookimage').find('img')['src']
    image_url = urljoin(base_url, image_path)

    book_genres = soup.find('span', class_='d_book').find_all('a')
    parsed_book_genres = ([genre.get_text() for genre in book_genres])

    book_page = {
        'author': author,
        'book_title': book_title,
        'comments_text': comments_text,
        'image_url': image_url,
        'genre': parsed_book_genres
    }

    return book_page


def main():
    parser = argparse.ArgumentParser(
        description='Download books from a range of IDs.')
    parser.add_argument('start_id',
                        type=int,
                        default=1,
                        help='Start book ID')
    parser.add_argument('end_id',
                        type=int,
                        default=10,
                        help='End book ID')
    args = parser.parse_args()

    first_retry = True

    for book_id in range(args.start_id, args.end_id + 1):
        text_url = 'https://tululu.org/txt.php'
        book_page_url = f'https://tululu.org/b{book_id}/'
        try:
            book_response = requests.get(book_page_url)
            book_response.raise_for_status()
            check_for_redirect(book_response)
            soup = BeautifulSoup(book_response.text, 'lxml')
            parsed_book = parse_book_page(soup, book_page_url)
            download_image(parsed_book['image_url'])
            download_txt(text_url, parsed_book['book_title'], book_id)
        except requests.exceptions.HTTPError as http_error:
            logging.error(f'HTTPError: {http_error}')
            continue
        except requests.exceptions.ConnectionError as connection_error:
            print(connection_error)
            if first_retry:
                time.sleep(3)
            first_retry = False
            time.sleep(10)
            continue


if __name__ == '__main__':
    main()
