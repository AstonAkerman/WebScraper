import os
import requests
import threading

from bs4 import BeautifulSoup
from tqdm import tqdm

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    images = soup.find_all('img')
    scripts = soup.find_all('script')
    styles = soup.find_all('link')

    return (links, images, scripts, styles)

def create_directories(directories, output_path):
    for directory in directories[:-1]:
        if directory:
            output_path += directory + '/'
            if not os.path.exists(output_path):
                os.makedirs(output_path)

def fetch_and_save_page(url, output_path):
    response = requests.get(url)

    domain = url.split('//')[-1]
    directories = domain.split('/')

    create_directories(directories, output_path)

    open(output_path + '/' + domain + 'index.html', 'wb').write(response.content)
    return response.text

# This function is called by each thread to fetch and save a single resource
def scrape(url, pages, resources, output_path):
    if not pages[url]:
        pages[url] = False
    if pages[url] == False:
        response = fetch_and_save_page(url, output_path)
        (current_pages, current_images, current_scripts, current_styles) = parse_html(response)

        for resource in current_pages:
            if resource not in pages:
                print(f'Found new resource {resource}')
                pages[resource] = False

        for image in current_images:
            if image not in resources:
                print(f'Found new image {image}')
                #TODO(Aston): Save the image to a file
                resources.add(image)

        for script in current_scripts:
            if script not in resources:
                print(f'Found new script {script}')
                #TODO(Aston): Download the script resource
                resources.add(script)

        for style in current_styles:
            if style not in resources:
                print(f'Found new style {style}')
                #TODO(Aston): Download the style resource
                resources.add(style)

        # The page has been visited
        pages[url] = True

def scrape_website(url, output_path):
    print(f'{25*'-'} WEB SCRAPER {25*'-'}')
    print(f'Scraping {url} and saving the output to {output_path}')

    # Create a dictionary to store resources, and whether they have already been visited
    pages = {url : False} # Add front page
    remainingPages = [url]
    resources = set()
    threads = []

    # Iterate over the resources and start a new thread for each resource, possibly using a queue for scalability
    #TODO(Aston): Add traversal through whole website (while remainingResources: )
    for page in remainingPages:
        print(f'Fetching resource {page}')
        thread = threading.Thread(target=scrape, args=(page, pages, resources, output_path))
        thread.start()
        threads.append(thread)
    remainingPages = [page for page, is_visited in pages.items() if not is_visited]

    for thread in tqdm(threads, desc='Fetching resources', unit='resource'):
        thread.join()