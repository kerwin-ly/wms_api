import decimal
import typing

from flask_restful import Resource
from app.patch import parse, fields
from app.utils.http import ApiResponse
from app.utils.sql import sql_manager

# list = [{'price': 23}]


def to_float(x):
    print('x', x)
    # x.price = float(x.price)
    return x
# to_float(list)
arr = [{
    'age':1,
    'name': '111'
}, {
    'age': 2,
    'name': 222
}]



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
        """入库列表"""

        data = sql_manager.get_list('SELECT * FROM warehouse_in')
        result = list(map(lambda x: {**x, 'price': float(x['price'])}, data))
        print('result', data, result)

        return ApiResponse.success(result)
