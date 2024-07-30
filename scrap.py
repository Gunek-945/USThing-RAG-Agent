import requests
from bs4 import BeautifulSoup

# The target URL
urls = ['https://seng.hkust.edu.hk/academics/undergraduate/faq-info-for-jupas-students']

for url in urls:

    with open('dataset.txt', 'a', encoding='utf-8') as f:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, features="html.parser")
        f.write(f"URL: {url}\n\n")
        field_items = soup.find_all('div', class_='field__item')
        for p in field_items:
            f.write(p.get_text().strip())