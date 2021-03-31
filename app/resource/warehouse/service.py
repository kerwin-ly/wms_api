from collections import OrderedDict

from app.resource.warehouse.type import WarehouseOperationType
from app.utils import date
from app.utils.sql import sql_manager


def in_ordered_params(fields, in_code, now):
    return list(
        map(
            lambda item: {
                "goods_id": item["goods_id"],
                "price": item["price"],
                "in_num": item["in_num"],
                "in_type": item["in_type"],
                "in_date": now,
                "in_code": in_code,
            },
            fields,
        )
    )


"""获取某商品的库存总数"""


def get_goods_total(goods_id):
    return sql_manager.get_one(f"""SELECT total FROM warehouse WHERE goods_id={goods_id}""")


"""库存表 新增行"""


def add_wms_row(in_item):
    sql_manager.create("INSERT INTO warehouse (goods_id, total) VALUES (%s, %s)", tuple(in_item.values()))


"""更新某商品的库存总数"""


def update_wms_row(goods_id, total):
    sql_manager.moddify("UPDATE warehouse SET total = %s WHERE goods_id = %s", (total, goods_id))


def to_ordered_list(in_list):
    return list(map(lambda item: {"goods_id": item["goods_id"], "in_num": item["in_num"]}, in_list))


"""更新库存表商品信息"""


def add_wms_num(in_list):
    ordered_list = to_ordered_list(in_list)
    for item in ordered_list:
        result = get_goods_total(item["goods_id"])
        if result is None:
            add_wms_row(item)
        else:
            goods_total = int(item["in_num"]) + result["total"]
            update_wms_row(item["goods_id"], goods_total)


"""格式化出库参数"""


def out_ordered_params(fields, out_code, out_date, wms_in_list):
    return list(
        map(
            lambda item: {
                "goods_id": item["goods_id"],
                "out_num": item["num"],
                "out_date": out_date,
                "out_code": out_code,
            },
            fields,
        )
    )


"""
获取出库批次
goods_id: 商品ID
out_total: 出库总数
in_list: 库存列表
"""


def get_out_batches(goods_id, out_total, in_list):
    # in_num = exit_num + out_num
    filter_list = list(filter(lambda item: item["goods_id"] == goods_id, in_list))
    batches = []
    total = 0
    index = 0

    while out_total > total:
        exit_num = filter_list[index]["exist_num"]
        if total + exit_num > out_total:
            current_out = out_total - total
        else:
            current_out = exit_num

        batches.append({**OrderedDict(filter_list[index]), "out_num": current_out})  # 如果出库总数小于和，则表明最后一批次未完全出库
        total += current_out
        index += 1
    return batches


"""获取库存信息"""


def get_wms_in_list():
    data = sql_manager.get_list(
        "SELECT id as in_id, goods_id, in_date, price, in_num, in_type, in_num-out_num as exist_num FROM warehouse_in WHERE out_num < in_num"
    )
    return list(map(lambda item: {**item, "price": float(item["price"])}, data))


"""更新库存表的出库数量"""


def update_wms_num(out_list, wms_in_list, out_code, out_date):
    need_update_list = []
    for item in out_list:
        batch = get_out_batches(item["goods_id"], item["num"], wms_in_list)
        need_update_list.extend(batch)
    # 更新入库表的out_num字段
    in_tuple = tuple(
        map(
            lambda in_item: tuple(OrderedDict({"out_num": in_item["out_num"], "in_id": in_item["in_id"]}).values()),
            need_update_list,
        )
    )
    sql_manager.multi_excute("UPDATE warehouse_in SET out_num = out_num + %s WHERE id = %s", in_tuple)
    # 更新库存表的库存总数
    total_tuple = tuple(
        map(
            lambda in_item: tuple(
                OrderedDict({"out_num": in_item["out_num"], "goods_id": in_item["goods_id"]}).values()
            ),
            need_update_list,
        )
    )
    sql_manager.multi_excute("UPDATE warehouse SET total = total - %s WHERE goods_id = %s", total_tuple)
    # 更新库存历史表，根据出库数量（先进先出规则），获取入库批次
    history = tuple(
        map(
            lambda in_item: tuple(
                OrderedDict(
                    {
                        "goods_id": in_item["goods_id"],
                        "price": in_item["price"],
                        "num": in_item["out_num"],
                        "type": WarehouseOperationType.out,
                        "last_update_time": out_date,
                        "code": out_code,
                    }
                ).values()
            ),
            need_update_list,
        )
    )
    add_wms_history(history)


"""新增仓库操作记录"""


def add_wms_history(params):
    sql_manager.multi_excute(
        "INSERT INTO warehouse_history (goods_id,price,num,type,last_update_time,code) VALUES (%s, %s, %s, %s, %s, %s)",
        params,
    )

def get_out_list_sql(args):
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    word = args.get("word")
    filter_list = []
    filter_str = ''
    if start_date and end_date:
        filter_list.append(f""" out_date BETWEEN '{start_date}' AND '{end_date}' """)
    if word:
        filter_list.append(f"""goods.name LIKE '%{word}%'""")
    if len(filter_list):
        filter_str = " WHERE " + " AND ".join(filter_list)
    sql = f"""
            (
                (
                    SELECT
                        wms_out.*, name as goods_name 
                    FROM
                        warehouse_out as wms_out
                    LEFT JOIN goods
                    ON wms_out.goods_id=goods.id
                    {filter_str}
                ) A
                LEFT JOIN (
                SELECT `code`, goods_id, CAST(sum( num * price ) AS FLOAT) out_cost 
                FROM
                    warehouse_history 
                WHERE
                    `code` LIKE 'out%' 
                GROUP BY `code`, goods_id 
                ) B 
                ON A.out_code = B.code AND A.goods_id = B.goods_id 
            )
            """
    return sql

def get_history_filter(args):
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    word = args.get("word")
    type = args.get("type")
    filter_list = []
    filter_str = ''
    if start_date and end_date:
        filter_list.append(f"""last_update_time BETWEEN '{start_date}' AND '{end_date}' """)
    if word:
        filter_list.append(f"""goods.name LIKE '%{word}%'""")
    if type is not None:
        filter_list.append(f"""type={type}""")
    if len(filter_list):
        filter_str = ' WHERE ' + " AND ".join(filter_list)
    return filter_str

def get_history_list_sql(args):
    filter_str = get_history_filter(args)

    sql = f"""
        FROM warehouse_history as wms 
        LEFT JOIN goods 
        ON wms.goods_id=goods.id {filter_str}"""

    return sql

def get_in_filter(args):
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    word = args["word"]
    in_type = args.get("in_type")
    filter_list = []
    filter_str = ''
    if start_date and end_date:
        filter_list.append(f""" in_date BETWEEN '{start_date}' AND '{end_date}' """)
    if word:
        filter_list.append(f"""goods.name LIKE '%{word}%'""")
    if in_type is not None:
        filter_list.append(f"""in_type = '{in_type}'""")
    if len(filter_list):
        filter_str = " WHERE " + "AND ".join(filter_list)
    return filter_str

def get_in_list_sql(args):
    filter_str = get_in_filter(args)
    return f"""
        FROM
            warehouse_in as wms
            LEFT JOIN goods ON wms.goods_id = goods.id {filter_str}
    """

