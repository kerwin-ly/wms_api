from flask import Blueprint

blueprint = Blueprint("api", __name__, url_prefix="/api")


from . import goods
from . import warehouse
from . import association
