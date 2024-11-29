python -m venv venv
venv\Scripts\activate

pip freeze > requirements.txt
pip install -r requirements.txt


Esta es la estructura de nuestro proyecto, mercadolibre_scraper/
├── .gitignore               # Archivo para ignorar archivos no deseados (como venv, archivos temporales)
├── .env                     # Archivo de configuración de variables de entorno (como claves de API)
├── app.py                   # Archivo principal para ejecutar la app
├── routes.py                # Define las rutas de Flask
├── scraper.py               # Clase Scraper
├── data/                    # Carpeta para almacenar los datos generados
│   └── mercadolibre_data.csv # Archivo CSV con los resultados
├── templates/               # Carpeta para las plantillas HTML
│   ├── index.html           # Página principal con el formulario
│   ├── results.html         # Página para mostrar los resultados
├── static/                  # Archivos estáticos (CSS/JS)
│   ├── css/
│   │   └── styles.css       # Estilos personalizados
│   ├── js/
│   │   └── scripts.js       # Archivo JS con funcionalidades de interacción
└── venv/                    # Entorno virtual  ,, no respondas aun 