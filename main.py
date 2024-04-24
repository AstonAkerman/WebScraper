import argparse

from webscraper import scrape_website

def main(args):
    scrape_website(args.url, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Scraper')
    parser.add_argument('-u', '--url', help='URL of the website to scrape')
    parser.add_argument('-o', '--output', help='Output path, where to store the scraped website')
    
    args = parser.parse_args()
    main(args)