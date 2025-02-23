from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Definir el formulario
class ContactForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    mensaje = StringField('Mensaje', validators=[DataRequired()])
    enviar = SubmitField('Enviar')

# Ruta para mostrar y procesar el formulario
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    form = ContactForm()
    if form.validate_on_submit():
        nombre = form.nombre.data
        email = form.email.data
        mensaje = form.mensaje.data
        flash('Formulario enviado con éxito', 'success')
        return render_template('resultado.html', nombre=nombre, email=email, mensaje=mensaje)
    return render_template('formulario.html', form=form)

# Ruta de inicio
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)