"""
和网络相关的封装。

HttpResponse：
    用作所有的接口数据返回。
"""
from flask import jsonify


class ApiResponse(object):
    @staticmethod
    def success(data={}):
        res = jsonify({"code": 200, "msg": "success", "data": data})
        return res

    @staticmethod
    def error(msg: str, code=-1):
        res = jsonify({"code": code, "msg": msg, "data": {}})
        return res


