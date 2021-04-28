from enum import Enum

"""
入库类型：
purchase:采购入库
surplus:盘盈入库
gift:赠送入库
out:出库
"""


class WarehouseAction(str, Enum):
    purchase = "purchase"
    gift = "gift"
    surplus = "surplus"
    out = "out"
