from sqlalchemy import Column, SmallInteger, Boolean, String, Integer

from database.base_model import BaseModel
from database.mysql_db import db


class Project(BaseModel):
    """
    项目
    """

    __tablename__ = "project"
    name = Column(String(30), nullable=False, index=True, comment="项目名称")
    project_manager_ids = Column(String(60), nullable=True, comment="项目经理id")
    developer_ids = Column(String(60), nullable=True, comment="开发人员id")
    ops_ids = Column(String(60), nullable=True, comment="运维人员id")
    server_id = Column(Integer, nullable=False, comment="服务器id")
    deploy_address = Column(String(100), nullable=False, comment="项目部署地址根目录")
    docker_network = Column(SmallInteger, nullable=False, comment="docker network网络")
    is_locked = Column(Boolean, default=False, nullable=False, comment="项目状态")
    servers = db.relationship(
        "Server_Project",
        back_populates="project_relation",
        primaryjoin="and_(Project.id==Server_Project.project_id)",
        lazy=True,
    )
