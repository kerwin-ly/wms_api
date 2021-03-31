from enum import Enum


class EntityWarehouseIn(str, Enum):
    purchase = 0
    gift = 1
    surplus = 2
    out = 3

MapWarehouseOperation = {
    '0': '采购入库',
    '1': '盘盈入库',
    '2': '赠送入库',
    '3': '出库'
}
