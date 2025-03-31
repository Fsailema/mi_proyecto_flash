from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configuraciones
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///desarrollo_web.db'  # Puedes usar MySQL si prefieres.
app.config['SECRET_KEY'] = 'mi_clave_secreta'  # Cambia esta clave para tu aplicación.
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de Usuario
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """Genera un hash de la contraseña."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña."""
        return check_password_hash(self.password, password)

# Modelo de Producto
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

# Cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Ruta de inicio
@app.route('/')
@login_required
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

# Ruta de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Nombre de usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

# Ruta de Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Ruta para agregar un producto
@app.route('/agregar_producto', methods=['GET', 'POST'])
@login_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']
        # Validaciones básicas
        if not nombre or not precio or not stock:
            flash('Todos los campos son requeridos.', 'error')
            return redirect(url_for('agregar_producto'))
        nuevo_producto = Producto(nombre=nombre, precio=precio, stock=stock)
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('Producto agregado exitosamente', 'success')
        return redirect(url_for('index'))
    return render_template('agregar_producto.html')

# Ruta para editar un producto
@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    producto = Producto.query.get(id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.precio = request.form['precio']
        producto.stock = request.form['stock']
        # Validaciones básicas
        if not producto.nombre or not producto.precio or not producto.stock:
            flash('Todos los campos son requeridos.', 'error')
            return redirect(url_for('editar_producto', id=id))
        db.session.commit()
        flash('Producto actualizado exitosamente', 'success')
        return redirect(url_for('index'))
    return render_template('editar_producto.html', producto=producto)

# Ruta para eliminar un producto
@app.route('/eliminar_producto/<int:id>')
@login_required
def eliminar_producto(id):
    producto = Producto.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('index'))

# Ruta para registrar un nuevo usuario (solo para pruebas)
@app.route('/registrar_usuario', methods=['GET', 'POST'])
def registrar_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validaciones
        if not username or not password:
            flash('El nombre de usuario y la contraseña son requeridos', 'error')
            return redirect(url_for('registrar_usuario'))
        nuevo_usuario = Usuario(username=username)
        nuevo_usuario.set_password(password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash('Usuario registrado exitosamente', 'success')
        return redirect(url_for('login'))
    return render_template('registrar_usuario.html')

if __name__ == '__main__':
    app.run(debug=True)