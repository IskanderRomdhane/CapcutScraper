import requests
from bs4 import BeautifulSoup
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from Utils.headers import get_headers
from Utils.Parser import parse_number
from Scrapers.authorDetails import scrape_author_details
from Scrapers.videoScraper import scrape_template_video


def extract_template_data(card, get_video_urls=False, get_author_details=False):
    try:
        img = card.select_one('img.main-image')
        image_url = img['src'] if img and img.has_attr('src') else None

        duration_element = card.select_one('div.preview-template-desc-duration')
        duration = duration_element.get_text(strip=True) if duration_element else None

        usage_element = card.select_one('div.preview-template-desc-usage')
        usage_text = usage_element.get_text(strip=True) if usage_element else "0"
        usage_count = parse_number(usage_text)

        desc_container = card.select_one('div.lv-template-card-desc-container')
        title = desc_container.select_one('h2.lv-template-card-desc').get_text(strip=True) if desc_container else None
        subtitle = desc_container.select_one('div.lv-template-card-subtitle').get_text(strip=True) if desc_container else None

        template_id = card.get('data-id', '')

        template = {
            'id': template_id,
            'title': title,
            'description': subtitle,
            'image_url': image_url,
            'duration': duration,
            'usage_count': usage_count,
            'author': None,
            'template_url': f"https://www.capcut.com/templates/{template_id}?scene=category&template_scale=9%3A16&enter_from=first_page&from_page=template_page" if template_id else None,
            'video_url': None
        }

        if get_video_urls:
            template['video_url'] = scrape_template_video(template)

        if get_author_details:
            template['author'] = scrape_author_details(template)

        return template

    except Exception as e:
        print(f"Error processing template card: {e}")
        return None


def scrape_capcut_templates(limit=None, get_video_urls=False, get_author_details=False, output_file="capcut_templates.json"):
    print("Starting CapCut template scraper...")
    base_url = "https://www.capcut.com/templates"

    try:
        response = requests.get(base_url, headers=get_headers())
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.select('div.waterfall__item')

        if limit:
            cards = cards[:limit]

        templates = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_card = {
                executor.submit(extract_template_data, card, get_video_urls, get_author_details): card
                for card in cards
            }

            for future in as_completed(future_to_card):
                result = future.result()
                if result:
                    templates.append(result)

        print(f"\nScraped {len(templates)} templates.")

        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(templates, f, ensure_ascii=False, indent=4)
        print(f"Saved templates to {output_file}")

        return templates

    except Exception as e:
        print(f"Error scraping CapCut templates: {e}")
        return []
