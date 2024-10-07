import csv
from database.databasecontrol import add_employee_to_database

# Ruta al archivo CSV
csv_file_path = './USERS.csv'

# Función para procesar y actualizar usuarios desde el archivo CSV
def export_users_from_csv(csv_file):
    with open(csv_file, mode='r', newline='') as file:
        csv_reader = csv.reader(file)
        
        # Procesar cada fila en el archivo CSV
        for row in csv_reader:
            # Extraer los datos relevantes
            first_last_name = row[0].strip().replace(',', '')  # Eliminar espacios y comas
            ss_last_four = row[1].strip()     # Segundo campo: "SS 4" (eliminando espacios)
            
            # Verificar que el SS no sea nulo y tenga exactamente 4 dígitos
            if not ss_last_four or len(ss_last_four) != 4:
                print(f"Invalid SS: {first_last_name} has SS Last Four: '{ss_last_four}'")
                continue
            
            # Dividir el nombre en First y Last
            name_parts = first_last_name.split()
            if len(name_parts) == 2:
                First = name_parts[0].strip()
                Last = name_parts[1].strip()
            elif len(name_parts) > 2:
                # Manejar nombres compuestos (más de dos partes)
                First = name_parts[0].strip()
                Last = " ".join(name_parts[1:]).strip()
            else:
                continue  # Si el nombre no tiene al menos dos partes, se omite la fila
            
            # Actualizar el empleado en la base de datos solo si el SS es válido
            add_employee_to_database(First, Last, ss_last_four, 1, 0, 0)
            print(f"Updated employee: {First} {Last}, SS Last Four: {ss_last_four}")

# Ejecutar la función
export_users_from_csv(csv_file_path)
