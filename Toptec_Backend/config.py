## variables con los datos importantes de login y configuracion
SECRET_KEY = 'django-insecure-lszooa+r20xm0tp(c=_i94rx7e4e3s37yaehqdjh7d4fry-*xi'

#Debug
debug = True

#Ip Production/Debug
protocol = 'http'
ip_server = "localhost"
url_server = "http://localhost:3000/"   ## modificar con el dominio final
port_front = 3000
port_back = 8000


# Adresses access allowed
allowed_host = ['*']
cors_allow_all = True
cors_whitelist = ['{protocol}://{ip}:{port}'.format(protocol=str(protocol), ip=str(ip_server), port=str(port_front))]



#Authentication data for BD sql server
driver_sql_server = 'ODBC Driver 17 for SQL Server'
server_bd_sql_server = '127.0.0.1'     # dev-server-mhc.database.windows.net'
database_sql_server = 'Toptec'   #bd_mhc_dev_production2 - bd_mhc_dev_Copy
username_bd_sql_server = 'postgres'
password_sql_server = '2718'
