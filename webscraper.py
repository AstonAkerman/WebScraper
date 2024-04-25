import time
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
            output_path += '/' + directory
            if not os.path.exists(output_path):
                os.makedirs(output_path)

def fetch_page(home_page, url, output_path):
    response = requests.get(home_page + '/' + url)

    path = (url).split('//')[-1]

    if url.endswith('/') or not url:
        url += 'index.html'

    return response

def add_resource(resources, url, resource, resource_tag):
    if resource_tag in resource.attrs and not resource[resource_tag].startswith('http'):
            (current_url, current_image_path) = calculate_backsteps(url, resource[resource_tag])    
            if (current_url, current_image_path) not in resources:  
                resources.add((current_url, current_image_path))

def save_resource(home_page, url, resource_path, output_path):

    link = home_page + '/' + url + resource_path
    response = requests.get(link)
    
    path = (url + '/' + resource_path).split('//')[-1]
    create_directories(path.split('/'), output_path)

    open(output_path + '/' + url + resource_path, 'wb').write(response.content)

def calculate_backsteps(url, resource_path):
    back_steps = resource_path.count('../')
    resource_path = resource_path.replace('../', '')

    if not url.endswith('/'):
        back_steps += 1

    url = ('/').join(url.split('/')[:-back_steps])
    return (url, resource_path)

# This function is called by each thread to fetch and save a single resource
def scrape(home_page, url, pages, resources, output_path):
    response = fetch_page(home_page, url, output_path)
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

def scrape_website(url, output_path):
    print(f'{25*'-'} WEB SCRAPER {25*'-'}')
    print(f'Scraping {url} and saving the output to {output_path}')

    # Create a dictionary to store pages, and whether they have already been visited
    pages = {'' : False} # Add front page
    remaining_pages = [''] # Add front page
    resources = set()
    threads = []
    home_page = url

    # Iterate over the resources and start a new thread for each resource, possibly using a queue for scalability
    nbr_max_threads = 30
    while remaining_pages:
        nbr_active_threads = threading.active_count() - 1
        if (threading.active_count() - 1) < nbr_max_threads:
            nbr_new_threads = nbr_max_threads - nbr_active_threads
            for page in remaining_pages[:nbr_new_threads]:
                if not pages[page]:
                    thread = threading.Thread(target=scrape, args=(home_page, page, pages, resources, output_path))
                    thread.start()
                    threads.append(thread)
        else:
            time.sleep(2)
        remaining_pages = [page for page, is_visited in pages.items() if not is_visited]

        print(f'\n{60*'-'}')
        print(f'| Pages in queue: ', len(remaining_pages))
        print(f'| Threads running: ', threading.active_count() - 1)
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
