import requests
import psycopg2
from bs4 import BeautifulSoup, NavigableString
from urllib.parse import urljoin, urlparse

def read_html_from_url(url):
    """Fetch HTML content from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Failed to retrieve HTML from {url}: {e}")
        return None

def extract_links(base_url, html):
    """Extract links from HTML while maintaining hierarchy."""
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('body')
    
    if body is None:
        print("No <body> tag found in HTML.")
        return []

    link_info = []
    traverse_hierarchy(body, [], link_info, base_url)
    return link_info

def traverse_hierarchy(element, current_path, link_info, base_url):
    """Recursively traverse HTML to extract links."""
    if element.name == 'a' and element.has_attr('href'):
        href = element['href']
        full_url = urljoin(base_url, href)
        parsed_url = urlparse(full_url)

        if parsed_url.path.endswith('/'):
            parent_path = parsed_url.path.rstrip('/')
        else:
            parent_path = '/'.join(parsed_url.path.split('/'))

        if parent_path == '':
            parent_path = '/'

        link_info.append({
            'id': len(link_info) + 1,
            'title': element.get_text(strip=True),
            'url': full_url,
            'parent': parent_path
        })

    for child in element.children:
        if isinstance(child, NavigableString):
            continue
        traverse_hierarchy(child, current_path + [element.name], link_info, base_url)

def connect_to_database():
    """Establish connection to PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='islamic_awareness',
            user='postgres',
            password='postgres'
        )
        return conn
    except psycopg2.DatabaseError as error:
        print(f"Database connection failed: {error}")
        return None

def insert_links(conn, link_info):
    """Insert extracted links into the database efficiently."""
    try:
        with conn.cursor() as cur:
            query = """
                INSERT INTO links (title, url, parent)
                VALUES (%s, %s, %s)
            """
            data = [(link['title'], link['url'], link['parent']) for link in link_info]
            cur.executemany(query, data)
        conn.commit()
        print(f"Inserted {len(link_info)} links into the database.")
    except psycopg2.DatabaseError as error:
        print(f"Failed to insert links: {error}")
        conn.rollback()

def main():
    """Main function to extract and store links."""
    url = input("Enter URL to scrape: ").strip()
    html = read_html_from_url(url)

    if html:
        links = extract_links(url, html)

        if links:
            print(f"Extracted {len(links)} links:")
            for link in links:
                print(link)

            conn = connect_to_database()
            if conn:
                insert_links(conn, links)
                conn.close()
        else:
            print("No links found.")

if __name__ == "__main__":
    main()
