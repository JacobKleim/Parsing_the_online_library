import requests


url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
response = requests.get(url)
response.raise_for_status()
# print(response.text)

from bs4 import BeautifulSoup


soup = BeautifulSoup(response.text, 'lxml')
title_tag = soup.find('main').find('header').find('h1')
title_text = title_tag.text
image = soup.find('img', class_='attachment-post-image')['src']
text = soup.find('main').find('div', class_='entry-content')
print(image)
print(title_text)
print(text.text)