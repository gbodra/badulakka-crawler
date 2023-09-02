import os
import time
import urllib.request
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException

SEARCH_TERMS = ["BVLGARI", "Versace", "Balenciaga", "Chanel", "Gucci", "Hermes", "Louis Vuitton", "MIUMIU"
                "Dior", "Burberry", "Yves Saint Laurent"]  # prada, Chloe Add other terms you're interested in
SCROLLS = 5
SLEEP = 2


def click_element_by_class(driver, class_name):
    elem = driver.find_element(By.CLASS_NAME, class_name)
    elem.click()


def click_element_with_text(driver, text, case_sensitive=True):
    try:
        if case_sensitive:
            elem = driver.find_element(By.XPATH, f"//div[contains(text(), '{text}')]")
        else:
            elem = driver.find_element(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                                                 f"'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]")
        elem.click()
    except ElementNotInteractableException:
        try:
            elem.send_keys(Keys.RETURN)
        except Exception as e:
            print(f"Failed to interact with the element. Error: {e}")


def capture_clean_image_srcs(driver):
    image_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'https://xcimg.szwego.com/2023')]")
    image_src_list = [image.get_attribute("src") for image in image_elements]

    cleaned_image_src_list = []
    for src in image_src_list:
        parsed = urlparse(src)
        cleaned_src = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        cleaned_image_src_list.append(cleaned_src)

    return cleaned_image_src_list


def download_images(image_list, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for i, img_url in enumerate(image_list):
        file_name = f"{folder_name}/image_{i}.jpg"
        urllib.request.urlretrieve(img_url, file_name)


def main():
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.get("https://a202011070035301700190788.wsxcme.com/static/index.html#shop_detail"
               "/_dLaLa_kpkLKpeTkBadzceQg7sQoXEauNlgoGP9w")

    for term in SEARCH_TERMS:
        # Navigate through the page to 'bag'
        time.sleep(SLEEP)
        click_element_by_class(driver, "wsxc_label_and_classification")
        time.sleep(SLEEP)
        click_element_with_text(driver, "bag")

        # Navigate to each search term and capture images
        time.sleep(SLEEP)
        click_element_with_text(driver, term, case_sensitive=False)
        time.sleep(SLEEP)

        all_cleaned_image_src_list = []
        all_cleaned_image_src_list.extend(capture_clean_image_srcs(driver))

        for _ in range(SCROLLS):  # Scroll 5 times
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SLEEP)
            all_cleaned_image_src_list.extend(capture_clean_image_srcs(driver))

        # Remove duplicates
        all_cleaned_image_src_list = list(set(all_cleaned_image_src_list))

        # Download images
        download_images(all_cleaned_image_src_list, term)

        # Navigate back to the previous page
        driver.back()

    driver.close()


if __name__ == "__main__":
    main()
