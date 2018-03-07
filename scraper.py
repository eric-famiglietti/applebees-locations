from bs4 import BeautifulSoup, SoupStrainer
import json
import requests


URL = 'https://restaurants.applebees.com/'
OUTPUT = 'locations.json'


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
    strainer = SoupStrainer('span', itemprop='streetAddress')
    soup = BeautifulSoup(page.content, 'html.parser', parse_only=strainer)
    locations = []
    for link in soup.find_all('a'):
        locations.append(parse_restaurant_page(link['href']))
    return locations


def parse_restaurant_page(url):
    page = requests.get(url)
    strainer = SoupStrainer('script', type='application/ld+json')
    soup = BeautifulSoup(page.content, 'html.parser', parse_only=strainer)

    # Sanitize and parse JSON data stored in script tag.
    data = soup.find_all('script')[1].string
    data = data.replace('// if the location file does not have the hours separated into open/close for each day, remove the below section', '')
    data = json.loads(data)

    return {
        'address': data['address']['streetAddress'],
        'city': data['address']['addressLocality'],
        'country': data['address']['addressCountry'],
        'id': data['@id'],
        'latitude': data['geo']['latitude'],
        'longitude': data['geo']['longitude'],
        'name': data['branchOf']['name'],
        'phone_number': data['telephone'],
        'state': data['address']['addressRegion'],
        'zip_code': data['address']['postalCode'],
    }


with open(OUTPUT, 'w') as f:
    f.write(json.dumps(parse_home_page(URL)))
