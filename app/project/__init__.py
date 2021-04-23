"""
项目模块
"""
from flask_restful import Api
from .. import blueprint

api = Api(blueprint, prefix="/project", decorators=[])

from . import view, url
