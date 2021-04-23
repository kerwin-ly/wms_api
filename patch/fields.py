import typing
import collections

import marshmallow
from werkzeug.datastructures import FileStorage
from marshmallow.base import SchemaABC
from marshmallow.fields import Raw, String, Integer, List, Boolean, DateTime, Nested as _Nested


class Nested(_Nested):
    def __init__(self, nested: typing.Union[typing.Dict, SchemaABC, type, str], *args, **kwargs):
        if isinstance(nested, dict):
            nested = marshmallow.Schema.from_dict(nested)
        super().__init__(nested, *args, **kwargs)  # type: ignore


class Dict(Raw):
    default_error_messages = {"invalid": "Not a valid dict."}

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, collections.Mapping):
            raise self.make_error("invalid")
        return value


class File(Raw):
    default_error_messages = {"invalid": "Not a valid file."}

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, FileStorage):
            raise self.make_error("invalid")
        return value


__all__ = [
    "String",
    "Integer",
    "List",
    "Boolean",
    "DateTime",
    "Nested",
    "Dict",
    "File",
]
