from flask import Flask, render_template, request, session
from scraper import Scraper
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

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

        # Lógica para obtener los comentarios y la puntuación del producto usando Selenium y BeautifulSoup
        options = Options()
        options.add_argument("--start-maximized")  # Maximiza la ventana
        service = Service(ChromeDriverManager().install())  # Usar WebDriverManager

        driver = webdriver.Chrome(service=service, options=options)

        # Acceder a la página del producto
        driver.get(product['post link'])

        # Esperar hasta que la página cargue completamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        # Intentar cerrar el banner de cookies si está presente
        try:
            cookie_banner = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cookie-consent-banner-opt-out__container button')))
            cookie_banner.click()  # Cierra el banner de cookies
        except TimeoutException:
            pass  # Si no se encuentra el banner de cookies, continuamos

        # Espera explícita para asegurarse de que el botón "Mostrar todas las opiniones" esté clickeable
        try:
            see_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'show-more-click')))
            
            # Desplazar hacia el botón para asegurarse de que esté en la vista
            driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)

            # Hacer clic en el botón
            see_more_button.click()
        except Exception as e:
            print("No se encontró el botón de 'Mostrar todas las opiniones', extraeremos los comentarios visibles directamente.")

        # Extraer el HTML de la página después de hacer clic (o si no se hace clic)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Crear listas vacías para almacenar los datos de los comentarios
        dates = []
        ratings = []
        comments = []

        # Buscar los comentarios visibles directamente en la página
        reviews = soup.find_all('article', class_='ui-review-capability-comments__comment')

        # Si no se encuentran comentarios, crear un DataFrame vacío
        if not reviews:
            print("No se encontraron comentarios en la página.")
            df = pd.DataFrame(columns=['Fecha', 'Calificación', 'Comentario'])
        else:
            # Si hay comentarios, extraerlos
            for review in reviews:
                # Extraer la fecha
                try:
                    date = review.find('span', class_='ui-review-capability-comments__comment__date').text.strip()
                    dates.append(date)
                except AttributeError:
                    dates.append('Fecha no disponible')
                
                # Extraer la calificación (contando las estrellas)
                try:
                    rating_text = review.find('p', class_='andes-visually-hidden').text.strip()  # Obtener el texto que contiene la calificación
                    # Extraer el número de calificación del texto (por ejemplo, 'Calificación 1 de 5')
                    rating = rating_text.split(' ')[1]  # Tomamos el número después de "Calificación"
                    ratings.append(rating)
                except AttributeError:
                    ratings.append('Calificación no disponible')
                
                # Extraer el comentario
                try:
                    comment = review.find('p', class_='ui-review-capability-comments__comment__content').text.strip()
                    comments.append(comment)
                except AttributeError:
                    comments.append('Comentario no disponible')

            # Crear el DataFrame con los datos extraídos
            df = pd.DataFrame({
                'Fecha': dates,
                'Calificación': ratings,
                'Comentario': comments
            })

        driver.quit()  # Cerrar el navegador cuando ya termine

        return render_template('nlp_analysis.html', product=product, reviews=df.to_html(classes='table table-bordered'))

    except IndexError:
        return "Producto no encontrado.", 404
    
@app.route('/results', methods=['GET', 'POST'])
def results():
    # Verificar si los productos están en la sesión
    products = session.get('products')
    if not products:
        return "No se encontraron productos.", 404  # Si no hay productos guardados

    return render_template('results.html', products=products)


if __name__ == "__main__":
    app.run(debug=True)
