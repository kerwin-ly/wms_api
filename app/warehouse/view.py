import typing
from flask_restful import Resource

from patch import fields, parse


class WarehouseList(Resource):
    """库存列表"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "word": fields.String(missing="")
        }
    )
    def get(self, args: typing.Dict):
        pass;

class WarehouseBatch(Resource):
    """库存批次详情"""
    @parse({
        "goods_id": fields.Integer(required=True),
        "page_index": fields.Integer(required=True),
        "page_size": fields.Integer(required=True)
    })
    def get(self, args: typing.Dict):
        pass;


class WarehouseInList(Resource):
    """入库列表"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "in_type": fields.Integer(),
        }
    )
    def get(self, args: typing.Dict):
        """入库列表"""
        pass;

class WarehouseInDownload(Resource):
    """入库表下载"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        pass;

class WarehouseIn(Resource):
    """入库"""

    @parse(
        {
            "fields": fields.List(
                fields.Nested(
                    {
                        "goods_id": fields.Integer(),
                        "price": fields.Integer(),
                        "in_num": fields.Integer(),
                        "in_type": fields.Integer(),
                    }
                )
            )
        }
    )
    def post(self, args: typing.List):
        pass;


class WarehouseOut(Resource):
    """出库"""

    @parse({"out_list": fields.List(fields.Nested({"goods_id": fields.Integer(), "num": fields.Integer()}))})
    def post(self, args: typing.List):
        pass;


class WarehouseOutList(Resource):
    """出库列表"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
        }
    )
    def get(self, args: typing.Dict):
        pass;

class WarehouseOutDownload(Resource):
    """出库列表下载"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
        }
    )
    def get(self, args: typing.Dict):
        pass;



class WarehouseOutBatch(Resource):
    """出库批次详情"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "goods_id": fields.Integer(required=True),
            "out_code": fields.String(required=True),
        }
    )
    def get(self, args: typing.Dict):
        pass;

class WarehouseHistory(Resource):
    """明细表"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        pass;

class WarehouseHistoryDownload(Resource):
    """明细表下载"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        pass;

