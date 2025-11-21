from Scrapers.main_scraper import scrape_capcut_templates

if __name__ == "__main__":
    templates = scrape_capcut_templates(limit=3, get_video_urls=True, get_author_details=True)
