from flask import Blueprint

goods = Blueprint("goods", __name__)

import app.resource.goods.api
