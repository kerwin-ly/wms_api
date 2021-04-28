from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database.base_model import BaseModel


class GoodsType(BaseModel):
    """
    商品分类表
    """

    __tablename__ = "goods_type"
    name = Column(String(30), nullable=False, index=True, comment="商品分类名称")
    goods = relationship(
        "Goods",
        back_populates="goods_type",
        primaryjoin="and_(GoodsType.id==Goods.type_id)",
        lazy=True,
    )


class Goods(BaseModel):
    """
    商品表
    """

    __tablename__ = "goods"
    name = Column(String(30), nullable=False, index=True, comment="商品名称")
    type_id = Column(Integer, ForeignKey("goods_type.id"), nullable=False, comment="商品分类ID")
    goods_type = relationship("GoodsType", back_populates="goods")
