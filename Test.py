import requests
from collections import Counter
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import csv
import re

def count_keyword_occurrences(url, keywords):
    try:
        # Fetch the content of the URL using requests_html to render JavaScript
        session = HTMLSession()
        response = session.get(url)
        response.html.render()  # Render JavaScript content if necessary
        content = response.html.html  # Get the rendered HTML

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script and style elements to avoid hidden text issues
        for script in soup(["script", "style"]):
            script.extract()

        # Extract text content
        text = soup.get_text()
        text = text.lower()  # Convert to lowercase for case-insensitive matching

        # Improved regex to retain words with special characters like hyphens, parentheses, and periods
        words = re.findall(r'\b[\w()\-\.]+\b', text)

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

def save_keyword_counts_to_csv(output_file, data, keywords):
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['url'] + keywords
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for entry in data:
                row = {'url': entry['url']}
                row.update(entry['keyword_counts'])
                writer.writerow(row)
        print(f"Keyword counts saved to {output_file}")
    except IOError as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    # Set the file path for URLs and keywords here
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
        keyword_counts = count_keyword_occurrences(url, keywords)
        data.append({'url': url, 'keyword_counts': dict(keyword_counts)})

    # Set the output CSV file path here
    output_file = 'path/to/your/output.csv'
    save_keyword_counts_to_csv(output_file, data, keywords)
