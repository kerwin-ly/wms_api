import os
import re
import uuid


def get_ext(filename: str) -> str:
    ext = os.path.splitext(filename)[-1]
    if ext and ext[0] == ".":
        ext = ext[1:]
    return ext.lower()


def generate_unique_name(ext: str) -> str:
    return f"{str(uuid.uuid4())}.{ext}"


def camel_to_underline(name: str) -> str:
    s = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s).lower()


def get_unique_name():
    return str(uuid.uuid4())
