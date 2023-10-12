from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1D8DE81DJ7nMtgny!'
app.config['MYSQL_DB'] = 'readthings_sql'

mysql = MySQL(app)

@app.route('/')
def inicio():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		return redirect(url_for('home'))

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'correo' in request.form and 'contrasenia' in request.form:
		nombreusuario = request.form['username']
		contrasenia = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM usuario WHERE username = % s AND contrasenia = % s', (nombreusuario, contrasenia, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['idUsuario'] = account['id']
			session['nombreusuario'] = account['username']
			session['correo'] = account['correo']
			if(account['privilegio'] == 2):
				session['admin'] = True
			return redirect(url_for('home', msg=msg))
		else:
			msg = 'Nombre o contraseña incorrectos !'
	return render_template('login.html', msg = msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST':
		nombre = request.form['firstname']
		apellido = request.form['lastname']
		nombreusuario = request.form['username']
		correo = request.form['mail']
		contrasenia = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM usuario WHERE correo = % s', (correo, ))
		account = cursor.fetchone()
		if account:
			msg = 'Este correo ya esta registrado !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', correo):
			msg = 'Correo invalido !'
		elif not re.match(r'[A-Za-z0-9]+', nombreusuario):
			msg = 'El nombre de usuario solo debe contener letras y numeros !'
		elif not re.match(r'[A-Za-z]+', nombre) or not re.match(r'[A-Za-z]+',apellido):
			msg = 'El nombre y/o apellido solo debe contener letras !'
		else:
			cursor.execute('INSERT INTO usuario (nombre, apellido, username, correo, contrasenia) VALUES (% s, % s, % s, % s, % s)', (nombre, apellido, nombreusuario, correo, contrasenia))
			mysql.connection.commit()
			msg = 'Registro exitoso !'
	return render_template('register.html', msg = msg)

@app.route('/home', methods = ['GET', 'POST'])
def menu():
	if 'loggedin' not in session:
		return redirect(url_for('login', msg = 'Primero inicia sesion!'))
	else:
		return render_template('menu.html')

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('idusuario', None)
	session.pop('nombreusuario', None)
	session.pop('correo', None)
	session.pop('admin', None)
	return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)