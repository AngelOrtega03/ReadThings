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
			session['nombre'] = account['nombre']
			session['apellido'] = account['apellido']
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


#Funciones usuario comun
@app.route('/home', methods = ['GET', 'POST'])
def home():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		if 'admin' in session:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT codigo, titulo, autor, genero, fecha_publicacion, precio_unitario FROM articulo')
			home_data = cursor.fetchall()
			return render_template('homeadmin.html', titulos = home_data)
		else:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT titulo, autor, genero, fecha_publicacion, precio_unitario FROM articulo WHERE genero = (SELECT genero FROM articulo WHERE codigo = (SELECT no_articulo FROM venta WHERE no_usuario = % s LIMIT 1) and cantidad <> 0 LIMIT 1)', (session['idUsuario'], ))
			prueba = cursor.fetchall()
			cursor.execute('SELECT codigo, titulo, autor, genero, fecha_publicacion, precio_unitario FROM articulo WHERE cantidad > 0')
			home_data = cursor.fetchall()
			if prueba:
				home_data = prueba
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
		if 'admin' in session:
			return render_template('profileadmin.html', msg = msg)
		else:
			return render_template('profile.html', msg = msg)
	
@app.route('/orders', methods = ['GET', 'POST'])
def orders():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		if 'admin' in session:
			if request.method == 'POST' and 'Searchbar' in request.form and 'search_for' in request.form:
				value = request.form['Searchbar']
				parameter = request.form['search_for']
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				if parameter == 'no_venta':
					cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE no_venta = % s ORDER BY no_venta DESC', (value, ))
				elif parameter == 'titulo':
					cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE titulo = % s ORDER BY no_venta DESC', (value, ))
				elif parameter == 'fecha_venta':
					cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE fecha_venta = % s ORDER BY no_venta DESC', (value, ))
				elif parameter == 'metodo_pago':
					cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE metodo_pago = % s ORDER BY no_venta DESC', (value, ))
				elif parameter == 'no_usuario':
					cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE no_usuario = % s ORDER BY no_venta DESC', (value, ))
				elif parameter == 'estado_envio':
					cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE estado_envio = % s ORDER BY no_venta DESC', (value, ))
				search_data = cursor.fetchall()
				return render_template('ordersadmin.html', ventas = search_data)
			else:
				return render_template('ordersadmin.html')
		else:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT no_venta, titulo, fecha_venta, cantidad, total, metodo_pago, envio, estado_envio FROM ventaarticulo WHERE no_usuario = % s ORDER BY no_venta DESC', (str(session['idUsuario'])))
			order_data = cursor.fetchall()
			return render_template('orders.html', ventas = order_data)
	
@app.route('/search', methods = ['GET', 'POST'])
def search():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		if 'admin' in session:
			return render_template('searchadmin.html')
		else:
			return render_template('search.html')

@app.route('/paymentadmin', methods = ['GET', 'POST'])
def paymentadmin(msg = ''):
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		if 'admin' in session:
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('SELECT titulo, codigo FROM articulo')
			articulos_nombre = cursor.fetchall()
			cursor.execute('SELECT no_compra, no_articulo, nombre_articulo, cantidad, nombre_proveedor, fecha_compra FROM proveedorcompras')
			compras = cursor.fetchall()
			return render_template('paymentsadmin.html', msg = msg, articulos_nombre = articulos_nombre, compras = compras)
		else:
			return redirect(url_for('inicio'))

@app.route('/paymentproduct', methods = ['GET', 'POST'])
def paymentproduct():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	elif 'admin' in session and request.method == 'POST' and 'book_name' in request.form and 'provider' in request.form and 'quantity' in request.form:
		msg = ''
		book_name = request.form['book_name']
		provider = request.form['provider']
		quantity = request.form['quantity']
		print(book_name)
		print(provider)
		print(quantity)
		print('Hola')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT codigo, cantidad FROM articulo WHERE titulo = % s', (book_name, ))
		book_id = cursor.fetchone()
		print(book_id)
		cantidadtotal = int(book_id['cantidad']) + int(quantity)
		print(cantidadtotal)
		cursor.execute('INSERT INTO comprasaproveedor (no_articulo, no_proveedor, cantidad) VALUES (% s, % s, % s)', (book_id['codigo'], provider, quantity, ))
		mysql.connection.commit()
		cursor.execute('UPDATE articulo SET cantidad = % s WHERE codigo = % s', (cantidadtotal, book_id['codigo'], ))
		mysql.connection.commit()
		msg = 'Compra realizada !'
	return redirect(url_for('paymentadmin', msg = msg))
		
@app.route('/registerproduct', methods = ['GET', 'POST'])
def registerproduct():
	if 'loggedin' not in session:
		return redirect(url_for('login'))
	else:
		if 'admin' in session:
			msg = ''
			if request.method == 'POST' and 'isbn' in request.form and 'book_name_1' in request.form and 'autor' in request.form and 'genero' in request.form and 'fecha_publicacion' in request.form and 'precio_unitario' in request.form:
				isbn = request.form['isbn']
				book_name = request.form['book_name_1']
				autor = request.form['autor']
				genero = request.form['genero']
				fecha_publicacion = request.form['fecha_publicacion']
				precio = request.form['precio_unitario']
				cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute('SELECT * FROM articulo WHERE codigo = % s', (isbn, ))
				account1 = cursor.fetchone()
				cursor.execute('SELECT * FROM articulo WHERE titulo = % s', (book_name, ))
				account2 = cursor.fetchone()
				if account1:
					msg = 'ISBN ya existente !'
				elif account2:
					msg = 'Nombre ya existente !'
				else:
					cursor.execute('INSERT INTO articulo (codigo, titulo, autor, genero, fecha_publicacion, precio_unitario) VALUES (% s, % s, % s, % s, % s, % s)', (isbn, book_name, autor, genero, fecha_publicacion, precio, ))
					mysql.connection.commit()
					msg = 'Producto registrado exitosamente !'
			return redirect(url_for('paymentadmin', msg = msg))

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
		if 'admin' in session:
			return render_template('searchadmin.html', busqueda = search_data)
		else:
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
	if 'admin' in session:
		return render_template('bookadmin.html', info = book_data)
	else:
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
	session.pop('nombre', None)
	session.pop('apellido', None)
	session.pop('correo', None)
	session.pop('admin', None)
	return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)