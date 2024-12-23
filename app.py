from flask import Flask, render_template, request, flash, redirect, url_for,jsonify
from db_config import init_app
from flask import Flask, render_template, request, session, flash, redirect, url_for
from db_config import init_app

app = Flask(__name__)
app.secret_key = 'tu_secreto_para_flash'
mysql = init_app(app)

# Ruta principal (Página de inicio)
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/producto/<int:idproducto>', methods=['GET'])
def obtener_producto(idproducto):
    cur = mysql.connection.cursor()
    cur.execute("SELECT idproducto, nombre, descripcion, precio, stock FROM producto WHERE idproducto = %s", (idproducto,))
    producto = cur.fetchone()
    cur.close()

    if producto:
        return jsonify({
            'idproducto': producto[0],
            'nombre': producto[1],
            'descripcion': producto[2],
            'precio': producto[3],
            'stock': producto[4]
        })
    else:
        return jsonify({'error': 'Producto no encontrado'}), 404





@app.route('/pedido', methods=['GET', 'POST'])
def pedido():
    # Recuperar productos y servicios
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM producto WHERE stock > 0")
    productos = cur.fetchall()

    cur.execute("SELECT * FROM servicio")
    servicios = cur.fetchall()

    # Si se ha enviado el formulario para actualizar el carrito
    if request.method == 'POST':
        carrito = session.get('carrito', [])

        # Agregar productos seleccionados al carrito
        productos_seleccionados = request.form.getlist('productos')
        for producto_id in productos_seleccionados:
            # Evitar agregar productos duplicados al carrito
            if producto_id not in carrito:
                carrito.append(producto_id)

        # Guardar carrito actualizado en la sesión
        session['carrito'] = carrito

        # Actualizar información del carrito en la interfaz
        flash(f'Se han agregado {len(productos_seleccionados)} productos al carrito', 'success')

    cur.close()
    return render_template('pedido.html', productos=productos, servicios=servicios)


@app.route('/ver_carrito', methods=['GET'])
def ver_carrito():
    carrito = session.get('carrito', [])
    productos_seleccionados = []
    
    # Si hay productos en el carrito, los recuperamos
    if carrito:
        cur = mysql.connection.cursor()
        for producto_id in carrito:
            cur.execute("SELECT * FROM producto WHERE idproducto = %s", (producto_id,))
            producto = cur.fetchone()
            productos_seleccionados.append(producto)
        cur.close()

    return render_template('carrito.html', productos=productos_seleccionados)


@app.route('/crear_pedido', methods=['POST'])
def crear_pedido():
    # Crear pedido usando los productos en el carrito
    carrito = session.get('carrito', [])
    productos_seleccionados = []

    if not carrito:
        flash('El carrito está vacío', 'danger')
        return redirect('/pedido')

    try:
        cur = mysql.connection.cursor()
        # Crear el pedido en la base de datos
        cur.execute("INSERT INTO pedido (fecha) VALUES (NOW())")
        pedido_id = cur.lastrowid

        # Insertar los productos en el pedido
        for producto_id in carrito:
            cur.execute("SELECT precio FROM producto WHERE idproducto = %s", (producto_id,))
            precio = cur.fetchone()['precio']
            cantidad = 1  # Por ahora, supondremos que cada producto tiene una cantidad de 1
            subtotal = precio * cantidad

            cur.execute(
                "INSERT INTO detalle_pedido_producto (idpedido, idproducto, cantidad, subtotal) VALUES (%s, %s, %s, %s)",
                (pedido_id, producto_id, cantidad, subtotal)
            )

        # Guardar cambios
        mysql.connection.commit()
        flash('Pedido creado exitosamente', 'success')

    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al crear el pedido: {e}', 'danger')

    finally:
        cur.close()
    
    # Limpiar el carrito después de la compra
    session.pop('carrito', None)
    
    return redirect('/pedido')



#comentarios 

@app.route('/guardar_comentario', methods=['POST'])
def guardar_comentario():
    # Obtener los datos del formulario
    nombre = request.form.get('name')
    correo = request.form.get('email')
    mensaje = request.form.get('message')

    if not (nombre and correo and mensaje):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    # Conexión a la base de datos
    conn = mysql.connection
    if not conn:
        return jsonify({'error': 'Error al conectar a la base de datos'}), 500

    try:
        cursor = conn.cursor()
        query = "INSERT INTO comentario (apenomb, correo, comentario) VALUES (%s, %s, %s)"
        cursor.execute(query, (nombre, correo, mensaje))
        conn.commit()
        return jsonify({'message': 'Comentario guardado exitosamente'}), 200
    except Exception as e:
        print(f"Error al insertar en la base de datos: {e}")
        return jsonify({'error': 'Error al guardar el comentario'}), 500
    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(debug=True)
