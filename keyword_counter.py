import requests
from collections import Counter
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import csv
import re
from time import sleep
from tqdm import tqdm

headers = {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	'accept-encoding':'gzip, deflate, br, zstd',
	'accept-language':'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
	'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
	'connection':'keep-alive'
}

def count_keyword_occurrences(url, keywords):
    try:
        # Fetch the content of the URL using requests_html to render JavaScript
        session = HTMLSession()
        response = session.get(url, headers=headers, timeout=10)
        sleep(1) #Avoid rate-limit
        response.html.render(timeout=60, sleep=10)  # Render JavaScript content if necessary
        content = response.html.html

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script and style elements to avoid hidden text issues
        for script in soup(["script", "style"]):
            script.extract()

        # Extract text content
        text = soup.get_text()
        text = text.lower()  # Convert to lowercase for case-insensitive matching

        # Improved regex to retain words with special characters like hyphens, parentheses, and periods
        #words = re.findall(r'\b[\w()\-\.]+\b', text)

        # Count the occurrences of each keyword using regex
        keyword_counts = Counter()
        for keyword in keywords:
            escaped_keyword = re.escape(keyword.lower())  # Escape special characters
            keyword_counts[keyword] = len(re.findall(r'\b' + escaped_keyword + r'\b', text))

        return keyword_counts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return Counter()

def read_urls_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file]
        return urls
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except IOError as e:
        print(f"Error reading {file_path}: {e}")
        return []

def save_keyword_counts_to_csv(data, keywords):
    try:
        with open('Keywords_output1.csv', 'w', newline='') as csvfile:
            fieldnames = ['url'] + keywords
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for entry in data:
                row = {'url': entry['url']}
                row.update(entry['keyword_counts'])
                writer.writerow(row)
        print("Keyword counts saved to output_file")
    except IOError as e:
        print(f"Error writing to output_file: {e}")

if __name__ == "__main__":

    # Set the file path for URLs and keywords here
    url_file = 'urls.txt'
    keywords = ["SCN5A", "Nav1.5", "Scn5a", "SkM1", "Sodium channel protein type 5 subunit alpha", "Sodium channel protein cardiac muscle subunit alpha", "Sodium channel protein type V subunit alpha", "Voltage-gated sodium channel subunit alpha Nav1.5", "sodium voltage-gated channel alpha subunit 5", "cardiac tetrodotoxin-insensitive voltage-dependent sodium channel alpha subunit", "Nav1.5c", "SkM2", "antibody", "anti-body", "antibodies", "anti-bodies", "mouse", "mice", "mus musculus"]

    urls = read_urls_from_file(url_file)
    if not urls:
        print("No URLs to process. Exiting.")
        exit(1)

    data = []
    for url in tqdm(urls):
        keyword_counts = count_keyword_occurrences(url, keywords)
        data.append({'url': url, 'keyword_counts': dict(keyword_counts)})

    # Save the file into csv
    save_keyword_counts_to_csv(data, keywords)
