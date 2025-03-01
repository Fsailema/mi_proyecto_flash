from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'

# Definir el formulario
class ContactForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mensaje = TextAreaField('Mensaje', validators=[DataRequired()])
    enviar = SubmitField('Enviar')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = ContactForm()
    if form.validate_on_submit():
        # Aquí puedes manejar los datos del formulario (por ejemplo, guardarlos en la base de datos o enviar un correo)
        nombre = form.nombre.data
        email = form.email.data
        mensaje = form.mensaje.data
        # Ejemplo de cómo manejar los datos
        print(f"Nombre: {nombre}, Email: {email}, Mensaje: {mensaje}")
        return redirect(url_for('index'))  # Redirigir a la página principal después de enviar el formulario
    return render_template('formulario.html', form=form)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)



from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import json
import csv
import os

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Verificar que la carpeta 'datos' exista, si no, crearla
if not os.path.exists('datos'):
    os.makedirs('datos')

# Modelo de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

# Rutas para la interfaz web
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

# ==========================
# PERSISTENCIA EN ARCHIVOS

# Guardar en archivo TXT
@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    with open('datos/datos.txt', 'a') as file:
        file.write(f"{data['nombre']}, {data['edad']}\n")
    return jsonify({"mensaje": "Datos guardados en TXT"})

# Leer desde archivo TXT
@app.route('/leer_txt', methods=['GET'])
def leer_txt():
    if not os.path.exists('datos/datos.txt'):
        return jsonify({"mensaje": "Archivo vacío o no existe"})

    with open('datos/datos.txt', 'r') as file:
        contenido = file.readlines()

    return jsonify({"datos": contenido})

# Guardar en archivo JSON
@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    archivo = 'datos/datos.json'

    try:
        if os.path.exists(archivo):
            with open(archivo, 'r') as file:
                try:
                    contenido = json.load(file)
                except json.JSONDecodeError:
                    contenido = []
        else:
            contenido = []

        contenido.append(data)

        with open(archivo, 'w') as file:
            json.dump(contenido, file, indent=4)

    except Exception as e:
        return jsonify({"mensaje": f"Error al guardar datos en JSON: {str(e)}"}), 500

    return jsonify({"mensaje": "Datos guardados en JSON"})

# Leer desde archivo JSON
@app.route('/leer_json', methods=['GET'])
def leer_json():
    archivo = 'datos/datos.json'

    if not os.path.exists(archivo):
        return jsonify({"mensaje": "Archivo vacío o no existe"})

    try:
        with open(archivo, 'r') as file:
            try:
                contenido = json.load(file)
            except json.JSONDecodeError:
                return jsonify({"mensaje": "Error en la lectura del archivo JSON"}), 500
    except Exception as e:
        return jsonify({"mensaje": f"Error al leer el archivo JSON: {str(e)}"}), 500

    return jsonify({"datos": contenido})

# Guardar en archivo CSV
@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    archivo = 'datos/datos.csv'

    existe = os.path.exists(archivo)

    try:
        with open(archivo, 'a', newline='') as file:
            writer = csv.writer(file)
            if not existe:
                writer.writerow(["nombre", "edad"])  # Escribir encabezado solo si es un archivo nuevo
            writer.writerow([data['nombre'], data['edad']])

    except Exception as e:
        return jsonify({"mensaje": f"Error al guardar datos en CSV: {str(e)}"}), 500

    return jsonify({"mensaje": "Datos guardados en CSV"})

# Leer desde archivo CSV
@app.route('/leer_csv', methods=['GET'])
def leer_csv():
    archivo = 'datos/datos.csv'

    if not os.path.exists(archivo):
        return jsonify({"mensaje": "Archivo vacío o no existe"})

    try:
        with open(archivo, 'r') as file:
            reader = csv.DictReader(file)
            contenido = [row for row in reader]

    except Exception as e:
        return jsonify({"mensaje": f"Error al leer el archivo CSV: {str(e)}"}), 500

    return jsonify({"datos": contenido})

# ==========================
# PERSISTENCIA EN SQLite

# Guardar usuario en SQLite
@app.route('/guardar_usuario', methods=['POST'])
def guardar_usuario():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    try:
        nuevo_usuario = Usuario(nombre=data['nombre'], edad=data['edad'])
        db.session.add(nuevo_usuario)
        db.session.commit()
    except Exception as e:
        return jsonify({"mensaje": f"Error al guardar usuario en SQLite: {str(e)}"}), 500

    return jsonify({"mensaje": "Usuario guardado en SQLite"})

# Leer todos los usuarios desde SQLite
@app.route('/leer_usuarios', methods=['GET'])
def leer_usuarios():
    try:
        usuarios = Usuario.query.all()
        resultado = [{"id": u.id, "nombre": u.nombre, "edad": u.edad} for u in usuarios]
    except Exception as e:
        return jsonify({"mensaje": f"Error al obtener usuarios de la base de datos: {str(e)}"}), 500

    return jsonify({"usuarios": resultado})

# Obtener usuario por ID
@app.route('/usuario/<int:id>', methods=['GET'])
def obtener_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if usuario:
            return jsonify({"id": usuario.id, "nombre": usuario.nombre, "edad": usuario.edad})
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"mensaje": f"Error al obtener usuario: {str(e)}"}), 500

# Eliminar usuario por ID
@app.route('/eliminar_usuario/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        usuario = Usuario.query.get(id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return jsonify({"mensaje": "Usuario eliminado"})
        return jsonify({"mensaje": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"mensaje": f"Error al eliminar usuario: {str(e)}"}), 500

# Crear las tablas si no existen
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Error al crear la base de datos: {e}")

if __name__ == '__main__':
    app.run(debug=True)