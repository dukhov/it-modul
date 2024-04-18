# app.py - главный модуль приложения

from flask import Flask
from web_app import WebApp

app = Flask(__name__)
web_app = WebApp(app)

if __name__ == '__main__':
    app.run(debug=True)
