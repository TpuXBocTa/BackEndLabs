import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_smorest import Api

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__)
app.config.from_pyfile("config.py", silent=True)

db.init_app(app)
migrate.init_app(app, db)
api = Api(app)
jwt = JWTManager(app)

from . import Models
from . import views


@app.cli.command("test_data")
def seed_command():
    from .Data import test_data
    test_data(reset=False)
    print("test data downloaded")
