import argparse
import os
import shutil

from webscraper import scrape_website

def main(args):
    output_directory = create_output_path(args.url, args.output)
    print('''
888       888          888       .d8888b.                                                     
888   o   888          888      d88P  Y88b                                                    
888  d8b  888          888      Y88b.                                                         
888 d888b 888  .d88b.  88888b.   "Y888b.    .d8888b 888d888 8888b.  88888b.   .d88b.  888d888 
888d88888b888 d8P  Y8b 888 "88b     "Y88b. d88P"    888P"      "88b 888 "88b d8P  Y8b 888P"   
88888P Y88888 88888888 888  888       "888 888      888    .d888888 888  888 88888888 888     
8888P   Y8888 Y8b.     888 d88P Y88b  d88P Y88b.    888    888  888 888 d88P Y8b.     888     
888P     Y888  "Y8888  88888P"   "Y8888P"   "Y8888P 888    "Y888888 88888P"   "Y8888  888     
                                                                    888                       
                                                                    888                       
                                                                    888                       
          ''')
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