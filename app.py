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
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
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
	if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form and 'username' in request.form and 'mail' in request.form and 'password' in request.form:
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
			cursor.execute('INSERT INTO usuario (nombre, apellido, username, correo, contrasenia) VALUES (% s, % s, % s, % s, % s)', (nombre, apellido, nombreusuario, correo, contrasenia, ))
			mysql.connection.commit()
			msg = 'Registro exitoso !'
	return render_template('register.html', msg = msg)

#Funciones usuario admin
@app.route('/homeadmin', methods = ['GET', 'POST'])
def homeadmin():
	if 'loggedin' not in session and 'admin' not in session:
		return redirect(url_for('login'))
	else:
		

#Funciones usuario comun
@app.route('/home', methods = ['GET', 'POST'])
def home():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		#cursor.execute('SELECT (titulo, autor, genero, fecha_publicacion, precio) FROM articulo WHERE genero = (SELECT genero FROM articulo WHERE codigo = (SELECT no_articulo FROM venta WHERE no_cliente = % s LIMIT 1) and cantidad <> 0)', (session['idUsuario'], ))
		cursor.execute('SELECT codigo, titulo, autor, genero, fecha_publicacion, precio_unitario FROM articulo WHERE cantidad > 0')
		home_data = cursor.fetchall()
		return render_template('home.html', recomendaciones = home_data)
	
@app.route('/profile', methods = ['GET', 'POST'])
def profile():
	msg = ''
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		if request.method == 'POST' and 'nombre' in request.form and 'apellido' in request.form and 'correo' in request.form and 'nombreusuario' in request.form and 'contrasenia1' in request.form and 'contrasenia2' in request.form:
			nombre = request.form['nombre']
			apellido = request.form['apellido']
			correo = request.form['correo']
			nombreusuario = request.form['nombreusuario']
			contrasenia1 = request.form['contrasenia1']
			contrasenia2 = request.form['contrasenia2']
			idActual = session['idUsuario']
			
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT * FROM usuario WHERE username = % s and id <> % s', (nombreusuario, idActual, ))
			account1 = cursor.fetchone()
			cursor.execute('SELECT * FROM usuario WHERE nombre = % s and apellido = % s and id <> % s', (nombre, apellido, idActual, ))
			account2 = cursor.fetchone()
			cursor.execute('SELECT * FROM usuario WHERE correo = % s and id <> % s', (correo, idActual, ))
			account3 = cursor.fetchone()
			if account1:
				msg = 'Este nombre de usuario ya existe !'
			elif account2:
				msg = 'Nombre y Apellidos ya existentes !'
			elif account3:
				msg = 'Correo ya existente !'
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', correo):
				msg = 'Correo invalido !'
			elif not re.match(r'[A-Za-z0-9]+', nombreusuario):
				msg = 'El nombre de usuario solo debe contener letras y numeros !'
			elif not re.match(r'[A-Za-z0-9]+', nombre):
				msg = 'El nombre solo debe contener letras !'
			elif not nombre or not apellido or not nombreusuario or not correo or not contrasenia1 or not contrasenia2:
				msg = 'Por favor llene el formulario !'
			elif contrasenia1 != contrasenia2:
				msg = 'Contraseñas no coinciden !'
			else:
				cursor.execute('UPDATE usuario SET nombre = % s, apellido = % s, correo = % s, username = % s, contrasenia = % s WHERE id = % s', (nombre, apellido, correo, nombreusuario, contrasenia1, idActual, ))
				mysql.connection.commit()
				session['nombre'] = nombre
				session['apellido'] = apellido
				session['correo'] = correo
				session['nombreusuario'] = nombreusuario
		elif request.method == 'POST':
			msg = 'No ha puesto nada para cambiar !'
		return render_template('profile.html', msg = msg)
	
@app.route('/orders', methods = ['GET', 'POST'])
def orders():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE no_usuario = % s', (str(session['idUsuario'])))
		order_data = cursor.fetchall()
		return render_template('orders.html', ventas = order_data)
	
