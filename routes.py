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

@app.route('/nlp_analysis/<int:product_id>', methods=['GET'])
def nlp_analysis(product_id):
    # Obtén los productos scrapeados
    scraper = Scraper('https://listado.mercadolibre.com.co/')
    products = scraper.scrape_products('producto')  # Esto debe devolver la lista de productos scrapeados

    # Asegúrate de que tienes la lista de productos
    if product_id < len(products):
        product = products[product_id]  # Obtener el producto por su ID
    else:
        return "Producto no encontrado", 404

    # Datos de análisis NLP (vacíos por ahora)
    nlp_data = {
        "resumen": "Análisis de NLP para este producto.",
        "sentimiento": "Positivo"
    }

    return render_template('nlp_analysis.html', product=product, nlp_data=nlp_data)
