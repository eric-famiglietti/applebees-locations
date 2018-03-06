from bs4 import BeautifulSoup, SoupStrainer
import json
import requests


URL = 'https://restaurants.applebees.com/'


def parse_home_page(url):
    page = requests.get(url)
    strainer = SoupStrainer('a', class_='thelinks normal')
    soup = BeautifulSoup(page.content, 'html.parser', parse_only=strainer)
    locations = []
    for link in soup.find_all('a'):
        locations += parse_state_page(link['href'])
    return locations


def parse_state_page(url):
    page = requests.get(url)
    strainer = SoupStrainer('a', class_='thelinks normal')
    soup = BeautifulSoup(page.content, 'html.parser', parse_only=strainer)
    locations = []
    for link in soup.find_all('a'):
        locations += parse_city_page(link['href'])
    return locations


def parse_city_page(url):
    page = requests.get(url)
    strainer = SoupStrainer('ul', class_='itemlist')
    soup = BeautifulSoup(page.content, 'html.parser', parse_only=strainer)
    return [{
        'address': location.find('span', attrs={'itemprop': 'streetAddress'}).a.get_text(),
        'city': location.find('span', attrs={'itemprop': 'addressLocality'}).get_text(),
        'country': location.find('span', attrs={'itemprop': 'addressCountry'}).get_text(),
        'name': location.find('li', attrs={'itemprop': 'name'}).get_text(),
        'phone_number': location.find('span', attrs={'itemprop': 'telephone'}).get_text(),
        'state': location.find('span', attrs={'itemprop': 'addressRegion'}).get_text(),
        'url': location.contents[-2].a['href'],
        'zip_code': location.find('span', attrs={'itemprop': 'postalCode'}).get_text(),
    } for location in soup.find_all('ul')]


print(json.dumps(parse_home_page(URL)))
