import typing

from flask_restful import Resource
from app.patch import parse, fields

class WarehouseInList(Resource):
    @parse({
        "page_index": fields.String(required=True),
        "page_size": fields.String(required=True),
        "start_date": fields.DateTime(),
        "end_date": fields.DateTime(),
        "word": fields.String(missing=''),
        "in_type": fields.Integer()
    })
    def get(self, args: typing.Dict):
        print('args', args)
        return {"code": 200, "msg": "success"}
