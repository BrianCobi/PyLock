import RPi.GPIO as GPIO  
from time import sleep
import threading


def GPIOinitialization():

    # Configuración inicial
    GPIO.setwarnings(False)
    GPIO.cleanup()

    # Modo BCM para la numeración de pines
    GPIO.setmode(GPIO.BCM)

    # Configuración de pines de entrada para los switches de las puertas
    GPIO.setup(5, GPIO.IN)  # Puerta 1 (pin 29)
    GPIO.setup(6, GPIO.IN)  # Puerta 1 (pin 29)
    GPIO.setup(13, GPIO.IN)  # Puerta 1 (pin 29)
    GPIO.setup(12, GPIO.IN)  # Puerta 1 (pin 29)


    # Configuración de pines de salida para los electromagnetos de las puertas
    GPIO.setup(16, GPIO.OUT)  # Electromagne    to Puerta 5
    GPIO.setup(19, GPIO.OUT)  # Electromagneto Puerta 5
    GPIO.setup(20, GPIO.OUT)  # Electromagneto Puerta 6
    GPIO.setup(21, GPIO.OUT)  # Electromagneto Puerta 7
    GPIO.setup(26, GPIO.OUT)  # Electromagneto PuerFalse

def TurnOnBackup():
    GPIO.output(16, True) 


def unlookAll():
    # try:
        GPIO.output(19, False) 
        GPIO.output(20, False) 
        GPIO.output(21, False) 
        GPIO.output(26, False)
    # finally:
    #     GPIO.cleanup() 

def LockAll():
    # try:
        GPIO.output(19, True) 
        GPIO.output(20, True) 
        GPIO.output(21, True) 
        GPIO.output(26, True)
    # finally:
    #     GPIO.cleanup() 



def switchwait(door, switch):
    GPIO.output(door, False) 
    #esperar 5 segunodos
    sleep(5)
    #Revisar switch
    while True:
        # 0 represents door closed
        # 1 represents door open 
        print(GPIO.input(switch))
        if GPIO.input(switch) == 0:  # Si el puerto 5 está en HIGH (puerta 1 cerrada)
            
            print(f"Puerta {switch} Cerrada")
            print(GPIO.input(switch))
            GPIO.output(door, True)  # Encender electromagneto Puerta 1
            print("TURN ON MAGNET")
            break


def buttonmonitor():
    # while True:
        if GPIO.input(5):  # Si el puerto 6 está en HIGH (puerta 2 cerrada)
            threading.Thread(target=switchwait, args=(19,5,), daemon=True).start()
        if GPIO.input(6):  # Si el puerto 6 está en HIGH (puerta 2 cerrada)
            threading.Thread(target=switchwait, args=(20,6,), daemon=True).start()
        if GPIO.input(13):  # Si el puerto 13 está en HIGH (puerta 3 cerrada)
            threading.Thread(target=switchwait, args=(21,13,), daemon=True).start()
        if GPIO.input(12):  # Si el puerto 12 está en HIGH (puerta 4 cerrada)
            threading.Thread(target=switchwait, args=(26,12,), daemon=True).start()
        # sleep(0.1) 
