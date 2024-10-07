import time
import requests

def main():
    while True:
        response = requests.post('http://192.168.2.1:5000/trigger_reload')  # Asegúrate de usar la IP correcta
        if response.status_code == 200:
            print("La página se recargó con éxito.")
        else:
            print(f"Error al intentar recargar la página: {response.status_code} - {response.text}")
        time.sleep(108000)  # Espera 5 segundos antes de enviar el siguiente request

if __name__ == "__main__":
    main()
