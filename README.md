## Instalación del Backend del Proyecto:

Tener en /cuenta que si deseas instalar el Backend en Windows:  

### Instalar Microsoft Visual C++ Build Tools:
Visita el enlace proporcionado en el mensaje de error: Microsoft C++ Build Tools.
Descarga e instala las herramientas de compilación de C++.
Durante la instalación, asegúrate de seleccionar la versión de Visual C++ Build Tools que incluya C++ 14.0 o superior.

El 1 paso es  clonar el repositorio:
* git clone https://github.com/BIOS-Co/PREDICCION-DE-FALLAS-TOPTEC--BACKEDN_F.git
*Una vez descargado el siguiente paso es ubicarse en la carpeta que contiene el proyecto y dentro crear un entorno virtual, para esto se deberá de tener instalado python,  la versión recomendada es: Python 3.12
Su enlace de descarga es el siguiente:
*Download Python | Python.org
*Para crear el entorno virtual deberá de ejecutar por consola el siguiente comando, dentro del la ubicación del repositorio descargado anteriormente:
* Python -m venv ”nombre del entorno”    ó  Python3 -m venv ”nombre del entorno”

Una vez creado el ambiente virtual se deberá de instalar las librerías correspondientes para su ejecución.  De las cuales existen 2 versiones, una para Windows y la otra para Linux
Para Windows:  
* pip install -r requirement_windows.txt

Para Linux:
* pip install -r requirement_linux.txt

Una vez instalado las librerias, el siguiente paso es migrar todos los datos a la base de datos, para esto debemos de tener instalo PostgredSQL su enlace de desca es el siguiente:
* PostgreSQL: Downloads
Y ejecutar los siguientes comandos:
* python manage.py makemigrations
* python manage.py migrate

Por otro lado dentro de la carpeta secciones y dentro de la subcarpeta "predict" .
Deberemos de crear 2 carpetas una llamada "models" y la otra "scalers". Allí debemos de ingresar los archivos de este repositorio:
* https://github.com/EstivenValencia/models-tt-2
Del cual los archivos con iniciales "best", van para models, y los otros para scalers.

Por último ejecutar el proyecto.
* python manage.py runserver

Tener en cuenta insertar estas variables en la base de datos, para esto encontrara los siguientes comandos SQL, para insertar las variables necesarias para iniciar el proyecto:

      insert into public.predict_machine (name, description)
      values('Máquina 1', '')
      
      insert into public.predict_machine (name, description)
      values('Máquina 2', '')
      
      
      
      
      insert into public.predict_process  (name, description)
      values('AUT', '')
      
      insert into public.predict_process  (name, description)
        values('NT', '')
