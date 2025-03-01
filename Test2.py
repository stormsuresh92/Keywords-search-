import requests
from collections import Counter
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import csv
import re

def count_keyword_occurrences(url, keywords):
    try:
        session = HTMLSession()
        response = session.get(url)
        response.html.render()  # Render JavaScript content
        raw_html = response.html.html.lower()  # Full page source (includes hidden content)

        # Parse with BeautifulSoup to extract visible text
        soup = BeautifulSoup(raw_html, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        visible_text = soup.get_text().lower()  # Only visible text

        keyword_counts = Counter()
        keyword_counts_source = Counter()

        for keyword in keywords:
            escaped_keyword = re.escape(keyword.lower())  # Escape special characters
            # Count in raw page source
            keyword_counts_source[keyword] = len(re.findall(r'\b' + escaped_keyword + r'\b', raw_html))
            # Count in visible text
            keyword_counts[keyword] = len(re.findall(r'\b' + escaped_keyword + r'\b', visible_text))

        return keyword_counts, keyword_counts_source
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return Counter(), Counter()

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

def save_keyword_counts_to_csv(output_file, data, keywords):
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['url'] + [f"{kw}_source" for kw in keywords] + [f"{kw}_visible" for kw in keywords]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for entry in data:
                row = {'url': entry['url']}
                row.update({f"{kw}_source": entry['keyword_counts_source'][kw] for kw in keywords})
                row.update({f"{kw}_visible": entry['keyword_counts'][kw] for kw in keywords})
                writer.writerow(row)
        print(f"Keyword counts saved to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    url_file = 'path/to/your/urls.txt'
    keywords = ["SCN4A", "CMS16", "CMYO22A", "CMYP22A", "HOKPP2", "HYKPP", "HYPP", "NAC1A", 
                "Na(V)1.4", "Nav1.4", "SkM1", "antibody", "anti-body", "antibodies", "anti-bodies", 
                "mouse", "mice", "mus musculus"]

    urls = read_urls_from_file(url_file)
    if not urls:
        print("No URLs to process. Exiting.")
        exit(1)

    data = []
    for url in urls:
        keyword_counts, keyword_counts_source = count_keyword_occurrences(url, keywords)
        data.append({'url': url, 'keyword_counts': dict(keyword_counts), 'keyword_counts_source': dict(keyword_counts_source)})

    output_file = 'path/to/your/output.csv'
    save_keyword_counts_to_csv(output_file, data, keywords)