@app.route('/search', methods = ['GET', 'POST'])
def search():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		return render_template('search.html')
		
@app.route('/searching', methods = ['POST'])
def searching():
	if request.method == 'POST' and 'Searchbar' in request.form and 'search_for' in request.form:
		value = request.form['Searchbar']
		parameter = request.form['search_for']
		print(parameter)
		print(value)
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		if parameter == 'titulo':
			cursor.execute('SELECT titulo, autor, genero, fecha_publicacion, precio_unitario, codigo FROM articulo WHERE titulo = % s and cantidad > 0', (value, ))
		elif parameter == 'autor':
			cursor.execute('SELECT titulo, autor, genero, fecha_publicacion, precio_unitario, codigo FROM articulo WHERE autor = % s and cantidad > 0', (value, ))
		elif parameter == 'genero':
			cursor.execute('SELECT titulo, autor, genero, fecha_publicacion, precio_unitario, codigo FROM articulo WHERE genero = % s and cantidad > 0', (value, ))
		elif parameter == 'codigo':
			cursor.execute('SELECT titulo, autor, genero, fecha_publicacion, precio_unitario, codigo FROM articulo WHERE codigo = % s and cantidad > 0', (value, ))
		search_data = cursor.fetchall()
		return render_template('search.html', busqueda = search_data)

@app.route('/book/<book_id>', methods = ['GET', 'POST'])
def book(book_id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT titulo, autor, genero, fecha_publicacion, fecha_ingreso, precio_unitario, cantidad, codigo FROM articulo WHERE codigo = % s', (book_id, ))
	book_data = cursor.fetchone()
	if book_data:
		if book_data['cantidad'] <= 0:
			return redirect(url_for('inicio'))
		else:
			session['bookCantidad'] = book_data['cantidad']
			session['bookId'] = book_data['codigo']
			print(session['bookCantidad'])
			print(session['bookId'])
	return render_template('book.html', info = book_data)

@app.route('/payment', methods = ['GET', 'POST'])
def payment():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	elif request.method == "POST" and 'Cantidad' in request.form and "metodo_pago" in request.form and "tipo_envio" in request.form:
		cantidad = request.form['Cantidad']
		metodo_pago = request.form['metodo_pago']
		envio = request.form['tipo_envio']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cantidad_t = session.get('bookCantidad')
		book_id = session.get('bookId')
		if(int(cantidad) > cantidad_t):
			diferencia = cantidad_t - int(cantidad)
			cursor.execute('INSERT INTO venta (no_usuario, no_articulo, cantidad, metodo_pago, envio, estado_envio) VALUES (% s, % s, % s, % s, % s, % s)',(str(session['idUsuario']), book_id, cantidad_t, metodo_pago, envio, 'LISTO PARA LLEGAR', ))
			mysql.connection.commit()
			cursor.execute('INSERT INTO venta (no_usuario, no_articulo, cantidad, metodo_pago, envio) VALUES (% s, % s, % s, % s, % s)',(str(session['idUsuario']), book_id, abs(diferencia), metodo_pago, envio, ))
			mysql.connection.commit()
			cursor.execute('UPDATE articulo SET cantidad = % s WHERE codigo = % s', (0, book_id, ))
		elif cantidad_t == 0:
			cursor.execute('INSERT INTO venta (no_usuario, no_articulo, cantidad, metodo_pago, envio) VALUES (% s, % s, % s, % s, % s)',(str(session['idUsuario']), book_id, abs(diferencia), metodo_pago, envio, ))
		else:
			diferencia = cantidad_t - int(cantidad)
			cursor.execute('INSERT INTO venta (no_usuario, no_articulo, cantidad, metodo_pago, envio, estado_envio) VALUES (% s, % s, % s, % s, % s, % s)',(str(session['idUsuario']), book_id, int(cantidad), metodo_pago, envio, 'LISTO PARA LLEGAR', ))
			mysql.connection.commit()
			cursor.execute('UPDATE articulo SET cantidad = % s WHERE codigo = % s', (diferencia, book_id, ))
		mysql.connection.commit()
	return redirect(url_for('orders'))

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