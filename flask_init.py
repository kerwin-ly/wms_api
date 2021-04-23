"""
flask 初始化
"""
import logging
from flask import Flask

from app import blueprint
from database.mysql_db import register_db_handler
from utils.api_handler import register_api_handler
from utils.logger import add_console_handler, add_file_handler


def create_app() -> Flask:
    app = Flask(__name__)

    # 集成日志
    logging.getLogger("werkzeug").disabled = True
    add_console_handler(app.logger)
    add_file_handler(app.logger)

    # 初始化数据库
    register_db_handler(app)

    # api请求/状态码处理
    register_api_handler(app)

    # 注册路由蓝图
    app.register_blueprint(blueprint)

    return app
