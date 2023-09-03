import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.request import urlretrieve


def fetch_content(url):
    parent_links = []
    child_links = []
    products = []

    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        objs = soup.find_all(class_='categories__children')

        if objs:
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
        else:
            return 'Objects with class "categories__children" not found'
    else:
        return f"Failed to fetch content. HTTP Status Code: {response.status_code}"


def fetch_child_links(url):
    links = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        objs = soup.find_all(class_='showalbumheader__gallerysubtitle')

        if objs:
            for obj in objs:
                a_tags = obj.find_all('a')
                for a_tag in a_tags:
                    link = a_tag['href']
                    links.append(link)
            return links
        else:
            return []
    else:
        return []


def fetch_product_links(url):
    products = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        objs = soup.find_all(class_='album__main')

        if objs:
            for obj in objs:
                link = 'https://expbag.x.yupoo.com' + obj['href']
                products.append(link)

            return products
        else:
            return []
    else:
        return []


def fetch_and_save_images(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        parent_candidates = soup.find_all(class_='yupoo-crumbs-span is-link')
        parent_folder = None
        for candidate in parent_candidates:
            if 'title' in candidate.attrs:
                parent_folder = candidate['title']
                break

        child_folder = soup.find(class_='showalbumheader__gallerytitle').text
        img_elements = soup.find_all('img', attrs={'data-origin-src': True})

        target_folder_path = os.path.join('img', parent_folder, child_folder)

        # Check if child folder already exists
        if os.path.exists(target_folder_path):
            print(f"Skipping download for existing folder: {target_folder_path}")
            return

        if parent_folder and child_folder and img_elements:
            os.makedirs(target_folder_path, exist_ok=True)

            for img in img_elements:
                img_url = 'http:' + img['data-origin-src']
                img_name = os.path.basename(img_url)
                img_path = os.path.join(target_folder_path, img_name)

                # Downloading image using requests with User-Agent
                headers["Referer"] = url
                img_response = requests.get(img_url, headers=headers)
                if img_response.status_code == 200:
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)


# Replace 'your_url_here' with the URL you want to fetch content from
url = 'https://expbag.x.yupoo.com/categories/2880389'
result = fetch_content(url)

# Display the result
print("Result:")
print(result)
