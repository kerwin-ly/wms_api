import typing
from flask_restful import Resource

from app.common.models.project import Project
from app.common.models.server import Server
from app.server.schema import ServerSchema, ServerItemSchema
from patch import fields, parse
from utils.http import ApiResponse


class ServerAddResource(Resource):
    @parse(
        {
            "name": fields.String(required=True),
            "username": fields.String(required=True),
            "ip": fields.String(required=True),
            "port": fields.Integer(required=True),
            "password": fields.String(required=True),
            "action": fields.String(required=True, validate=lambda x: x in ("test", "save")),
        }
    )
    def post(self, args: typing.Dict):
        """
        测试/新增服务
        """
        params = {key: value for key, value in args.items() if key != 'action'}
        if args["action"] == "save":
            job = Server.create(**params)
            job.commit()
        elif args['action'] == 'test':
            # 测试服务器连接状态
            pass;

        return ApiResponse.success()

class ServerItemResource(Resource):
    @parse({
        "name": fields.String(required=True),
        "username": fields.String(required=True),
        "password": fields.String(required=True)
    })
    def put(self, args: typing.Dict, server_id: int):
        """
        修改服务器信息
        """
        data = Server.query.filter_by(id=server_id).one()
        data.update(**args)
        data.commit()
        return ApiResponse.success()


    def get(self, server_id: int):
        """
        服务器详情
        """
        data = Server.query.filter(server_id == Server.id).one()
        result = ServerSchema().dump(data)

        return ApiResponse.success(result)

    def delete(self, server_id: int):
        """
        删除服务器
        """
        matched_list = Server.query \
            .join(Project, Server.id == Project.server_id) \
            .filter(Server.id == server_id).all()
        if len(matched_list):
            return ApiResponse.error('当前服务器上已部署项目，无法删除')
        data = Server.query.filter_by(id=int(server_id)).first()
        if not data:
            return ApiResponse.error(f"id={server_id}数据不存在")
        data.delete()
        data.commit()
        return ApiResponse.success()

class ServerListResource(Resource):
    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "word": fields.String(missing=""),
        }
    )
    def get(self, args: typing.Dict):
        """服务器列表"""
        page_index = int(args["page_index"])
        page_size = int(args["page_size"])
        offset = (page_index - 1) * page_size
        word = args.get("word")
        query_case = []
        if word:
            query_case.append(Server.name.like(f"%{word}%"))
        server_list = Server.query.filter(*query_case).limit(page_size).offset(offset).all()
        result = ServerItemSchema(many=True).dump(server_list)

        return ApiResponse.success({"items": result, "total": Server.query.filter(*query_case).count()})

