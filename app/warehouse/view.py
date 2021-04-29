import typing
from flask_restful import Resource
from sqlalchemy import func

from app.common.models.goods import Goods, GoodsType
from app.common.models.warehouse import WarehouseIn, WarehouseOut, Warehouse, WarehouseHistory
from app.warehouse.schema import WarehouseSchema, WarehouseBatchSchema, WarehouseInSchema
from app.warehouse.service import (
    get_out_batches,
    get_filtered_in_list,
    convert_out_list,
    update_goods_total,
    update_goods_history,
    out_of_range,
    convert_out2history,
    convert_in2history,
    convert_in2total,
    insert_goods_in,
    get_history_list,
    get_in_list,
    get_out_list)
from database.mysql_db import session
from patch import fields, parse
from utils import fs
from utils.date import now_date
from utils.http import ApiResponse


class WarehouseList(Resource):
    """库存列表"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "word": fields.String(missing=""),
            "type_id": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        subq = WarehouseIn.query \
            .with_entities(
                WarehouseIn.goods_id,
                func.sum(WarehouseIn.price * (WarehouseIn.in_num - WarehouseIn.out_num)).label('cost'),
            ) \
            .filter(WarehouseIn.in_num > WarehouseIn.out_num) \
            .group_by(WarehouseIn.goods_id).subquery()

        q = Warehouse.query \
            .with_entities(
                Warehouse.id,
                Warehouse.total.label('num'),
                Warehouse.goods_id,
                Goods.name.label('goods_name'),
                Goods.type_id,
                GoodsType.name.label('type_name'),
                subq.c.cost
            ) \
            .outerjoin(Goods, Warehouse.goods_id == Goods.id) \
            .outerjoin(GoodsType, Goods.type_id == GoodsType.id) \
            .outerjoin(subq, Warehouse.goods_id == subq.c.goods_id)

        if args.get("word"):
            q = q.filter(Goods.name.like(f"%{args['word']}%"))
        if args.get("type_id"):
            q = q.filter(Goods.type_id == args["type_id"])
        count = q.count()
        offset = (args["page_index"] - 1) * args["page_size"]
        items = q.offset(offset).limit(args["page_size"]).all()
        result = WarehouseSchema(many=True).dump(items)

        return {"total": count, "items": result}


class WarehouseBatch(Resource):
    """库存批次详情"""

    @parse(
        {
            "goods_id": fields.Integer(required=True),
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
        }
    )
    def get(self, args: typing.Dict):
        q = WarehouseIn.query \
            .with_entities(
                WarehouseIn.price,
                WarehouseIn.in_type,
                WarehouseIn.in_code,
                func.date_format(WarehouseIn.created_time, '%Y-%m-%d %H:%i:%S').label('in_date'),
                (WarehouseIn.in_num - WarehouseIn.out_num).label('exist_num')
            ) \
            .filter(
                WarehouseIn.in_num > WarehouseIn.out_num,
                WarehouseIn.goods_id == args['goods_id']
            ) \
            .order_by(WarehouseIn.created_time.desc())
        count = q.count()
        offset = (args["page_index"] - 1) * args["page_size"]
        items = q.offset(offset).limit(args["page_size"]).all()
        result = WarehouseInSchema(many=True).dump(items)
        return ApiResponse.success({
            'total': count,
            'result': result
        })



class WarehouseInList(Resource):
    """入库列表"""

    @parse(
        {
            "page_index": fields.Integer(missing=1),
            "page_size": fields.Integer(missing=10),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type_id": fields.Integer(),
            "in_type": fields.String(validate=lambda x: x in ["purchase", "surplus", "gift"]),
        }
    )
    def get(self, args: typing.Dict):
        """入库列表"""
        data = get_in_list(args)

        return ApiResponse.success(data)


class WarehouseInDownload(Resource):
    """入库表下载"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type_id": fields.Integer(),
            "in_type": fields.String(validate=lambda x: x in ["purchase", "surplus", "gift"]),
        }
    )
    def get(self, args: typing.Dict):
        data = get_in_list(args)
        result = data["items"]
        cols = [
            {
                "key": "goods_name",
                "value": "类目名",
            },
            {"key": "type_name", "value": "分类名称"},
            {"key": "price", "value": "单价"},
            {"key": "in_num", "value": "入库数量"},
            {"key": "in_type", "value": "入库类型"},
            {"key": "in_code", "value": "入库单号"},
            {"key": "in_date", "value": "入库时间"},
        ]
        url = fs.generate_excel(cols, result, "入库列表")

        return ApiResponse.success({"url": url})


