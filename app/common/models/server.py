
from sqlalchemy import String, SmallInteger
from sqlalchemy.schema import Column

from database.base_model import BaseModel
from database.mysql_db import db


class Server(BaseModel):
    """
    服务器
    """

    __tablename__ = "server"
    name = Column(String(30), nullable=False, index=True, comment="服务器名称")
    username = Column(String(30), nullable=False, comment="服务器登录用户名")
    ip = Column(String(20), nullable=False, comment="IP地址")
    port = Column(SmallInteger, nullable=False, comment="端口号")
    password = Column(String(64), nullable=False, comment="账户密码")
    projects = db.relationship(
        "Server_Project",
        back_populates="server_relation",
        primaryjoin="and_(Server.id==Server_Project.server_id)",
        lazy=True,
    )
