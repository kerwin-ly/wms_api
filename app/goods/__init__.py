from flask_restful import Api
from .. import blueprint

api = Api(blueprint, prefix="/goods", decorators=[])

from . import view, url
