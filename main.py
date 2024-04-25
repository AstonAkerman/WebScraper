import argparse
import os
import shutil

from webscraper import scrape_website

def main(args):
    output_directory = create_output_path(args.url, args.output)
    scrape_website(args.url, output_directory)

def create_output_path(url, output_path):
    domain = url.split('//')[-1]
    output_directory = output_path + '/' + domain
    if os.path.exists(output_directory):
        input(f'The output path \'{output_directory}\' already exists. Press Enter to overwrite the directory and continue, or Ctrl+C to cancel')
        shutil.rmtree(output_directory)
    os.makedirs(output_directory)
    return output_directory

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Scraper')
    parser.add_argument('-u', '--url', help='URL of the website to scrape')
    parser.add_argument('-o', '--output', help='Output path, where to store the scraped website')
    
    args = parser.parse_args()
    main(args)