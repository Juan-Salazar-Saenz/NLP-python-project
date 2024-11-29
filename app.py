from flask import Flask, render_template, request, session
from scraper import Scraper
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Necesario para usar sesiones

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

        if data:  # Verificar que se encontró información
            session['products'] = data
            return render_template('results.html', products=data)
        else:
            return "No se encontraron productos.", 404  # Si no se encuentra información

    return render_template('index.html')


@app.route('/nlp_analysis/<int:product_id>', methods=['GET'])
def nlp_analysis(product_id):
    # Recuperar los productos de la sesión
    products = session.get('products')
    if products is None:
        return "No se han encontrado productos para analizar.", 400

    try:
        product = products[product_id]  # Seleccionar el producto por su índice
        # Aquí puedes agregar tu lógica para el análisis NLP
        return render_template('nlp_analysis.html', product=product)
    except IndexError:
        return "Producto no encontrado.", 404


if __name__ == "__main__":
    app.run(debug=True)
