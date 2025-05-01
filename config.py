import os
import secrets

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///flaskdb.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = secrets.token_urlsafe(24)
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://alejandro:seyerreyes@coolify2.isladigital.xyz:3311/store'
    #SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://usuario:contaseña@85.239.241.150:3306/store'

#Comandos para descargar en instalar todas las librerias offline
#python ñ
#pip install --no-index --find-links=librerias -r requirements.txt