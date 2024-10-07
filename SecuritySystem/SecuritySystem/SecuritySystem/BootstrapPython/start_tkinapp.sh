#!/bin/bash

# Cambiar al directorio donde está ubicado el script
cd /home/vbs/Desktop/SecuritySystem/SecuritySystem/SecuritySystem/BootstrapPython/

# Configurar la variable DISPLAY para el entorno gráfico
export DISPLAY=:0

# Permitir que root acceda al entorno gráfico
xhost +SI:localuser:root

# Ejecutar el script de Python
/usr/bin/python3 /home/vbs/Desktop/SecuritySystem/SecuritySystem/SecuritySystem/BootstrapPython/tkinapp.py >> /home/vbs/Desktop/SecuritySystem/logs/tkinapp.log 2>&1

