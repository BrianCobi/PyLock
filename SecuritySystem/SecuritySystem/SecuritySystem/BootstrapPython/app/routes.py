from flask import render_template, request, redirect, url_for, session, flash,  send_file
from app import app, socketio
from database.databasecontrol import *
from datetime import datetime
# from DoorControl import *
import csv
import io
# routes.py
import os
from collections import defaultdict


# Clave dura para la autenticación
ADMIN_USERNAME = 'vbs'
ADMIN_PASSWORD = 'vbsinc1'

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Obtener el estado actual de la puerta
    x = get_setting_by_id(1)
    door_state = {
        "lock_state": x[3]
    }

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error, door_state=door_state)
    
    return render_template('login.html', door_state=door_state)



IMAGE_FOLDER = 'app/static/images/'

@app.route('/imageviewer')
def imageviewer():
    # Crear un diccionario para agrupar las imágenes por fecha
    images_by_date = defaultdict(list)

    # Listar las imágenes en el directorio
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.endswith(".jpg") or filename.endswith(".png"):  # Solo incluir imágenes
            # Extraer la parte de la fecha del nombre del archivo (por ejemplo, 20241007)
            date_str = filename.split('_')[1]
            # Convertir la fecha a un objeto datetime para facilitar la ordenación
            date = datetime.strptime(date_str, "%Y%m%d")
            # Agregar la imagen a la lista correspondiente a esa fecha
            images_by_date[date].append(filename)
    
    # Ordenar las fechas en orden descendente (más reciente primero)
    sorted_dates = sorted(images_by_date.keys(), reverse=True)
    
    # Pasar las imágenes agrupadas y ordenadas a la plantilla
    return render_template('imageviewer.html', images_by_date=images_by_date, sorted_dates=sorted_dates)



@app.route('/')
@app.route('/index')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    records = get_all_records()
    logs = []
    for record in records:
        Name = record[1] + " "  + record[2]
        Date = record[3]
        access_dict = {
            "name": Name,
            "access_date": Date,
        }
        logs.append(access_dict)
    
    x = get_setting_by_id(1)
    door_state = {
        "lock_state": x[3]
    }
    
    return render_template('index.html', title='Home', door_state=door_state, logs=logs)

@app.route('/check_session')
def check_session():
    if session.get('logged_in'):
        return {'status': 'ok'}, 200
    else:
        return {'status': 'expired'}, 401


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    print("Emitiendo evento reload_page")
    socketio.emit('reload_page')
    return redirect(url_for('login'))


def convert_to_am_pm(time_str):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    time_obj = datetime.strptime(time_str, '%H:%M:%S')
    return time_obj.strftime('%I:%M:%S %p')

def convert_to_24_hour(time_str):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Ajustar el formato según la entrada
    if len(time_str.split(':')) == 2:  # Formato sin segundos
        time_obj = datetime.strptime(time_str, '%I:%M%p')
    elif len(time_str.split(':')) == 3:  # Formato con segundos
        time_obj = datetime.strptime(time_str, '%I:%M:%S %p')
    else:
        raise ValueError("Time data does not match expected format")

    return time_obj.strftime('%H:%M:%S')

@app.get('/enroll_employee')
def enroll_employee():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('enroll.html', title='Enroll Employee')

@app.get('/enrolled')
def enrolled():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    enrolled_employees = []
    employees = get_all_employees()
    # print(employees)
    for emp in employees:
        print(emp)
        name = f"{emp[1]} {emp[2]}"
        # accesstype = emp[4]
        # print(accesstype)
        access_dict = {
            "name": name,
            "general_access": emp[4] == 1,
            "weekend_access": emp[5] == 1,
            "after_hours_access": emp[6] == 1,
        }
        enrolled_employees.append(access_dict)
    return render_template('enrolled.html', title='Enrolled', enrolled_employees=enrolled_employees)

@app.get('/settings')
def settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    print("Check")
    settings = get_setting_by_id(1)
    # print(settings)
    time_12hr_format = convert_to_am_pm(settings[1])
    setting = {
        "lockdown_time": time_12hr_format,
        "maindoorsecs": settings[2]
    }
    # print(time_12hr_format())
    return render_template('settings.html', title='Settings', setting = setting)

@app.post('/settings')
def update_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    settings = request.get_json()
    # print(settings)
    time = convert_to_24_hour(settings['lockdown_time'])
    update_setting_database(1, time, settings['maindoorsecs'])

    return {}

@app.post('/door_state')
def update_doorstate():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    door_state = request.get_json()
    print(door_state['state'])
    socketio.emit('reload_page')
    print(f"Setting database state to {door_state['state']} ")
    if door_state['state'] == 'unlocked':
        update_setting_database(setting_id=1, is_active=0)
    else:
        update_setting_database(setting_id=1, is_active=1)
        
    return {}

@app.post('/add_employee')
def add_employee():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    employee = request.get_json()
    employeeName = employee['name'].lstrip()
    employeeName = employeeName.rstrip()
    print(employeeName)
    Name =  employeeName.split(" ")
    First = Name[0]
    Last = Name[1] if len(Name)>1 else " "
    print(f"Adding employee: Firstname={First}, Lastname={Last}, LastFour={employee['lastfour']}, GeneralAccess={1}, Weekends={0}, AfterHours={0}")
    add_employee_to_database(First, Last, employee['lastfour'], 1, 0, 0)

    return {}

@app.post('/update_employee')
def update_employee():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    employee = request.get_json()
    Name = employee['name'].split(" ")
    First = Name[0]
    Last = Name[1] if len(Name) > 1 else ""
    response = employee_exists(First, Last)
    print(response)
    print(employee)
    if response:
        print('Updating')
        update_employee_by_name(First, Last,general_access=employee['general_access'], weekends=employee['weekend_access'], after_hours=employee['after_hours_access'])
    return {}
    # print(Controlling system)

@app.delete('/delete_employee')
def delete_employee():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    employee = request.get_json()
    Name = employee['name'].split(" ")
    First = Name[0]
    Last = Name[1] if len(Name) > 1 else ""
    response = delete_employee_by_name(First, Last)
    # print(employee['name'] + " was deleted.")
    return {"message": response}

@app.post('/trigger_reload')
def trigger_reload():
    # if not session.get('logged_in'):
    #     return redirect(url_for('login'))
    print("Emitiendo evento reload_page")
    socketio.emit('reload_page')
    return {}, 200



@app.route('/download_logs')
def download_logs():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    records = get_all_records_database()

    # Crear un archivo CSV en memoria usando StringIO en lugar de BytesIO para manejar cadenas de texto
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Employee Name', 'Access Date Time'])  # Header
    
    for record in records:
        name = f"{record[1]} {record[2]}"
        date = record[3]
        writer.writerow([name, date])
    
    # Convertir el contenido a bytes para poder usar send_file
    output.seek(0)
    response = io.BytesIO(output.getvalue().encode('utf-8'))

    # Enviar el archivo CSV como respuesta
    return send_file(response, mimetype='text/csv', as_attachment=True, download_name='logs.csv')
    # return {}, 200
