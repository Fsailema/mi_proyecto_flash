from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
import csv
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/desarrollo_web.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Verificar que la carpeta 'datos' exista
if not os.path.exists('datos'):
    os.makedirs('datos')

# Modelo de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(db.Integer, nullable=False)

# ==========================
# Rutas de la aplicación

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/prueba')
def prueba():
    return jsonify({"mensaje": "Ruta de prueba funcionando correctamente"})


# ==========================
# PERSISTENCIA EN ARCHIVOS

@app.route('/guardar_txt', methods=['POST'])
def guardar_txt():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    with open('datos/datos.txt', 'a') as file:
        file.write(f"{data['nombre']}, {data['edad']}\n")
    return jsonify({"mensaje": "Datos guardados en TXT"})

@app.route('/leer_txt', methods=['GET'])
def leer_txt():
    archivo = 'datos/datos.txt'
    if not os.path.exists(archivo):
        return jsonify({"mensaje": "Archivo vacío o no existe"})

    with open(archivo, 'r') as file:
        contenido = file.readlines()
    return jsonify({"datos": contenido})

@app.route('/guardar_json', methods=['POST'])
def guardar_json():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    archivo = 'datos/datos.json'
    contenido = []

    if os.path.exists(archivo):
        try:
            with open(archivo, 'r') as file:
                contenido = json.load(file)
        except json.JSONDecodeError:
            pass

    contenido.append(data)

    with open(archivo, 'w') as file:
        json.dump(contenido, file, indent=4)

    return jsonify({"mensaje": "Datos guardados en JSON"})

@app.route('/leer_json', methods=['GET'])
def leer_json():
    archivo = 'datos/datos.json'
    if not os.path.exists(archivo):
        return jsonify({"mensaje": "Archivo vacío o no existe"})

    try:
        with open(archivo, 'r') as file:
            contenido = json.load(file)
    except json.JSONDecodeError:
        return jsonify({"mensaje": "Error en la lectura del archivo JSON"}), 500

    return jsonify({"datos": contenido})

@app.route('/guardar_csv', methods=['POST'])
def guardar_csv():
    data = request.json
    if not data.get('nombre') or not data.get('edad'):
        return jsonify({"mensaje": "Nombre y edad son campos obligatorios"}), 400

    archivo = 'datos/datos.csv'
    existe = os.path.exists(archivo)

    with open(archivo, 'a', newline='') as file:
        writer = csv.writer(file)
        if not existe:
            writer.writerow(["nombre", "edad"])
        writer.writerow([data['nombre'], data['edad']])

    return jsonify({"mensaje": "Datos guardados en CSV"})

@app.route('/leer_csv', methods=['GET'])
def leer_csv():
    archivo = 'datos/datos.csv'
    if not os.path.exists(archivo):
        return jsonify({"mensaje": "Archivo vacío o no existe"})

    with open(archivo, 'r') as file:
        reader = csv.DictReader(file)
        contenido = [row for row in reader]

    return jsonify({"datos": contenido})

# ==========================
# PERSISTENCIA EN SQLite

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

@app.route('/leer_usuarios', methods=['GET'])
def leer_usuarios():
    try:
        usuarios = Usuario.query.all()
        resultado = [{"id": u.id, "nombre": u.nombre, "edad": u.edad} for u in usuarios]
    except Exception as e:
        return jsonify({"mensaje": f"Error al obtener usuarios de la base de datos: {str(e)}"}), 500

    return jsonify({"usuarios": resultado})

@app.route('/usuario/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        return jsonify({"id": usuario.id, "nombre": usuario.nombre, "edad": usuario.edad})
    return jsonify({"mensaje": "Usuario no encontrado"}), 404

@app.route('/eliminar_usuario/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    usuario = Usuario.query.get(id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"mensaje": "Usuario eliminado"})
    return jsonify({"mensaje": "Usuario no encontrado"}), 404

from sqlalchemy import text

@app.route('/test_db')
def test_db():
    try:
        # Ejecutar la consulta correctamente usando 'text'
        resultado = db.session.execute(text("SELECT 1")).fetchall()
        return jsonify({"mensaje": "Conexión exitosa a la base de datos"}) if resultado else jsonify({"mensaje": "Conexión fallida"}), 500
    except Exception as e:
        return jsonify({"mensaje": f"Error al conectar a la base de datos: {str(e)}"}), 500

# ==========================
# Creación de la base de datos
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f"Error al crear la base de datos: {e}")

if __name__ == '__main__':
    app.run(debug=True)