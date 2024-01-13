import os

import requests
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


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


for book_id in range(1, 11):
    text_url = f'https://tululu.org/txt.php?id={book_id}'
    book_page_url = f'https://tululu.org/b{book_id}/'
    text_response = requests.get(text_url)
    text_response.raise_for_status()
    book_response = requests.get(book_page_url)
    book_response.raise_for_status()
    try:
        check_for_redirect(text_response)
        soup = BeautifulSoup(book_response.text, 'lxml')
        page_title = soup.find('body').find('table').find(
            'td', class_='ow_px_td').find('div').find('h1')
        page_title_text = page_title.text
        page_title_splited_text = page_title_text.split('::')
        book_title = page_title_splited_text[0]
        author = page_title_splited_text[1]
        download_txt(text_url, book_title)
    except requests.HTTPError:
        print(f"HTTPError: {text_response.history}")
