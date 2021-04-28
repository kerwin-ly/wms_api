from webargs.flaskparser import parser
from marshmallow.base import SchemaABC


def parse(argmap, *args, **kwargs):
    try:
        if isinstance(argmap, SchemaABC):
            argmap = getattr(argmap, "_declared_fields")
        return parser.use_args(argmap, *args, **kwargs)
    except Exception as err:
        raise err
