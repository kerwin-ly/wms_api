from webargs.flaskparser import parser
from marshmallow.base import SchemaABC


@parser.error_handler
def handle_error(err, req, schema, status_code, headers):
    raise err


def parse(argmap, *args, **kwargs):
    if isinstance(argmap, SchemaABC):
        argmap = getattr(argmap, "_declared_fields")
    return parser.use_args(argmap, *args, **kwargs)
