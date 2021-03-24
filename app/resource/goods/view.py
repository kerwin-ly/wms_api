import typing
from flask_restful import Resource
from app.patch import fields, parse
from app.utils.http import ApiResponse
from app.utils.sql import sql_manager


class GoodsResource(Resource):
    @parse({"name": fields.String(required=True)})
    def post(self, args: typing.Dict):
        """新增类目"""
        try:
            name = str(args["name"])
            result = sql_manager.create("INSERT INTO goods (name) VALUES (%s)", name)
            return ApiResponse.success({"id": result})
        except Exception as e:
            return ApiResponse.fail("服务端错误" + str(e))


class GoodsListResource(Resource):
    @parse(
        {
            "page_index": fields.String(required=True),
            "page_size": fields.String(required=True),
            "word": fields.String(missing=""),
        }
    )
    def get(self, args: typing.Dict):
        """入库列表"""
        try:
            page_index = int(args["page_index"])
            page_size = int(args["page_size"])
            offset = (page_index - 1) * page_size
            data = sql_manager.get_list(f"""SELECT id, name FROM goods LIMIT {offset},{page_size}""")
            count = sql_manager.get_one("SELECT COUNT(id) FROM goods")
            result = {"total": count["COUNT(id)"], "items": data}

            return ApiResponse.success(result)
        except Exception as e:
            return ApiResponse.fail("服务端错误" + str(e))


class GoodsItemResource(Resource):
    @parse({"name": fields.String(required=True)})
    def put(self, args: typing.Dict, goods_id):
        """修改类目"""
        try:
            name = args["name"]
            sql_manager.moddify("UPDATE goods SET name = %s WHERE id = %s", (name, goods_id))
            return ApiResponse.success(None)
        except Exception as e:
            ApiResponse.fail("服务端错误" + str(e))

    def delete(self, goods_id):
        """删除类目"""
        try:
            sql_manager.moddify(f"""DELETE from goods WHERE id={goods_id}""")
            return ApiResponse.success(None)
        except Exception as e:
            ApiResponse.fail("服务端错误" + str(e))
