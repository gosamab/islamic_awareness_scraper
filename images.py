import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, quote

def safe_folder_name(url):
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/").replace("/", "_")
    folder_name = f"{parsed_url.netloc}{'_' + path if path else ''}"
    return quote(folder_name)

def extract_background_images(soup, base_url):
    image_urls = set()
    for element in soup.find_all(style=True):
        style = element["style"]
        matches = re.findall(r"url\(['\"]?(.*?)['\"]?\)", style)
        for match in matches:
            full_url = urljoin(base_url, match)
            image_urls.add(full_url)
    return image_urls

def get_internal_links(url, domain):
    internal_links = set()
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return internal_links

        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            link = urljoin(url, a_tag["href"])
            if urlparse(link).netloc == domain:
                internal_links.add(link)

    except requests.RequestException as e:
        print(f"Error fetching links from {url}: {e}")
    
    return internal_links

def download_images(url, base_output_folder):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"Failed to retrieve {url}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        
        img_tags = soup.find_all("img")
        img_urls = {urljoin(url, img["src"]) for img in img_tags if img.get("src")}

        bg_images = extract_background_images(soup, url)
        img_urls.update(bg_images)

        page_folder = os.path.join(base_output_folder, safe_folder_name(url))
        os.makedirs(page_folder, exist_ok=True)

        for img_url in img_urls:
            try:
                img_data = requests.get(img_url, timeout=5).content
                img_name = os.path.join(page_folder, os.path.basename(urlparse(img_url).path) or "image.jpg")
                
                with open(img_name, "wb") as f:
                    f.write(img_data)
                print(f"Downloaded {img_name}")

            except requests.RequestException as e:
                print(f"Error downloading {img_url}: {e}")

    except requests.RequestException as e:
        print(f"Error fetching images from {url}: {e}")

def scrape_website(base_url):
    domain = urlparse(base_url).netloc
    base_output_folder = f"images_{domain.replace('.', '_')}"
    
    visited_links = set()
    to_visit = {base_url}

    all_links = set()

    while to_visit:
        current_url = to_visit.pop()
        if current_url in visited_links:
            continue

        print(f"\nScraping: {current_url}")
        visited_links.add(current_url)

        internal_links = get_internal_links(current_url, domain)
        all_links.update(internal_links)
        to_visit.update(internal_links - visited_links)

        download_images(current_url, base_output_folder)

    print("\nAll extracted internal links:")
    for link in all_links:
        print(link)

if __name__ == "__main__":
    website_url = input("Enter website URL: ")
    scrape_website(website_url)
