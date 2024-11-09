# Examen Final
# Kiel R. Sáenz Zúñiga

## Parte Teórica 

Las respuestas a la primera parte del examen se encuentra en el archivo respuestas.ipynb


## Parte Práctica 

### Prerrequisitos

Asegúrate de tener instalados los siguientes requisitos en tu máquina:

- Python 3.x
- `pip` (la herramienta de instalación de paquetes de Python)
- `virtualenv` (para crear entornos virtuales)
- Se creo una base de datos en la nube, por consiguiente es necesario una conexión a internet

### 1. Crear un Entorno Virtual, activar el Entorno Virtual com git-bash, instalar las dependencias del requirements.txt y por último ejecutar el aplicativo

```bash
virtualenv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
fastapi dev main.py
```