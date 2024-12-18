from flask import Flask, render_template
from db_config import init_app

app = Flask(__name__)
mysql = init_app(app)  # Inicializa MySQL con la app Flask

@app.route('/')
def index():
    # Obtén datos de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM cliente')
    data = cur.fetchall()
    cur.close()
    
    return render_template('index.html', datos=data)

if __name__ == '__main__':
    app.run(debug=True)
