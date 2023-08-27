import os
import time
import urllib.request
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://a202011070035301700190788.wsxcme.com/static/index.html#shop_detail/_dLaLa_kpkLKpeTkBadzceQg7sQoXEauNlgoGP9w")

elem = driver.find_element(By.CLASS_NAME, "wsxc_label_and_classification")
elem.click()
time.sleep(3)
div_with_bag = driver.find_element(By.XPATH, "//div[contains(text(), 'bag')]")
div_with_bag.click()
time.sleep(3)
div_with_prada = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                                               "'abcdefghijklmnopqrstuvwxyz'), 'prada')]")
div_with_prada.click()
time.sleep(3)

# image_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'https://xcimg.szwego.com/2023')]")
#
# # Generate a list of src attributes from these img elements
# image_src_list = [image.get_attribute("src") for image in image_elements]
#
# cleaned_image_src_list = []
# for src in image_src_list:
#     parsed = urlparse(src)
#     cleaned_src = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
#     cleaned_image_src_list.append(cleaned_src)


all_cleaned_image_src_list = []

# Define a function to capture and clean the image src values
def capture_clean_image_srcs():
    image_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'https://xcimg.szwego.com/2023')]")
    image_src_list = [image.get_attribute("src") for image in image_elements]
    cleaned_image_src_list = []
    for src in image_src_list:
        parsed = urlparse(src)
        cleaned_src = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        cleaned_image_src_list.append(cleaned_src)
    return cleaned_image_src_list

# Capture the initial set of image src values
all_cleaned_image_src_list.extend(capture_clean_image_srcs())

# Scroll and capture more image src values
for i in range(5):  # Adjust the range based on how many times you want to scroll and capture
    # Scroll down
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for 3 seconds for new images to load
    time.sleep(3)

    # Capture more image src values after scrolling
    all_cleaned_image_src_list.extend(capture_clean_image_srcs())

# Remove duplicates if any
all_cleaned_image_src_list = list(set(all_cleaned_image_src_list))

# Create a folder called "prada" if it doesn't exist
if not os.path.exists("prada"):
    os.makedirs("prada")

# Download images
for i, img_url in enumerate(all_cleaned_image_src_list):
    file_name = f"prada/image_{i}.jpg"
    urllib.request.urlretrieve(img_url, file_name)

driver.close()
