from sqlalchemy import Column, Integer, SmallInteger, String, Enum, text, Float
from app.common.types.warehouse import WarehouseAction
from database.base_model import BaseModel


class Warehouse(BaseModel):
    """
    库存表
    """

    __tablename__ = "warehouse"
    goods_id = Column(Integer, nullable=False, comment="商品ID")
    total = Column(SmallInteger, nullable=False, comment="商品库存总量")

    def query_goods_total(self, goods_id):
        item = self.query.filter_by(goods_id=goods_id).one()
        return item.total


class WarehouseIn(BaseModel):
    """
    入库表
    """

    __tablename__ = "warehouse_in"
    goods_id = Column(Integer, nullable=False, comment="商品ID")
    price = Column(Float, nullable=False, comment="商品单价")
    in_num = Column(SmallInteger, nullable=False, comment="入库数量")
    in_type = Column(Enum(WarehouseAction))
    in_code = Column(String(30), nullable=False, comment="入库单号")
    out_num = Column(SmallInteger, server_default=text("0"), comment="已出库数量")


class WarehouseOut(BaseModel):
    """
    出库表
    """

    __tablename__ = "warehouse_out"
    goods_id = Column(Integer, nullable=False, comment="商品ID")
    out_code = Column(String(30), nullable=False, comment="出库单号")
    out_num = Column(SmallInteger, nullable=False, comment="出库总数")


class WarehouseHistory(BaseModel):
    """
    库存明细表
    """

    __tablename__ = "warehouse_history"
    goods_id = Column(Integer, nullable=False, comment="商品ID")
    num = Column(SmallInteger, nullable=False, comment="出入库数量")
    type = Column(Enum(WarehouseAction))
    price = Column(Float, nullable=False, comment="商品单价")
    code = Column(String(30), nullable=False, comment="出入库单号")
