from app import app
from flask import render_template, request
from scraper import Scraper

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        product_name = request.form['product_name']
        country = request.form['country']
        base_urls = {
            "colombia": "https://listado.mercadolibre.com.co/",
            "argentina": "https://listado.mercadolibre.com.ar/",
            "mexico": "https://listado.mercadolibre.com.mx/"
        }
        base_url = base_urls.get(country.lower(), "https://listado.mercadolibre.com.co/")

        scraper = Scraper(base_url)
        data = scraper.scrape_products(product_name)
        return render_template('results.html', products=data)
    return render_template('index.html')
