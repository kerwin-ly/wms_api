from sqlalchemy import Column, Integer, ForeignKey

from database.base_model import BaseModel
from database.mysql_db import db


class Server_Project(BaseModel):
    """
    服务器-项目 中间关系表
    """

    __tablename__ = "server_project"
    server_id = Column(Integer, ForeignKey("server.id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
    server_relation = db.relationship(
        "Server", back_populates="projects", primaryjoin="and_(Server.id==Server_Project.server_id)", lazy=True
    )
    project_relation = db.relationship(
        "Project", back_populates="servers", primaryjoin="and_(Project.id==Server_Project.project_id)", lazy=True
    )
