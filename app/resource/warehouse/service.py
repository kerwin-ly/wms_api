from collections import OrderedDict

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
                "batch": ",".join(
                    list(
                        map(
                            lambda in_item: str(in_item["in_id"]),
                            get_out_batches(item["goods_id"], item["num"], wms_in_list),
                        )
                    )
                ),
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


def update_wms_num(out_list, wms_in_list):
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
