"""
服务器模块
"""
from flask_restful import Api
from .. import blueprint

api = Api(blueprint, prefix="/server", decorators=[])

from . import view, url, schema, service
