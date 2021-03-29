from enum import Enum

"""
入库类型：
0:采购入库
1:盘盈入库
2:赠送入库
"""


class WarehouseOperationType(str, Enum):
    purchase = 0
    gift = 1
    surplus = 2
    out = 3
