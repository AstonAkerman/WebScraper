import multiprocessing
import threading
import time
import requests

from bs4 import BeautifulSoup
from multiprocessing import Manager, Pool
from tqdm import tqdm

from file_helper import calculate_backsteps, create_directories, save_resource

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    images = soup.find_all('img')
    scripts = soup.find_all('script')
    styles = soup.find_all('link')

    return (links, images, scripts, styles)

def add_resource(resources, url, resource, resource_tag):
    if resource_tag in resource.attrs and not resource[resource_tag].startswith('http'):
            (current_url, current_image_path) = calculate_backsteps(url, resource[resource_tag])    
            if (current_url, current_image_path) not in resources:  
                resources.append((current_url, current_image_path))

# This function is called by each thread to fetch and save a single resource
def scrape(home_page, url, pages, resources):
    response = requests.get(home_page + '/' + url)
    pages[url] = response.content
    (current_pages, current_images, current_scripts, current_styles) = parse_html(response.text)

    for page in current_pages:
        (current_url, new_path) = calculate_backsteps(url, page['href']) 
        current_page = current_url + '/' + new_path 
        if current_page not in pages:
            pages[current_page] = False    

    for image in current_images:
        add_resource(resources, url, image, 'src')
    for script in current_scripts:
        add_resource(resources, url, script, 'src')
    for style in current_styles:
        add_resource(resources, url, style, 'href')

def scrape_website(home_page, output_path):
    print(f'{25*'-'} WEB SCRAPER {25*'-'}')
    print(f'Scraping {home_page} and saving the output to {output_path}')

    # Create a dictionary to store pages, and whether they have already been visited
    manager = Manager()
    pages = manager.dict()
    pages[''] = False # Add front page
    remaining_pages = manager.list()
    remaining_pages.append('') # Add front page
    resources = manager.list()
    threads = []
    home_page

    # Iterate over the resources and start a new thread for each resource
    nbr_max_threads = multiprocessing.cpu_count()
    print('Number of CPU cores: ', nbr_max_threads)
    pool = Pool(nbr_max_threads)

    while remaining_pages:
        for url in remaining_pages:
            if not pages[url]:
                pool.apply_async(scrape, args=(home_page, url, pages, resources))
                pages[url] = True

        time.sleep(2)
        remaining_pages = [page for page, is_visited in pages.items() if not is_visited]

        print(f'\n{60*'-'}')
        print(f'| Pages in queue: ', len(remaining_pages))
        print(f'| Resources in queue: ', len(resources))
        print(f'| Pages visited, ', len(pages))
        print(f'{60*'-'}\n')

    for thread in tqdm(threads, desc='Fetching pages', unit='resource'):
        thread.join()

    for(page, html) in tqdm(pages.items(), desc='Creating page directories', unit='page'):
        if (len(page) > 200):
            # Python cannot create directories for very long paths.
            # see: https://stackoverflow.com/a/61628356
            continue
        create_directories(page.split('/'), output_path)
        if page == '':
            page = 'index.html'
        open(output_path + '/' + page, 'wb').write(html)

    for (url, resource_path) in tqdm(resources, desc='Fetching resources', unit='resource'):
        save_resource(home_page, url, resource_path, output_path)
