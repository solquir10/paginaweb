from flask import Flask, render_template, request, redirect, flash, url_for
from db_config import init_app
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'tu_secreto_para_flash'
mysql = init_app(app)

# Ruta principal
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM cliente')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', datos=data)

# Ruta para el formulario de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('registro'))

        # Verificar si el correo ya está registrado
        try:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM usuario WHERE correo = %s", (email,))
            existing_user = cur.fetchone()
            if existing_user:
                flash('El correo electrónico ya está registrado. Por favor, usa otro.', 'danger')
                return redirect(url_for('registro'))

            # Encriptar la contraseña
            hashed_password = generate_password_hash(password)

            # Insertar el nuevo usuario
            query = "INSERT INTO usuario (usuario, correo, clave) VALUES (%s, %s, %s)"
            cur.execute(query, (username, email, hashed_password))
            mysql.connection.commit()
            flash('Usuario registrado exitosamente. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f'Error al registrar el usuario: {e}', 'danger')
        finally:
            cur.close()

    return render_template('registro.html')

# Ruta para iniciar sesión (puedes implementarla después)
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
