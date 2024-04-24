import time
import os
import requests
import threading, queue

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
            output_path += '/' + directory
            if not os.path.exists(output_path):
                os.makedirs(output_path)

def fetch_and_save_page(home_page, url, output_path):
    response = requests.get(home_page + '/' + url)

    path = (url).split('//')[-1]
    create_directories(path.split('/'), output_path)

    if url.endswith('/') or not url:
        url += 'index.html'

    open(output_path + '/' + url, 'wb').write(response.content)
    return response.text

def fetch_resource(home_page, url, resource, output_path, html_tag):
    if html_tag in resource.attrs and not resource[html_tag].startswith('http'):
        resource_link = resource[html_tag]
        link = home_page + '/' + url + resource_link
        response = requests.get(link)
       
        path = (url + '/' + resource_link).split('//')[-1]
        create_directories(path.split('/'), output_path)

        open(output_path + '/' + url + resource_link, 'wb').write(response.content)

# This function is called by each thread to fetch and save a single resource
def scrape(home_page, url, pages, resources, output_path):
    response = fetch_and_save_page(home_page, url, output_path)

    (current_pages, current_images, current_scripts, current_styles) = parse_html(response)
    for page in current_pages:
        if page not in pages:
            pages[page['href']] = False

    for image in current_images:
        if image not in resources:
            fetch_resource(home_page, url, image, output_path, 'src')      
            resources.add(image)

    for script in current_scripts:
        if script not in resources:
            fetch_resource(home_page, url, script, output_path, 'src')
            resources.add(script)

    for style in current_styles:
        if style not in resources:
            fetch_resource(home_page, url, style, output_path, 'href')
            resources.add(style)

def scrape_website(url, output_path):
    print(f'{25*'-'} WEB SCRAPER {25*'-'}')
    print(f'Scraping {url} and saving the output to {output_path}')

    # Create a dictionary to store pages, and whether they have already been visited
    pages = {'' : False} # Add front page
    remainingPages = ['']
    resources = set()
    threads = []
    home_page = url

    #For multithreading
    #queue = queue.Queue(30) 

    # Iterate over the resources and start a new thread for each resource, possibly using a queue for scalability
    #TODO(Aston): Add traversal through whole website (while remainingResources: )
   # while remainingPages:
   # nbr_threads = min(30, len(remainingPages))
    while remainingPages:
        nbr_threads = min(10, len(remainingPages))
        for page in remainingPages[:nbr_threads]:
            pages[page] = True
            thread = threading.Thread(target=scrape, args=(home_page, page, pages, resources, output_path))
            thread.start()
            threads.append(thread)
        time.sleep(5)
        remainingPages = [page for page, is_visited in pages.items() if not is_visited]

    for thread in tqdm(threads, desc='Fetching resources', unit='resource'):
        thread.join()