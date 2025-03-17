from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

# Configuraciones de la app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/desarrollo_web'
app.config['SECRET_KEY'] = 'secretkey'  # Cambia esto por una clave segura
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo de usuario
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Formulario de login
class LoginForm(FlaskForm):
    username = StringField('nombre de usuario', validators=[DataRequired()])
    password = PasswordField('contraeña', validators=[DataRequired()])

# Rutas
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()  # Crear el formulario aquí

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Credenciales incorrectas.')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()
        flash('Usuario registrado con éxito.')
        return redirect(url_for('login'))

    return render_template('formulario.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    if request.method == 'POST':
        # Capturamos los datos del formulario
        nombre = request.form['nombre']
        email = request.form['email']
        mensaje = request.form['mensaje']

        # Redirigir a la página de resultados con los datos capturados
        return render_template('resultado.html', nombre=nombre, email=email, mensaje=mensaje)

    # Renderiza el formulario en caso de que sea un GET
    return render_template('formulario.html')

@app.route('/about')
def about():
    return render_template('about.html')

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)