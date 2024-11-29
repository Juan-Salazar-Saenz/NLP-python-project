import httpx
from bs4 import BeautifulSoup
import random
import time
import os

class Scraper:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
    ]

    def __init__(self, base_url):
        self.base_url = base_url
        self.data = []

    def scrape_products(self, product_name):
        cleaned_name = product_name.replace(" ", "-").lower()
        page_number = 50

        with httpx.Client(verify=False) as client:
            for i in range(1, 200):  # Máximo 200 páginas
                headers = {
                    "User-Agent": random.choice(self.USER_AGENTS)
                }
                url = f"{self.base_url}{cleaned_name}_Desde_{page_number + 1}_NoIndex_True"
                print(f"Scrapeando página número {i}. {url}")

                try:
                    response = client.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                except httpx.RequestError as e:
                    print(f"Error al realizar la solicitud: {e}")
                    break

                content = soup.find_all('li', class_='ui-search-layout__item')
                if not content:
                    print("No hay más contenido para scrapear.")
                    break

                for post in content:
                    try:
                        title = post.find('h2').text
                        price = post.find('span', class_='andes-money-amount__fraction').text
                        post_link = post.find("a")["href"]
                        img_link = post.find("img").get("data-src", post.find("img").get("src"))
                        self.data.append({"title": title, "price": price, "post link": post_link, "image link": img_link})
                    except AttributeError:
                        continue

                page_number += 50
                time.sleep(random.uniform(3.0, 10.0))

        return self.data
