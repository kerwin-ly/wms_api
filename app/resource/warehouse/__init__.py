from flask_restful import Api
from .. import blueprint

api = Api(blueprint, prefix="/warehouse", decorators=[])

from . import view, url
