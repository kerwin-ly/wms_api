"""
flask 初始化
"""
import logging
import json
import typing

from flask import Flask, request, Response
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.exceptions import HTTPException

from utils.http import ApiResponse
from utils.logger import logger, log_err

logging.getLogger("werkzeug").disabled = False


def register_api_handler(app: Flask) -> None:
    @app.before_request
    def before_request():
        data = json.loads(request.data) if request.data else {}
        data.update(request.args)
        data.update(dict(request.form))
        setattr(request, "bjson", data)
        logger.debug(f"url:{request.path}, params:{json.dumps(data)}")

    @app.after_request
    def after_request(response):
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        allow_headers = "Content-Type, Authorization, token"
        response.headers.add("Access-Control-Allow-Headers", allow_headers)
        if "Access-Control-Allow-Credentials" not in response.headers:
            response.headers.add("Access-Control-Allow-Credentials", "true")

        logger.debug(f"url:{request.path}, response:{response.json}")

        return response

    @app.errorhandler(404)
    @log_err
    def not_found(err: HTTPException) -> typing.Tuple[Response, typing.Optional[int]]:
        return ApiResponse.error("Not Found", err.code)

    @app.errorhandler(422)
    @app.errorhandler(400)
    @log_err
    def bad_request(err: HTTPException) -> typing.Tuple[Response, typing.Optional[int]]:
        return ApiResponse.error("Bad Request", err.code)

    @app.errorhandler(ValidationError)
    @log_err
    def validation_error(err: ValidationError) -> typing.Tuple[Response, typing.Optional[int]]:
        return ApiResponse.error(err.messages, 400)

    @app.errorhandler(NoResultFound)
    @log_err
    def no_result_found(err: NoResultFound) -> typing.Tuple[Response, typing.Optional[int]]:
        return ApiResponse.error(str(err), 400)

    @app.errorhandler(Exception)
    @log_err
    def err_not_catch(err: Exception) -> typing.Tuple[Response, typing.Optional[int]]:
        from database.mysql_db import session

        session.rollback()
        return ApiResponse.error("服务器内部错误或网络错误" + str(err), 500)
