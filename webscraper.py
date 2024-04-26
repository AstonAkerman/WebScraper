import multiprocessing
import time
import requests

from bs4 import BeautifulSoup
from multiprocessing import Manager, Pool
from tqdm import tqdm

from file_helper import calculate_backsteps, create_directories, create_resource_directory

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    images = soup.find_all('img')
    scripts = soup.find_all('script')
    styles = soup.find_all('link')

    return (links, images, scripts, styles)

def do_request(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # If the request was successful, no Exception will be raised
    except requests.RequestException as err:
        print(f"Request failed: {err}")
        return None
    return response

def add_resource(resources, url, resource, resource_tag):
    if resource_tag in resource.attrs and not resource[resource_tag].startswith('http'):
            (current_url, current_image_path) = calculate_backsteps(url, resource[resource_tag])    
            if (current_url, current_image_path) not in resources:  
                resources.append((current_url, current_image_path))

def save_resource(home_page, url, resource_path, output_path):
    link = home_page + '/' + url + resource_path
    response = do_request(link)
    try:
        with open(output_path + '/' + url + resource_path, 'wb') as file:
            file.write(response.content)
    except IOError as err:
        print(f"Failed to save resource: {err}")
        return False
    return True

def save_page(output_path, page, html):
    if (len(page) > 200):
        # Python cannot create directories in Windows for very long paths.
        # see: https://stackoverflow.com/a/61628356
        return
    create_directories(page.split('/'), output_path)
    if page == '':
        page = 'index.html'
    open(output_path + '/' + page, 'wb').write(html)

# This function is called by each thread to fetch and save a single resource
def scrape(home_page, url, pages, resources):
    response = do_request(home_page + '/' + url)
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
    print(f'Scraping {home_page} and saving the output to {output_path}')

    # Create a dictionary to store pages, and whether they have already been visited
    manager = Manager()
    pages = manager.dict()
    pages[''] = False # Add front page
    remaining_pages = manager.list()
    remaining_pages.append('') # Add front page
    resources = manager.list()
    results = []
    home_page

    # Iterate over the resources and start a new thread for each resource
    nbr_max_threads = multiprocessing.cpu_count()
    print('Number of CPU cores: ', nbr_max_threads)
    pool = Pool(nbr_max_threads)

    # Explore the website and find all resources
    while remaining_pages:
        for url in remaining_pages:
            if not pages[url]:
                pages[url] = True
                result = pool.apply_async(scrape, args=(home_page, url, pages, resources))
                results.append(result)

        remaining_pages = [page for page, is_visited in pages.items() if not is_visited]
        
        print(f'\n{60*'-'}')
        print(f'| Resources found: ', len(resources))
        print(f'| Pages visited: ', len(pages))
        print(f'{60*'-'}\n')
        # If there are no current remaining pages to visit, make sure that current threads do not find new pages
        if len(remaining_pages) == 0:
            [results.wait() for results in results]
            remaining_pages = [page for page, is_visited in pages.items() if not is_visited]

    pool.close()
    # block until all tasks are complete and threads close
    pool.join()

    # Create all directories for the web pages, and save the pages
    for(page, html) in tqdm(pages.items(), desc='Creating page directories', unit='page'):
        save_page(output_path, page, html)

    for (url, resource_path) in tqdm(resources, desc='Creating resource directories', unit='resource'):
        create_resource_directory(url, resource_path, output_path)

    # Fetch and save all resources (images, script resources, styles)
    pool = Pool(nbr_max_threads)
    results = []
    for (url, resource_path) in resources:
        results.append(pool.apply_async(save_resource, args=(home_page, url, resource_path, output_path)))

    for (result) in tqdm(results, desc='Saving resources', unit='resource'):
        result.get()

    pool.close()
    # block until all tasks are complete and threads close
    pool.join()

    print(f'Finished scraping \'{home_page}\'!')