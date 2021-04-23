from flask import Blueprint

blueprint = Blueprint("api", __name__, url_prefix="/api")


from . import server
from . import project
from . import association
