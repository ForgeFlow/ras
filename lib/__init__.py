from flask import Flask

app = Flask(__name__)

from lib import routes
