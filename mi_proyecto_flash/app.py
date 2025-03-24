from flask import Flask, render_template, request, redirect, url_for, g
import pymysql
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymysql.cursors import DictCursor
from forms import ProductoForm  # Importar el formulario

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para las sesiones de Flask

# Configuración de la base de datos
DB_CONFIG = {
    "host": "localhost",
    "user": "favi",
    "password": "favio",  # Agrega tu contraseña si es necesaria
    "database": "desarrollo_web",
    "cursorclass": DictCursor  # Devuelve resultados como diccionarios
}

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Ruta de login si el usuario no está autenticado

# Función para obtener conexión a la base de datos
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**DB_CONFIG)
    return g.db

# Cerrar la conexión después de cada solicitud
@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Clase User para Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

    @staticmethod
    def get(user_id):
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = cursor.fetchone()
            if user:
                return User(user['id'])
            return None

# Cargar el usuario con Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# 🛠 Crear Producto
@app.route('/crear', methods=['GET', 'POST'])
@login_required  # Asegura que solo los usuarios autenticados puedan crear productos
def crear_producto():
    form = ProductoForm()  # Crear una instancia del formulario

    if form.validate_on_submit():  # Si el formulario se envía correctamente
        nombre = form.nombre.data
        precio = form.precio.data
        stock = form.stock.data
        try:
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute("INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s)",
                               (nombre, precio, stock))
                db.commit()
            return redirect(url_for('mostrar_productos'))
        except pymysql.MySQLError as e:
            return f"Error en la base de datos: {e}"
    return render_template('formulario.html', form=form)  # Pasamos el formulario al template

# 🛠 Leer Productos
@app.route('/productos')
@login_required  # Asegura que solo los usuarios autenticados puedan ver los productos
def mostrar_productos():
    try:
        db = get_db()  # Esta línea debe estar separada
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM productos")
            productos = cursor.fetchall()
        return render_template('productos.html', productos=productos)
    except pymysql.MySQLError as e:
        return f"Error en la base de datos: {e}"

# 🛠 Actualizar Producto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    form = ProductoForm()  # Crear una instancia del formulario
    try:
        db = get_db()
        with db.cursor() as cursor:
            if request.method == 'POST' and form.validate_on_submit():
                nombre = form.nombre.data
                precio = form.precio.data
                stock = form.stock.data
                cursor.execute("UPDATE productos SET nombre=%s, precio=%s, stock=%s WHERE id_producto=%s",
                               (nombre, precio, stock, id))
                db.commit()
                return redirect(url_for('mostrar_productos'))

            cursor.execute("SELECT * FROM productos WHERE id_producto=%s", (id,))
            producto = cursor.fetchone()
            form.nombre.data = producto['nombre']
            form.precio.data = producto['precio']
            form.stock.data = producto['stock']
        return render_template('formulario.html', form=form)  # Pasamos el formulario al template
    except pymysql.MySQLError as e:
        return f"Error en la base de datos: {e}"

# 🛠 Eliminar Producto
@app.route('/eliminar/<int:id>')
@login_required
def eliminar_producto(id):
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM productos WHERE id_producto=%s", (id,))
            db.commit()
        return redirect(url_for('mostrar_productos'))
    except pymysql.MySQLError as e:
        return f"Error en la base de datos: {e}"

# 🏠 Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# 📄 Página "Acerca de"
@app.route('/about')
def about():
    return render_template('about.html')

# 🚪 Iniciar sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):  # Verificar el hash de la contraseña
                login_user(User(user['id']))
                return redirect(url_for('index'))

        return 'Credenciales incorrectas', 401

    return render_template('login.html')

# 🚪 Cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)