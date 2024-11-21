import json
import time
from pathlib import Path
from typing import List

import requests
from bs4 import BeautifulSoup
from loguru import logger


BASE_DIR = Path(__file__).parent.parent


class HouzzCrawler:
    def __init__(self):
        self.BASE_URL = \
            'https://www.houzz.com/professionals/general-contractor/california-md-us-probr0-bo~t_11786~r_4350049'
        self.records_per_page = 15

    def run(self):
        all_detail_pages_urls = self.crawl_detail_pages_urls_from_list_pages()
        contractors_data = self.crawl_detail_pages(all_detail_pages_urls)
        self.save_contractors_data(contractors_data)

    def crawl_detail_pages_urls_from_list_pages(self) -> List[str]:
        detail_urls = []
        page = 0
        while page < 10:
            current_page_detail_pages_urls = self.crawl_list_page(page)
            detail_urls.extend(current_page_detail_pages_urls)

            page += 1
        return detail_urls

    def crawl_detail_pages(self, all_detail_pages_urls) -> List[dict]:
        contractors_data = []

        for i, detail_pages_url in enumerate(all_detail_pages_urls):
            try:
                response = requests.get(detail_pages_url)
                logger.info(f"Requested {i+1}/{len(all_detail_pages_urls)} detail pages")
                if i == 120:
                    time.sleep(30)
            except Exception as e:
                logger.error(f"Something went wrong while requesting the contractor detail page: {str(e)}")
                exit()

            business_details = self.parse_business_details(response.content) # noqa
            contractors_data.append({
                "business_details": business_details
            })
        return contractors_data

    @staticmethod
    def save_contractors_data(contractors_data: list):
        with open(BASE_DIR / "contractors_data.json", "w") as json_file:
            json.dump(contractors_data, json_file, indent=4)

    def crawl_list_page(self, page_number: int) -> List[str]:
        try:
            response = requests.get(self.BASE_URL, params={"fi": page_number * self.records_per_page})
            logger.info(f"Requested list page #{page_number+1}")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Something went wrong while requesting the contractor list page: {str(e)}")
            exit()

        detail_pages_links = self.parse_detail_pages_urls(response.content) # noqa
        return detail_pages_links

    @staticmethod
    def parse_detail_pages_urls(page_content: bytes) -> List[str]:
        detail_pages_urls = []

        soup = BeautifulSoup(page_content, "html.parser")

        contractors_elements = soup.find("ul", class_="hz-pro-search-results")
        if contractors_elements:
            for contractor_element in contractors_elements:
                sponsored_div = contractor_element.find("div", string="Sponsored")  # noqa
                if sponsored_div:
                    continue

                contractor_a_element = contractor_element.find("a")
                if contractor_a_element:
                    contractor_detail_page_link = contractor_a_element.get("href")  # noqa
                    detail_pages_urls.append(contractor_detail_page_link)

        return detail_pages_urls

    @staticmethod
    def parse_business_details(page_content: bytes):
        contractors_business_details = {}

        soup = BeautifulSoup(page_content, "html.parser")
        business_details = soup.find("div", {"data-container": "Business Details"})
        business_details_blocks = business_details.find_all("div", recursive=False)

        for block in business_details_blocks:
            block_header = block.find('h3').text
            block_content = block.find('p').text
            contractors_business_details.update({
                block_header: block_content
            })
        return contractors_business_details
