import typing
from flask_restful import Resource
from app.patch import parse, fields
from app.resource.warehouse.service import (
    add_wms_num,
    in_ordered_params,
    out_ordered_params,
    get_wms_in_list,
    update_wms_num,
    add_wms_history,
)
from app.utils.basic import convert_arrobj_to_tuple
from app.utils.date import now_date
from app.utils.http import ApiResponse
from app.utils.sql import sql_manager


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
        offset = (args['page_index'] - 1) * args['page_size']
        page_size = args['page_size']
        word = args['word']
        filter_str = ''
        if word:
            filter_str = f"""WHERE name LIKE '%{word}%"""
        sql = f"""(
                (SELECT wms.id, wms.total as num, wms.goods_id, goods.name as goods_name
                FROM warehouse as wms
                LEFT JOIN goods
                ON wms.goods_id=goods.id
                {filter_str}) A
                LEFT JOIN
                (SELECT goods_id, Cast(sum(price * (in_num - out_num)) AS FLOAT) as cost 
                FROM warehouse_in
                WHERE in_num > out_num
                GROUP BY goods_id) B
                ON A.goods_id=B.goods_id
            )"""
        sql_list = f"""SELECT * FROM {sql} LIMIT {offset}, {page_size}"""
        sql_count = f"""SELECT COUNT(*) as total FROM {sql}"""
        data = sql_manager.get_list(sql_list)
        count = sql_manager.get_one(sql_count)
        res = {
            'total': count['total'],
            'items': data
        }
        return ApiResponse.success(res)

class WarehouseBatch(Resource):
    """库存批次详情"""
    @parse({
        "goods_id": fields.Integer(required=True),
        "page_index": fields.Integer(required=True),
        "page_size": fields.Integer(required=True)
    })
    def get(self, args: typing.Dict):
        page_index = args["page_index"]
        page_size = args["page_size"]
        offset = (page_index - 1) * page_size
        goods_id = args["goods_id"]
        sql_list = f"""
            SELECT CAST(price AS FLOAT ) as price, (in_num-out_num) as exit_num, in_type, in_code, in_date
            FROM warehouse_in
            WHERE in_num>out_num AND goods_id={goods_id}
        """
        data = sql_manager.get_list(f"""{sql_list} LIMIT {offset},{page_size}""")
        sql_count = sql_manager.get_one(f"""SELECT COUNT(*) as total FROM warehouse_in WHERE in_num>out_num AND goods_id={goods_id}""")
        return ApiResponse.success({
            'total': sql_count['total'],
            'items': data
        })


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
            CAST(wms.price AS FLOAT) as price,
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
            SELECT COUNT(wms.goods_id) as total FROM
            warehouse_in as wms
            LEFT JOIN goods ON wms.goods_id = goods.id WHERE {filter_str} 
        """
        )

        res = {"total": count["total"], "items": data}

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
        # 添加入库表行数据
        sql_manager.multi_excute(
            "INSERT INTO warehouse_in (goods_id,price,in_num,in_type,in_date,in_code) VALUES (%s, %s, %s, %s, %s, %s)",
            tuple_values,
        )
        # 添加库存操作记录
        add_wms_history(tuple_values)
        # 添加库存表数据
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
            "INSERT INTO warehouse_out (goods_id,out_num,out_date,out_code) VALUES (%s, %s, %s, %s)",
            tuple_values,
        )
        # 更新库存表信息状态
        update_wms_num(args["out_list"], wms_in_list, out_code, out_date)
        return ApiResponse.success(None)


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
        page_index = int(args["page_index"])
        page_size = int(args["page_size"])
        offset = (page_index - 1) * page_size
        start_date = args["start_date"]
        end_date = args["end_date"]
        word = args["word"]
        filter_list = []
        if start_date and end_date:
            filter_list.append(f""" out_date BETWEEN '{start_date}' AND '{end_date}' """)
        if word:
            filter_list.append(f"""goods.name LIKE '%{word}%'""")

        filter_str = " AND ".join(filter_list)
        sql = f"""
        (
            (
                SELECT
                    wms_out.*, name as goods_name 
                FROM
                    warehouse_out as wms_out
                LEFT JOIN goods
                ON wms_out.goods_id=goods.id
                WHERE {filter_str}
            ) A
            LEFT JOIN (
            SELECT `code`, goods_id, sum( num * price ) out_cost 
            FROM
                warehouse_history 
            WHERE
                `code` LIKE 'out%' 
            GROUP BY `code`, goods_id 
            ) B 
            ON A.out_code = B.code AND A.goods_id = B.goods_id 
        )
        """
        sql_list = "SELECT * FROM " + sql
        limit = f"""LIMIT {offset},{page_size}"""
        data = sql_manager.get_list(sql_list + limit)
        sql_count = "SELECT COUNT(*) as total FROM " + sql
        count = sql_manager.get_one(sql_count)
        result = list(map(lambda x: {**x, "out_cost": float(x["out_cost"])}, data))
        res = {"total": count["total"], "items": result}

        return ApiResponse.success(res)

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
        goods_id = args['goods_id']
        out_code = args['out_code']
        page_index = args['page_index']
        page_size = args['page_size']
        offset = (page_index - 1) * page_size
        sql_list = f"""
            SELECT CAST(price AS FLOAT) as price, num as in_num, type as in_type, code as in_code, last_update_time as in_date 
            FROM warehouse_history 
            WHERE code='{out_code}' AND goods_id={goods_id}
            LIMIT {offset},{page_size}
        """
        sql_count = f"""
            SELECT COUNT(*) as total
            FROM warehouse_history 
            WHERE code='{out_code}' AND goods_id={goods_id}
        """
        data = sql_manager.get_list(sql_list)
        count = sql_manager.get_one(sql_count)
        res = {
            'total': count['total'],
            'items': data
        }

        return ApiResponse.success(res)

class WarehouseHistory(Resource):
    """明细表"""

    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "start_date": fields.String(),
            "end_date": fields.String(),
            "word": fields.String(missing=""),
            "type": fields.Integer(missing=-1)
        }
    )
    def get(self, args: typing.Dict):
        page_index = int(args["page_index"])
        page_size = int(args["page_size"])
        offset = (page_index - 1) * page_size
        start_date = args["start_date"]
        end_date = args["end_date"]
        word = args["word"]
        type = args["type"]
        filter_list = []
        if start_date and end_date:
            filter_list.append(f"""last_update_time BETWEEN '{start_date}' AND '{end_date}' """)
        if word:
            filter_list.append(f"""goods.name LIKE '%{word}%'""")
        if type != -1:
            filter_list.append(f"""type={type}""")

        filter_str = " AND ".join(filter_list)
        sql_list = f"""SELECT goods_id, goods.name as goods_name, type as operation, last_update_time as date, num FROM warehouse_history as wms LEFT JOIN goods ON wms.goods_id=goods.id WHERE {filter_str} LIMIT {offset},{page_size}"""
        print(sql_list)
        data = sql_manager.get_list(sql_list)
        sql_count = f"""SELECT COUNT(*) as total FROM warehouse_history as wms LEFT JOIN goods ON wms.goods_id=goods.id WHERE {filter_str}"""
        count = sql_manager.get_one(sql_count)
        res = {
            'total': count['total'],
            'items': data
        }
        return ApiResponse.success(res)