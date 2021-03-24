import typing
from flask_restful import Resource
from app.patch import parse, fields
from app.resource.warehouse.service import (
    add_wms_num,
    in_ordered_params,
    out_ordered_params,
    get_wms_in_list,
    update_wms_num,
)
from app.utils.basic import convert_arrobj_to_tuple
from app.utils.date import now_date
from app.utils.http import ApiResponse
from app.utils.sql import sql_manager


class WarehouseInList(Resource):
    """入库列表"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "in_type": fields.Integer(),
        }
    )
    def get(self, args: typing.Dict):
        """入库列表"""
        page_index = int(args["page_index"])
        page_size = int(args["page_size"])
        offset = (page_index - 1) * page_size
        start_date = args["start_date"]
        end_date = args["end_date"]
        word = args["word"]
        in_type = args.get("in_type")
        filter_list = []
        if start_date and end_date:
            filter_list.append(f""" in_date BETWEEN '{start_date}' AND '{end_date}' """)
        if word:
            filter_list.append(f"""goods.name LIKE '%{word}%'""")
        if in_type is not None:
            filter_list.append(f"""in_type = '{in_type}'""")

        filter_str = " AND ".join(filter_list)
        sql = f"""
            SELECT
            wms.in_date as in_date,
            wms.id as id,
            wms.price as price,
            wms.in_num as in_num,
            wms.in_type as in_type,
            wms.in_code as in_code,
            goods.name as goods_name,
            wms.goods_id as goods_id
            FROM
            warehouse_in as wms
            LEFT JOIN goods ON wms.goods_id = goods.id WHERE {filter_str}
            """
        data = sql_manager.get_list(sql + f"""LIMIT {offset},{page_size}""")
        count = sql_manager.get_one(
            f"""
            SELECT COUNT(wms.goods_id) FROM
            warehouse_in as wms
            LEFT JOIN goods ON wms.goods_id = goods.id WHERE {filter_str} 
        """
        )
        result = list(map(lambda x: {**x, "price": float(x["price"])}, data))
        res = {"total": count["COUNT(wms.goods_id)"], "items": result}

        return ApiResponse.success(res)


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

        prefix = "in_"
        in_code = prefix + now_date("%Y%m%d%H%M%S")
        now = now_date("%Y-%m-%d %H:%M:%S")
        extra_params = in_ordered_params(args["fields"], in_code, now)
        tuple_values = convert_arrobj_to_tuple(extra_params)
        sql_manager.multi_excute(
            "INSERT INTO warehouse_in (goods_id,price,in_num,in_type,in_date,in_code) VALUES (%s, %s, %s, %s, %s, %s)",
            tuple_values,
        )
        add_wms_num(extra_params)
        return ApiResponse.success(None)


class WarehouseOut(Resource):
    """出库"""

    @parse({"out_list": fields.List(fields.Nested({"goods_id": fields.Integer(), "num": fields.Integer()}))})
    def post(self, args: typing.List):
        prefix = "out_"
        out_code = prefix + now_date("%Y%m%d%H%M%S")
        out_date = now_date("%Y-%m-%d %H:%M:%S")
        wms_in_list = get_wms_in_list()
        extra_params = out_ordered_params(args["out_list"], out_code, out_date, wms_in_list)
        tuple_values = convert_arrobj_to_tuple(extra_params)
        # 添加出库表行数据
        sql_manager.multi_excute(
            "INSERT INTO warehouse_out (goods_id,out_num,out_date,out_code,batch) VALUES (%s, %s, %s, %s, %s)",
            tuple_values,
        )
        # 更新入库表信息状态
        update_wms_num(args["out_list"], wms_in_list)
        return ApiResponse.success(None)


class WarehouseOutList(Resource):
    """出库列表"""

    pass
