import requests
import threading

from bs4 import BeautifulSoup
from tqdm import tqdm

def fetch_resource(url):
    response = requests.get(url)
    print(f'Fetched {url}')
    print(response.content)
    return response
    #TODO(Aston): Process the fetched resource here

def scrape_website(url, output_path):
    print(f'{25*'-'} WEB SCRAPER {25*'-'}')
    print(f'Scraping {url} and saving the output to {output_path}')
    
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    # Create a dictionary to store resources, and whether they have been fetched
    resources = {}

    # Iterate over the resources and start a new thread for each resource, possibly using a queue for scalability
    for link in links:
        resource_url = link.get('href')
        if resource_url:
            thread = threading.Thread(target=fetch_resource, args=(url + resource_url,))
            thread.start()
            resources.append(thread)

    for resource in tqdm(resources, desc='Fetching resources', unit='resource'):
        resource.join()