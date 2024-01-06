import os

import requests
from pathlib import Path

path = Path('books')
path.mkdir(parents=True, exist_ok=True)

for book_id in range(32168, 32178):
    url = f"https://tululu.org/txt.php?id={book_id}"
    response = requests.get(url)
    response.raise_for_status() 

    filepath = os.path.join(path, f'{book_id}.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)