class WarehouseItemIn(Resource):
    """入库"""

    @parse(
        {
            "fields": fields.List(
                fields.Nested(
                    {
                        "goods_id": fields.Integer(),
                        "price": fields.Integer(),
                        "in_num": fields.Integer(),
                        "in_type": fields.String(
                            required=True, validate=lambda x: x in ["purchase", "surplus", "gift"]
                        ),
                    }
                )
            )
        }
    )
    def post(self, args: typing.List):
        prefix = "in_"
        in_code = prefix + now_date("%Y%m%d%H%M%S")
        in_list = list(map(lambda x: {**x, "in_code": in_code}, args["fields"]))

        # 更新入库表
        insert_goods_in(in_list)

        # 更新明细表
        format_in_history = convert_in2history(in_list)
        update_goods_history(format_in_history)

        # 更新库存表
        format_in_list = convert_in2total(in_list)
        update_goods_total("in", format_in_list)

        session.commit()
        return ApiResponse.success()


class WarehouseItemOut(Resource):
    """出库"""

    @parse({"out_list": fields.List(fields.Nested({"goods_id": fields.Integer(), "num": fields.Integer()}))})
    def post(self, args: typing.List):

        if out_of_range(args["out_list"]):
            return ApiResponse.error(f"出库数量超出库存总数")
        prefix = "out_"
        out_code = prefix + now_date("%Y%m%d%H%M%S")
        out_list = args["out_list"]
        filtered_in_list = get_filtered_in_list()  # 获取未全部出库的入库单信息
        need_update_list = []

        for item in out_list:
            item["out_code"] = out_code
            batches = get_out_batches(item["goods_id"], item["num"], filtered_in_list)
            need_update_list.extend(batches)
        # 更新入库表中的出库数量
        session.bulk_update_mappings(WarehouseIn, need_update_list)

        # 更新出库表
        format_out_list = convert_out_list(out_list, out_code)
        session.bulk_insert_mappings(WarehouseOut, format_out_list)

        # 更新库存表
        update_goods_total("out", out_list)

        # 更新明细表
        format_out_history = convert_out2history(need_update_list, out_code)
        update_goods_history(format_out_history)

        return ApiResponse.success()


class WarehouseOutList(Resource):
    """出库列表"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type_id": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        data = get_out_list(args)
        return ApiResponse.success(data)


class WarehouseOutDownload(Resource):
    """出库列表下载"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type_id": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        data = get_out_list(args)
        result = data['items']
        cols = [{
            'key': 'goods_name',
            'value': '类目名',
        }, {
            'key': 'type_name',
            'value': '分类名称'
        }, {
            'key': 'out_num',
            'value': '出库数量'
        }, {
            'key': 'out_code',
            'value': '出库单号'
        }, {
            'key': 'out_date',
            'value': '出库时间'
        }, {
            'key': 'out_cost',
            'value': '出库成本'
        }]
        url = fs.generate_excel(cols, result, '出库列表')
        return ApiResponse.success({'url': url})


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
        q = WarehouseHistory.query \
            .with_entities(
                WarehouseHistory.price,
                WarehouseHistory.type.label("in_type"),
                WarehouseHistory.num.label("out_num"),
                WarehouseHistory.code.label("in_code"),
                func.date_format(WarehouseHistory.created_time, '%Y-%m-%d %H:%i:%S').label('in_date'),
            ) \
            .filter(
                WarehouseHistory.goods_id == args['goods_id'],
                WarehouseHistory.code == args['out_code']
            ) \
            .order_by(WarehouseHistory.created_time.desc())

        count = q.count()
        offset = (args["page_index"] - 1) * args["page_size"]
        items = q.offset(offset).limit(args["page_size"]).all()
        result = WarehouseBatchSchema(many=True).dump(items)

        return {"total": count, "items": result}


class WarehouseItemHistory(Resource):
    """明细表"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type_id": fields.Integer(),
            "type": fields.String(validate=lambda x: x in ["purchase", "surplus", "gift"]),
        }
    )
    def get(self, args: typing.Dict):
        data = get_history_list(args)

        return ApiResponse.success(data)


class WarehouseHistoryDownload(Resource):
    """明细表下载"""

    @parse(
        {
            "page_index": fields.Integer(required=True),
            "page_size": fields.Integer(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type_id": fields.Integer(),
            "type": fields.String(validate=lambda x: x in ["purchase", "surplus", "gift"]),
        }
    )
    def get(self, args: typing.Dict):
        data = get_history_list(args)
        result = data["items"]
        cols = [
            {
                "key": "goods_name",
                "value": "类目名",
            },
            {"key": "type_name", "value": "分类名称"},
            {"key": "operation", "value": "操作类型"},
            {"key": "num", "value": "数量"},
            {"key": "date", "value": "时间"},
        ]

        url = fs.generate_excel(cols, result, "明细列表")
        return ApiResponse.success({"url": url})
