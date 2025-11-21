import requests
from bs4 import BeautifulSoup
from Utils.headers import get_headers
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


def scrape_author_details(template):
    print(f"Scraping Author details for template {template.get('id')}")
    author = {
        "name": "",
        "avatar_url": "",
        "gender": "",
        "description": "",
        "creator_url": ""
    }

    try:
        profil_url = get_author_profile_url(template["template_url"])
        author["creator_url"] = profil_url
        response = requests.get(profil_url , headers=get_headers())
        soup = BeautifulSoup(response.text, 'html.parser')

        avatar_div = soup.find('span', class_='lv-avatar-image')
        if avatar_div :
            author["avatar_url"] = avatar_div.find('img')['src']

        #Extract Author name
        name_div = soup.find('div', class_='homepageHeaderTitleWrapper-kPVJkT')
        if name_div :
            author["name"] = name_div.find('div' , class_='homepageHeaderTitle-CoAbbQ').text

        description_div = soup.find('div', class_='homepageHeaderIntro-gdGcY1')
        if description_div :
            author["description"] = description_div.text
        return author

    except Exception as e:
        print(f"Error scraping author details: {e}")
        return author


def get_author_profile_url(template_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--start-maximized")  # Maximize window to ensure visibility
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(template_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.toC_info.couldClick"))
        )

        #clicking the author name
        try:
            author_name = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.toC_info.couldClick div.name"))
            )
            time.sleep(3)
            author_name.click()
        except Exception as name_error:
            print(f"Couldn't click name: {name_error}. Trying avatar...")

        # Wait for URL change
        original_url = driver.current_url
        profile_url = None

        #Extract Profil url
        try:
            WebDriverWait(driver, 5).until(
                lambda d: d.current_url != original_url and "creator" in d.current_url.lower()
            )
            profile_url = driver.current_url
        except TimeoutException:
            # Method 2: Check if new tab opened
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[1])
                profile_url = driver.current_url

        if profile_url and profile_url != original_url:
            return profile_url
        else:
            return None

    except Exception as e:
        print(f"error: {str(e)}")
        return None
    finally:
        driver.quit()