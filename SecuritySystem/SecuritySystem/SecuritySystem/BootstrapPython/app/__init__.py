from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_socketio import SocketIO
from datetime import timedelta  # Importar para configurar la duración de la sesión

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['BOOTSTRAP_SERVE_LOCAL'] = True

# Agregar clave secreta para manejar sesiones
app.config['SECRET_KEY'] = '9c744494bd8541f664281fdd8071c358'  # Reemplaza 'your_secret_key_here' por una clave segura
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=2)  # Establecer la duración de la sesión

bootstrap = Bootstrap5(app)
socketio = SocketIO(app)  # Inicializa SocketIO y lo asocia con la aplicación Flask

from app import routes  # Asegúrate de importar las rutas al final
