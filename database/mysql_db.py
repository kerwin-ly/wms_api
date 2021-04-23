"""
初始化数据库
"""
import os
import configparser

from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy_utils import database_exists, create_database
from config.settings import ROOT_DIR

from flask_script import Manager
from sqlalchemy import create_engine


config_path = os.path.join(ROOT_DIR, "config", "sql.ini")
conf = configparser.ConfigParser()
conf.read(config_path)
host = conf.get("database", "host")
port = conf.getint("database", "port")
user = conf.get("database", "user")
pwd = conf.get("database", "pwd")
dbname = conf.get("database", "dbname")
charset = conf.get("database", "charset")
pool_size = conf.get("database", "pool_size")
pool_timeout = conf.get("database", "pool_timeout")
pool_recycle = conf.get("database", "pool_recycle")

db = SQLAlchemy()
session = db.session


def register_db_handler(app: Flask) -> None:
    sql_uri = f"""mysql+pymysql://{user}:{pwd}@{host}:{port}/{dbname}"""
    app.config["SQLALCHEMY_DATABASE_URI"] = sql_uri
    app.config["pool_size"] = pool_size
    app.config["pool_timeout"] = pool_timeout
    app.config["pool_recycle"] = pool_recycle
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
    app.config["SQLALCHEMY_ENCODING"] = "utf-8"
    app.config["SQLALCHEMY_ECHO"] = True

    engine = create_engine(
        sql_uri,
    )

    if not database_exists(engine.url):
        create_database(engine.url)
    engine.dispose()

    db.init_app(app)
    # 添加sqlalchemy 格式化转换
    Marshmallow(app)
    manager = Manager(app)

    # 迁移数据库
    Migrate(app, db)

    # manager是Flask-Script的实例，这条语句在flask-Script中添加一个db命令
    manager.add_command("db", MigrateCommand)
