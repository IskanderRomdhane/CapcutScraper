import requests
from bs4 import BeautifulSoup
from Utils.headers import get_headers


def scrape_template_video(template):
    print(f"Scraping video URL for template {template.get('id')}")
    try:
        response = requests.get(template["template_url"], headers=get_headers())
        soup = BeautifulSoup(response.text, 'html.parser')

        #Check video tag
        video_tag = soup.find('video')
        if video_tag and video_tag.has_attr('src'):
            return video_tag['src']

        return None

    except Exception as e:
        print(f"Error scraping video URL: {e}")
        return None