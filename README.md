# online_store

Zora | Online Store
Zora es una plataforma de comercio electrónico especializada en la venta de suplementos para gimnasio y ropa deportiva. Diseñada bajo una arquitectura limpia y eficiente, la aplicación permite a los entusiastas del fitness gestionar sus compras y listas de deseos de manera intuitiva.

🚀 Características
- Gestión de Usuarios: Sistema de autenticación completo (Login/Registro) con protección de rutas.

- Catálogo Fitness: Visualización dinámica de productos, incluyendo suplementación y textiles deportivos.

- Carrito de Compras: Experiencia de compra fluida con persistencia de datos para los artículos seleccionados.

- Lista de Deseos (Wishlist): Funcionalidad para guardar productos favoritos y consultarlos posteriormente.

- Administración de Datos: Uso de modelos relacionales para el control de inventario y pedidos.

🛠️ Stack Tecnológico
Backend: Python con el micro-framework Flask.

- Base de Datos: SQLAlchemy (ORM) para la gestión de modelos y persistencia.

- Seguridad: Flask-Login para el manejo de sesiones de usuario.

- Frontend: Jinja2, HTML5 y CSS3 para interfaces dinámicas.


Instalación:
En el powershell o cmd
- python -m venv entorno

(Recuerda activar el entorno antes de instalar)
cd .\entorno\Scripts\

.\activate          <---- escribelo a secas like this

instalar dependencias:
- pip install -r requirements.txt

Para correr la pagina
python main.py
o
Te metes en el archivo "main.py" y le das a ejecutar con python 🤙