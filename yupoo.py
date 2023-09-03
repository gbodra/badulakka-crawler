import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup

# Constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}


def get_soup(url, headers=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Failed to fetch {url}. Error: {e}")
        return None


def fetch_content(url):
    parent_links = []
    child_links = []
    products = []

    soup = get_soup(url)
    if not soup:
        return f"Failed to fetch content."

    objs = soup.find_all(class_='categories__children')
    if not objs:
        return 'Objects with class "categories__children" not found'

    for obj in tqdm(objs):
        a_tag = obj.find('a')
        if a_tag:
            link = 'https://expbag.x.yupoo.com' + a_tag['href']
            parent_links.append(link)

    for link in tqdm(parent_links):
        child_links += fetch_child_links(link)

    for link in tqdm(child_links):
        products += fetch_product_links(link)

    for product in tqdm(products):
        fetch_and_save_images(product)

    return products


def fetch_child_links(url):
    links = []
    soup = get_soup(url)
    if not soup:
        return []

    objs = soup.find_all(class_='showalbumheader__gallerysubtitle')
    for obj in objs:
        a_tags = obj.find_all('a')
        for a_tag in a_tags:
            links.append(a_tag['href'])
    return links


def fetch_product_links(url):
    products = []
    soup = get_soup(url)
    if not soup:
        return []

    objs = soup.find_all(class_='album__main')
    for obj in objs:
        link = 'https://expbag.x.yupoo.com' + obj['href']
        products.append(link)

    return products


def fetch_and_save_images(url):
    soup = get_soup(url, headers=HEADERS)
    if not soup:
        return

    parent_candidates = soup.find_all(class_='yupoo-crumbs-span is-link')
    parent_folder = next((c['title'] for c in parent_candidates if 'title' in c.attrs), None)

    child_folder = soup.find(class_='showalbumheader__gallerytitle').text
    img_elements = soup.find_all('img', attrs={'data-origin-src': True})

    target_folder_path = os.path.join('img', parent_folder, child_folder)
    if os.path.exists(target_folder_path):
        print(f"Skipping download for existing folder: {target_folder_path}")
        return

    if parent_folder and child_folder and img_elements:
        os.makedirs(target_folder_path, exist_ok=True)

        for img in img_elements:
            img_url = 'http:' + img['data-origin-src']
            img_name = os.path.basename(img_url)
            img_path = os.path.join(target_folder_path, img_name)
            try:
                HEADERS["Referer"] = url
                img_response = requests.get(img_url, headers=HEADERS)
                img_response.raise_for_status()
                with open(img_path, 'wb') as f:
                    f.write(img_response.content)
            except requests.RequestException as e:
                print(f"Failed to download {img_url}. Error: {e}")


# Main Execution
if __name__ == "__main__":
    url = 'https://expbag.x.yupoo.com/categories/2880389'
    result = fetch_content(url)
    print("Result:")
    print(result)
