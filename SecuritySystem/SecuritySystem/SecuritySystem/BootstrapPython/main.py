from app import app, socketio  # Importa app y socketio desde __init__.py
from database.databasecontrol import initialize_database

if __name__ == '__main__':
    
    initialize_database()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
