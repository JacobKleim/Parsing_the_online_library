import argparse
import os
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if any(res.status_code == 302 for res in response.history):
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    path = Path(folder)
    path.mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()

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


def parse_book_page(soup):
    book_page = {}
    page_title = soup.find('body').find('table').find(
        'td', class_='ow_px_td').find('div').find('h1')
    page_title_text = page_title.text
    page_title_splited_text = page_title_text.split('::')
    book_title = page_title_splited_text[0].strip()
    author = page_title_splited_text[1].strip()
    page_comments = soup.find('body').find('table').find(
        'td', class_='ow_px_td').find_all('div', class_='texts')
    comments_text = '; '.join(
        [comment.get_text().split(')', 1)[1].strip()
            for comment in page_comments])
    image_path = soup.find('body').find('table').find(
        'div', class_='bookimage').find('img')['src']
    image_url = urljoin('https://tululu.org/', image_path)

    book_genres = soup.find('body').find('table').find(
        'span', class_='d_book').find_all('a')
    genre = ([genre.get_text() for genre in book_genres])
    book_page = {'author': author,
                 'book_title': book_title,
                 'comments_text': comments_text,
                 'image_url': image_url,
                 'genre': genre
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

    for book_id in range(args.start_id, args.end_id + 1):
        text_url = f'https://tululu.org/txt.php?id={book_id}'
        book_page_url = f'https://tululu.org/b{book_id}/'
        text_response = requests.get(text_url)
        text_response.raise_for_status()
        book_response = requests.get(book_page_url)
        book_response.raise_for_status()
        try:
            check_for_redirect(text_response)
            soup = BeautifulSoup(book_response.text, 'lxml')
            parsed_book = parse_book_page(soup)
            download_image(parsed_book['image_url'])
            download_txt(text_url, parsed_book['book_title'])
        except requests.HTTPError:
            print(f'HTTPError: {text_response.history}')


if __name__ == '__main__':
    main()
