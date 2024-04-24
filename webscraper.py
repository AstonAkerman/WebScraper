import os
import requests
import threading

from bs4 import BeautifulSoup
from tqdm import tqdm

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    images = soup.find_all('img')
    return (links, images)

def create_directories(directories, output_path):
    for directory in directories[:-1]:
        if directory:
            output_path += directory + '/'
            if not os.path.exists(output_path):
                os.makedirs(output_path)

def fetch_and_save_resource(url, output_path):
    response = requests.get(url)

    domain = url.split('//')[-1]
    directories = domain.split('/')

    create_directories(directories, output_path)

    open(output_path + '/' + domain + 'index.html', 'wb').write(response.content)
    return response.text

# This function is called by each thread to fetch and save a single resource
def scrape(url, resources, images, output_path):
    if not resources[url]:
        resources[url] = False
    if resources[url] == False:
        response = fetch_and_save_resource(url, output_path)
        (new_resources, new_images) = parse_html(response)

        for new_resource in new_resources:
            if new_resource not in resources:
                print(f'Found new resource {new_resource}')
                resources[new_resource] = False

        for new_image in new_images:
            if new_image not in images:
                print(f'Found new image {new_image}')
                #TODO(Aston): Save the image to a file
                images.add(new_image)
        resources[url] = True

def scrape_website(url, output_path):
    print(f'{25*'-'} WEB SCRAPER {25*'-'}')
    print(f'Scraping {url} and saving the output to {output_path}')

    # Create a dictionary to store resources, and whether they have already been visited
    resources = {url : False} # Add front page
    remainingResources = [url]
    images = set()
    threads = []

    # Iterate over the resources and start a new thread for each resource, possibly using a queue for scalability
    #TODO(Aston): Add traversal through whole website (while remainingResources: )
    for resource in remainingResources:
        print(f'Fetching resource {resource}')
        thread = threading.Thread(target=scrape, args=(resource, resources, images, output_path))
        thread.start()
        threads.append(thread)
    remainingResources = [resource for resource, isVisited in resources.items() if not isVisited]

    for thread in tqdm(threads, desc='Fetching resources', unit='resource'):
        thread.join()