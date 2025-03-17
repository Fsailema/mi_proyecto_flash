from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Crear la instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de la URI de conexión a la base de datos MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://favi:Favio@localhost/desarrollo_web'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy con la aplicación Flask
db = SQLAlchemy(app)

# Crear una tabla en MySQL
class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    mail = db.Column(db.String(100), nullable=False)

    def __init__(self, nombre, mail):
        self.nombre = nombre
        self.mail = mail

    def __repr__(self):
        return f'<Usuario {self.nombre}>'

# Función para crear la base de datos (si no existe)
def crear_base_de_datos():
    db.create_all()  # Crear las tablas en la base de datos si no existen

if __name__ == '__main__':
    with app.app_context():
        crear_base_de_datos()  # Crea las tablas cuando se inicia la aplicación
    app.run(debug=True)