"""
更新明细表
"""
from collections import OrderedDict
from sqlalchemy import cast, Float, func, and_
from app.common.models.goods import Goods, GoodsType
from app.common.models.warehouse import WarehouseIn, Warehouse, WarehouseHistory, WarehouseOut
from app.common.types.warehouse import WarehouseAction
from app.warehouse.schema import WarehouseInSchema, WarehouseSchema, WarehouseHistorySchema, WarehouseOutSchema
from database.mysql_db import session

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
            goods_num = goods_item.total - item["num"]
            goods_item.update(total=goods_num)
    elif type == "in":
        for item in goods_list:
            goods_item = Warehouse.query.filter_by(goods_id=item["goods_id"]).first()
            if goods_item:
                goods_num = goods_item.total + item["num"]
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
    filter_list = list(filter(lambda item: item["goods_id"] == goods_id, in_list))
    batches = []
    total = 0
    index = 0
    while out_total > total:
        exist_num = filter_list[index]["exist_num"]
        if total + exist_num > out_total:
            current_out = out_total - total
        else:
            current_out = exist_num

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
                "type": item['in_type'],
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
        if item["num"] > result.total:
            return True
    return False


"""
获取明细表信息
"""


def get_history_list(args):
    q = WarehouseHistory.query \
        .outerjoin(Goods, WarehouseHistory.goods_id == Goods.id) \
        .outerjoin(GoodsType, Goods.type_id == GoodsType.id) \
        .with_entities(
            WarehouseHistory.id,
            WarehouseHistory.goods_id,
            Goods.name.label("goods_name"),
            Goods.type_id,
            GoodsType.name.label("type_name"),
            WarehouseHistory.type.label("operation"),
            func.date_format(WarehouseHistory.created_time, '%Y-%m-%d %H:%i:%S').label('date'),
            WarehouseHistory.num,
            WarehouseHistory.code,
            cast(WarehouseHistory.price, Float),
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
    q = q.order_by(WarehouseHistory.created_time.desc())
    count = q.count()
    offset = (args["page_index"] - 1) * args["page_size"]
    items = q.offset(offset).limit(args["page_size"]).all()
    result = WarehouseHistorySchema(many=True).dump(items)
    result_list = list(map(lambda x: {**x, "state": 'out' if x['code'].startswith('out') else 'in'},result))

    return {"total": count, "items": result_list}


"""
获取入库列表
"""


def get_in_list(args):
    q = WarehouseIn.query.outerjoin(Goods, WarehouseIn.goods_id == Goods.id) \
        .outerjoin(GoodsType, Goods.type_id == GoodsType.id) \
        .with_entities(
            WarehouseIn.id,
            WarehouseIn.goods_id,
            Goods.name.label("goods_name"),
            Goods.type_id,
            GoodsType.name.label("type_name"),
            WarehouseIn.in_type,
            WarehouseIn.in_code,
            WarehouseIn.price,
            WarehouseIn.in_num,
            func.date_format(WarehouseIn.created_time, '%Y-%m-%d %H:%i:%S').label('in_date'),
        )


    if args.get("start_date") and args.get("end_date"):
        q = q.filter(WarehouseIn.created_time >= args["start_date"]).filter(
            WarehouseIn.created_time <= args["end_date"]
        )
    if args.get("word"):
        q = q.filter(Goods.name.like(f"%{args['word']}%"))
    if args.get("type_id"):
        q = q.filter(Goods.type_id == args["type_id"])
    if args.get("type"):
        q = q.filter(WarehouseIn.in_type == args["in_type"])
    q = q.order_by(WarehouseIn.created_time.desc())
    count = q.count()
    offset = (args["page_index"] - 1) * args["page_size"]
    items = q.offset(offset).limit(args["page_size"]).all()
    result = WarehouseInSchema(many=True).dump(items)

    return {"total": count, "items": result}


"""
出库列表
"""


def get_out_list(args):
    subq = WarehouseHistory.query.filter(WarehouseHistory.code.like((f"out%"))) \
        .with_entities(
            WarehouseHistory.goods_id,
            WarehouseHistory.code,
            func.sum(WarehouseHistory.num * WarehouseHistory.price).label("out_cost"),
        ) \
        .group_by(WarehouseHistory.code, WarehouseHistory.goods_id)\
        .subquery()

    q = WarehouseOut.query.outerjoin(Goods, WarehouseOut.goods_id == Goods.id) \
        .outerjoin(GoodsType, Goods.type_id == GoodsType.id) \
        .outerjoin(subq, and_(subq.c.code == WarehouseOut.out_code, subq.c.goods_id == WarehouseOut.goods_id)) \
        .with_entities(
            WarehouseOut.id,
            WarehouseOut.goods_id,
            Goods.name.label("goods_name"),
            Goods.type_id,
            GoodsType.name.label("type_name"),
            WarehouseOut.out_num,
            WarehouseOut.out_code,
            func.date_format(WarehouseOut.created_time, '%Y-%m-%d %H:%i:%S').label('out_date'),
            subq.c.out_cost
        )

    if args.get("start_date") and args.get("end_date"):
        q = q.filter(WarehouseIn.created_time >= args["start_date"]).filter(
            WarehouseIn.created_time <= args["end_date"]
        )
    if args.get("word"):
        q = q.filter(Goods.name.like(f"%{args['word']}%"))
    if args.get("type_id"):
        q = q.filter(Goods.type_id == args["type_id"])
    q = q.order_by(WarehouseOut.created_time.desc())
    count = q.count()
    offset = (args["page_index"] - 1) * args["page_size"]
    items = q.offset(offset).limit(args["page_size"]).all()
    result = WarehouseOutSchema(many=True).dump(items)
    return {
        'total': count,
        'items': result
    }
