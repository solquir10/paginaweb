from flask_mysqldb import MySQL

mysql = None

def init_app(app):
   
    global mysql
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = ''
    app.config['MYSQL_DB'] = 'repuestera'
    
    mysql = MySQL(app)
    return mysql

