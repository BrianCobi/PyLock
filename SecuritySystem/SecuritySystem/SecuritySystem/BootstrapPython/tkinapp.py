import tkinter as tk
import time
from math import sin, cos, pi
import threading
from database.databasecontrol import *
from DoorControl import *
from datetime import datetime
import requests
import subprocess
import socket

class SynchronizedSpinner(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.dots = []
        self.num_dots = 12
        self.radius = 50
        self.min_size = 10
        self.max_size = 20
        self.angular_speed = 2 * pi / 2  # Una rotación completa cada 2 segundos
        self.size_wave_speed = 2 * pi / 2  # Un ciclo completo de cambio de tamaño cada 2 segundos

        self.dot_angles = []
        for i in range(self.num_dots):
            angle = 2 * pi * i / self.num_dots
            self.dot_angles.append(angle)
            dot = self.create_oval(0, 0, self.min_size, self.min_size, fill='gray')
            self.dots.append(dot)

        self.update_animation()

    def update_animation(self):
        current_time = time.time()
        for i in range(self.num_dots):
            angle = self.dot_angles[i]
            x = self.winfo_width() / 2 + self.radius * cos(angle)
            y = self.winfo_height() / 2 + self.radius * sin(angle)

            # Tamaño - la onda de cambio de tamaño se propaga alrededor
            size_wave = sin(angle - self.size_wave_speed * current_time)
            size = self.min_size + (self.max_size - self.min_size) * (1 + size_wave) / 2

            self.coords(self.dots[i], x - size / 2, y - size / 2, x + size / 2, y + size / 2)

        self.after(16, self.update_animation)  # ~60 FPS
class VirtualKeyboard(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_keyboard()

    def create_keyboard(self):
        keys = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Clear', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<---']  # Añadido el botón de retroceso
        ]

        for y, row in enumerate(keys):
            for x, key in enumerate(row):
                # Ajustar el tamaño de los botones para que sean más pequeños y definir la fuente
                if key == '<---':
                    button = tk.Button(self, text=key, font=('Arial', 20),
                                        bg='#c44141',  # Background color
                                        fg='white',  # Foreground (text) color
                                        relief='raised',  # Button border style
                                        bd=3, # Border width command=self.show_spinner)
                                        activebackground='white',  # Background color when the button is active (pressed) 
                                        width=4, height=2, command=self.on_backspace)
                elif key == 'Clear':
                    button = tk.Button(self, text=key,  
                                        font=('Arial', 20), 
                                        bg='#c44141',  # Background color
                                        fg='white',  # Foreground (text) color
                                        relief='raised',  # Button border style
                                        bd=3, # Border width command=self.show_spinner)
                                        activebackground='white',  # Background color when the button is active (pressed)
                                        width=4, height=2, command=self.on_clear)
                else:
                    button = tk.Button(self, 
                                        text=key, 
                                        font=('Arial', 20), 
                                        bg='black',  # Background color
                                        fg='white',  # Foreground (text) color
                                        # padx=10,  # Horizontal padding
                                        # pady=5,  # Vertical padding
                                        relief='raised',  # Button border style
                                        bd=3, # Border width command=self.show_spinner)
                                        activebackground='white',  # Background color when the button is active (pressed)
                                        # activeforeground='white'  # Foreground color when the button is active (pressed)
                                        width=4, height=2, command=lambda k=key: self.on_key_press(k))
                button.grid(row=y, column=x, padx=1, pady=1)

    def on_key_press(self, key):
        app.text_input.insert(tk.END, key)

    def on_backspace(self):
        # Elimina el último carácter en el TextInput
        current_text = app.text_input.get()
        app.text_input.delete(len(current_text) - 1, tk.END)

    def on_clear(self):
        # Borra todo el texto del TextInput
        app.text_input.delete(0, tk.END)

class MyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VBS PyLock")
        self.geometry("1024x600")
        # self.configure(bg='red')  # Set the background color of the entire application
        self.attributes('-fullscreen',True)

        self.layout = tk.Frame(self)
        self.layout.pack(expand=True, fill='both')
        self.keyboard = VirtualKeyboard(self)
        self.bind('<Shift-Alt-Key-question>', self.open_terminal)        # self.layout.configure(bg='black')  # Set the background color of the layout frame


        GPIOinitialization()
        self.icon_image = tk.PhotoImage(file='test1.png').subsample(7, 7)
        self.pylock_label = tk.Label(self.layout, text="", font=('Courier New', 40), fg='black')
        self.pylock_label.place(relx=0.5, rely=0.1, anchor='center')
        self.message_label = tk.Label(self.layout, text="Open doors\nSystem inactive", font=('Arial', 80, 'bold'), fg='black')
        self.text_input = tk.Entry(self.layout, font=('Arial', 48), show='*', justify='center', bg='#f0f0f0',
                                   fg='black', bd=3, relief='sunken', highlightthickness=2, 
                                   highlightbackground='gray', highlightcolor='black')
        self.enter_button = tk.Button(self.layout, text='Enter', font=('Arial', 20), bg='black', fg='white',
                                      padx=10, pady=5, relief='raised', bd=5, command=self.show_spinner)
        threading.Thread(target=self.animate_text, daemon=True).start()

        self.button_monitor_active = False  # Bandera para controlar el hilo de monitoreo
        self.button_monitor_thread = None  # Referencia al hilo

        self.previous_state = None  # Para almacenar el estado previo
        self.previous_timeclose = None
        self.onlyonce = True
        TurnOnBackup()
        self.check_lockdown()  # Inicializa la verificación periódica

    def open_terminal(self, event):
        # Lanza la terminal (por ejemplo, gnome-terminal)
                # Comando para matar la aplicación
        command = "pkill -f tkinapp.py"
        
        # Lanza la terminal con el comando preescrito y esperando para ejecutarse
        subprocess.Popen(['qterminal', '-e', f'bash -c "echo \'{command}\'; exec bash"'])

    def check_lockdown(self):
        # print("Verificando")
        timeclose = self.checklockdowntime()
        state = get_setting_by_id(1)
        Management = state[3]
        LockControl = False
        LockControl = True if Management else False
        
        if timeclose and self.onlyonce:

            LockControl = True
            update_setting_database(setting_id=1, is_active=1)
            self.onlyonce = False
            print("Setting up onlyonce to True")
            response = requests.post('http://localhost:5000/trigger_reload')
            requests.post(f'http://192.168.2.1:5000/trigger_reload')
            # response = requests.post('http://192.168.2.2:5000/trigger_reload')


        # now = datetime.now()
        # if now.hour == 0 and now.minute == 0:
        #     self.onlyonce = True
        if timeclose == False:
            self.onlyonce = True


        if LockControl != self.previous_state:
            if LockControl:
                print("Changing to locked state")
                LockAll()
                self.start_lockdown_mode()
            else:
                print("Changing to unlocked state")
                unlookAll()
                self.unlocksystem()
            
            # Actualizar los estados previos
            self.previous_state = LockControl

        # Verifica nuevamente cada minuto (60000 ms)
        self.after(1000, self.check_lockdown)

    def checklockdowntime(self):
        settings = get_setting_by_id(1)
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        # Obtener la hora y los minutos del tiempo de lock desde settings
        lock_hour = int(settings[1][0:2])
        lock_minute = int(settings[1][3:5])
        # Comparar hora y minutos
        past_locktime = (current_hour > lock_hour) or (current_hour == lock_hour and current_minute >= lock_minute)
        return past_locktime

    def unlocksystem(self):
        # Si aún no es la hora de bloqueo o ya pasó la medianoche, mostrar "Working hours"
        self.message_label.place(relx=0.5, rely=0.5, anchor='center')
        self.text_input.place_forget()
        self.enter_button.place_forget()
        self.keyboard.place_forget()
        self.focus_set()
        # Detener el hilo de monitoreo si está activo
        if self.button_monitor_active:
            self.button_monitor_active = False
            if self.button_monitor_thread is not None:
                self.button_monitor_thread.join()  # Espera a que el hilo termine
        

    def start_lockdown_mode(self):
        print("Starting system")
        self.message_label.place_forget()  # Oculta el mensaje de "System inactive" si estaba presente
        

        # Inicia el hilo de monitoreo solo si no está activo
        if not self.button_monitor_active:
            self.button_monitor_active = True
            self.button_monitor_thread = threading.Thread(target=self.button_monitor, daemon=True)
            self.button_monitor_thread.start()

        self.text_input.place(relx=0.45, rely=0.3, anchor='center', width=600, height=80)
        self.enter_button.place(relx=0.82, rely=0.3, anchor='center', width=120, height=80)
        self.text_input.bind("<FocusIn>", self.on_focus)

    def button_monitor(self):
        while self.button_monitor_active:
            #buttonmonitor()  # Suponiendo que `buttonmonitor` es una función que monitorea botones
            time.sleep(0.1)  # Intervalo de espera entre chequeos

    def animate_text(self):
        text = "PyLock"
        while True:
            for i in range(len(text) + 1):
                self.pylock_label.config(text=text[:i])
                self.update()
                time.sleep(0.2)

            self.pylock_label.config(image=self.icon_image, compound='right')

            for _ in range(4):
                for size in range(40, 70, 2):
                    self.pylock_label.config(font=('Courier New', size, 'bold'))
                    self.update()
                    time.sleep(0.05)
                for size in range(70, 40, -2):
                    self.pylock_label.config(font=('Courier New', size, 'bold'))
                    self.update()
                    time.sleep(0.05)

            time.sleep(10)

    def on_focus(self, event):
        self.keyboard.place(relx=0.5, rely=0.7, anchor='center')


    def show_spinner(self):


        self.focus_set()
        #Check for valid data entry
        # self.checkaccess()
        employees = get_all_employees()
        print('Cheking employees')
        content = self.text_input.get() 
        EmployeeExist = False
        Access = { "Success":True, "TypeofAccess":"General", "Message":"Hello"}
        for emp in employees:
            name = f"{emp[1][0]}{emp[2][0]}"
            ss = emp[3]
            # print(name+ss)
            code = name+ss
            # print(code)
            if code == content:
                EmployeeExist = True
                content = f"{emp[1]} {emp[2]}"
                now = datetime.now()  # Obtiene la fecha y hora actual                
                past_five_pm = self.checklockdowntime()
                is_weekend = now.weekday in [5, 6]  # 5 es sábado y 6 es domingo
                # now.weekday
                if not is_weekend and not past_five_pm:
                    if emp[4] == 1:
                        print("General Access")
                        Access['Success'] = True
                        Access['TypeofAccess'] = "General"
                        Access['Message'] = f"Welcome, {content}!"
                    else:
                        print("Request Access with Manager")
                        Access['Success'] = False
                        Access['TypeofAccess'] = "General Access"
                        Access['Message'] = f"Please request access\n for {content}"
                elif not is_weekend and past_five_pm:
                    if emp[5] == 1:
                        print("After hours Access")
                        Access['Success'] = True
                        Access['TypeofAccess'] = "After hours"
                        Access['Message'] = f"After hours access:\n Welcome, {content}!"
                    else:
                        print("Request After hour Access with Manager")
                        Access['Success'] = False
                        Access['TypeofAccess'] = "After hours Access"
                        Access['Message'] = f"Please request\n after hours access"
                elif is_weekend:
                    if emp[6] == 1:
                        print("Weekend Access")
                        Access['Success'] = True
                        Access['TypeofAccess'] = "Weekend"
                        Access['Message'] = f"Weekends access:\n Welcome, {content}!"
                    else:
                        print("Request Weekend Access with Manager")
                        Access['Success'] = False
                        Access['TypeofAccess'] = "Weekend Access"
                        Access['Message'] = f"Please request\n weekend access"

        self.text_input.place_forget()
        self.enter_button.place_forget()
        self.keyboard.place_forget()


        # Añade el spinner animado en el lugar del TextInput y botón
        spinner = SynchronizedSpinner(self.layout, width=200, height=200)  # Ajustar el tamaño del spinner
        spinner.place(relx=0.5, rely=0.5, anchor='center')

        # Mostrar el spinner por 5 segundos
        self.after(1000, self.show_welcome_message, spinner, content, EmployeeExist, Access)

    # def checkaccess(self):
    #     # print("Checking access")

    def show_welcome_message(self, spinner, content, EmployeeExist, Access):
        # Elimina el spinner
        spinner.place_forget()

        def sendmessague(First, Last, text):
            messagelabel = tk.Label(self.layout, text=text, font=('Arial', 60, 'bold'))
            messagelabel.place(relx=0.5, rely=0.6, anchor='center')
            now = datetime.now()
            formatted_now = now.strftime('%Y-%m-%d %H:%M:%S')
            datelabel = tk.Label(self.layout, text=formatted_now, font=('Arial', 45))
            datelabel.place(relx=0.5, rely=0.4, anchor='center')
            # if not Last == "failed":
            insert_tracking(First, Last, formatted_now)
            # response = requests.post('http://localhost:5000/trigger_reload')
            #hostname = socket.gethostname()
            #local_ip = socket.gethostbyname(hostname)
            #print(local_ip)
            requests.post(f'http://192.168.2.1:5000/trigger_reload')
                    
            return messagelabel, datelabel

        if EmployeeExist:
            # Muestra el mensaje de bienvenida
            if Access['Success'] == True:
                Name =  content.split(" ")
                First = Name[0]
                Last = Name[1] if len(Name)>1 else " "
                messagelabel, datelabel = sendmessague(First, Last, Access['Message'])
                threading.Thread(target=switchwait, args=(19,5,), daemon=True).start()
            else:
                Name =  content.split(" ")
                First = Name[0]
                Last = Name[1] if len(Name)>1 else " "
                messagelabel, datelabel = sendmessague(First, Last + f" not {Access['TypeofAccess']}", Access['Message'])

        else:
            messagelabel, datelabel = sendmessague("login","failed", "User not recognized!")

        # Mostrar el mensaje de bienvenida por 5 segundos y luego volver al TextInput y botón
        self.after(5000, self.show_input_screen, messagelabel, datelabel)

    def show_input_screen(self, messagelabel,datelabel):
        # Elimina el mensaje de bienvenida
        messagelabel.place_forget()
        datelabel.place_forget()

        # Restablece el TextInput y lo limpia
        self.text_input.delete(0, tk.END)
        self.text_input.place(relx=0.45, rely=0.3, anchor='center', width=400, height=80)

        # Vuelve a mostrar el botón de Enter
        self.enter_button.place(relx=0.72, rely=0.3, anchor='center', width=120, height=80)

        # Restablece el evento de enfoque para que llame nuevamente a on_focus
        self.text_input.unbind("<FocusIn>")
        self.text_input.bind("<FocusIn>", self.on_focus)

if __name__ == '__main__':
    app = MyApp()
    app.mainloop()
