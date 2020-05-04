from flask import Flask

app = Flask(__name__)

# import anything already loaded in main
from main import *
from recipease.routes.home import *