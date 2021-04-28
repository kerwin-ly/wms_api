"""
更新明细表
"""
from collections import OrderedDict

from app.common.models.goods import Goods, GoodsType
from app.common.models.warehouse import WarehouseIn, Warehouse, WarehouseHistory
from app.common.types.warehouse import WarehouseAction
from app.warehouse.schema import WarehouseInSchema, WarehouseSchema, WarehouseHistorySchema
from database.mysql_db import session
from utils.date import now_date

"""
批量插入入库表
"""


def insert_goods_in(goods_list):
    session.bulk_insert_mappings(WarehouseIn, goods_list)


"""
更新库存明细
"""


def update_goods_history(goods_list):
    session.bulk_insert_mappings(WarehouseHistory, goods_list)


"""
更新库存表总数
"""


def update_goods_total(type: str, goods_list):
    if type == "out":
        for item in goods_list:
            goods_item = Warehouse.query.filter_by(goods_id=item["goods_id"]).one()
            goods_dict = WarehouseSchema().dump(goods_item)
            goods_num = goods_dict["total"] - item["num"]
            goods_item.update(total=goods_num)
    elif type == "in":
        for item in goods_list:
            goods_item = Warehouse.query.filter_by(goods_id=item["goods_id"]).first()
            if goods_item:
                goods_dict = WarehouseSchema().dump(goods_item)
                goods_num = goods_dict["total"] + item["num"]
                goods_item.update(total=goods_num)
            else:
                Warehouse.create(goods_id=item["goods_id"], total=item["num"])


"""
获取未全部出库的入库单列表
"""


def get_filtered_in_list():
    items = (
        WarehouseIn.query.filter(WarehouseIn.out_num < WarehouseIn.in_num)
        .with_entities(
            WarehouseIn.id,
            WarehouseIn.goods_id,
            WarehouseIn.out_num,
            WarehouseIn.in_num,
            WarehouseIn.price,
            WarehouseIn.in_type,
            (WarehouseIn.in_num - WarehouseIn.out_num).label("exist_num"),
        )
        .all()
    )
    filtered_in_list = WarehouseInSchema(many=True).dump(items)

    return filtered_in_list


"""
获取出库批次
goods_id: 商品ID
out_total: 出库总数
in_list: 未全部出库的入库单信息
"""


def get_out_batches(goods_id: int, out_total: int, in_list):
    # in_num = exit_num + out_num
    filter_list = list(filter(lambda item: item["goods_id"] == goods_id, in_list))
    batches = []
    total = 0
    index = 0
    print(out_total, total)
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


"""
将入参转换为入库对应参数
"""


def convert_out_list(out_list, out_code: str):
    return list(map(lambda item: {**item, "out_num": item["num"], "out_code": out_code}, out_list))


"""
入库请求参数 => 库存表参数
"""


def convert_in2total(goods_list):
    return list(map(lambda item: {"goods_id": item["goods_id"], "num": item["in_num"]}, goods_list))


"""
出库请求参数 => 库存明细表
"""


def convert_out2history(goods_list, out_code: str):
    return list(
        map(
            lambda item: {
                "goods_id": item["goods_id"],
                "num": item["out_num"],
                "price": item["price"],
                "code": out_code,
                "type": WarehouseAction.out,
            },
            goods_list,
        )
    )


"""
入库请求参数 => 库存明细表
"""


def convert_in2history(in_list):
    return list(
        map(
            lambda item: {
                "goods_id": item["goods_id"],
                "num": item["in_num"],
                "price": item["price"],
                "code": item["in_code"],
                "type": item["in_type"],
            },
            in_list,
        )
    )


"""
判断出库总数是否超出库存数量
"""


def out_of_range(out_list):
    for item in out_list:
        result = Warehouse.query.with_entities(Warehouse.total).filter_by(goods_id=item["goods_id"]).one()
        print(item["num"], result.total)
        if item["num"] > result.total:
            return True
    return False

"""
获取明细表信息
"""
def get_history_list(args):
    q = (
        WarehouseHistory.query.outerjoin(Goods, WarehouseHistory.goods_id == Goods.id)
            .outerjoin(GoodsType, Goods.type_id == GoodsType.id)
            .with_entities(
            WarehouseHistory.id,
            WarehouseHistory.goods_id,
            Goods.name.label("goods_name"),
            Goods.type_id,
            GoodsType.name.label("type_name"),
            WarehouseHistory.type.label("operation"),
            WarehouseHistory.created_time.label("date"),
            WarehouseHistory.num,
        )
    )
    if args.get("start_date") and args.get("end_date"):
        q = q.filter(WarehouseHistory.created_time >= args["start_date"]).filter(
            WarehouseHistory.created_time <= args["end_date"]
        )
    if args.get("word"):
        q = q.filter(Goods.name.like(f"%{args['word']}%"))
    if args.get("type_id"):
        q = q.filter(Goods.type_id == args["type_id"])
    if args.get("type"):
        q = q.filter(WarehouseHistory.type == args["type"])
    count = q.count()
    offset = (args["page_index"] - 1) * args["page_size"]
    items = q.offset(offset).limit(args["page_size"]).all()
    result = WarehouseHistorySchema(many=True).dump(items)

    return {
        'total': count,
        'items': result
    }