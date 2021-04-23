import typing

from marshmallow import ValidationError, post_load
from marshmallow_sqlalchemy import ModelSchema
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.ext.declarative import declared_attr

from database.db_session import DatabaseOperateMixin
from database.mysql_db import db
from utils.name import camel_to_underline


class ClassProperty(object):
    def __init__(self, fget: typing.Callable):
        self.fget = fget

    def __get__(self, owner_self: object, owner_cls: type) -> typing.Any:
        return self.fget(owner_cls)


class BaseModel(db.Model, DatabaseOperateMixin):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_updated_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), index=True)
    created_time = Column(DateTime, server_default=func.now())

    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_underline(cls.__name__)

    @ClassProperty
    def schema_class(cls) -> typing.Type[ModelSchema]:
        class Meta(ModelSchema.Meta):
            model = cls
            include_fk = True
            # serializer.session/serializer.opts.sqla_session
            sqla_session = db.session

        return type(f"{cls.__name__}Schema", (ModelSchema,), {"Meta": Meta})

    @property
    def schema(self) -> ModelSchema:
        return self.schema_class()

    @classmethod
    @post_load
    def create(cls, **raw_data) -> db.Model:
        schema = cls.schema_class()
        errors = schema.validate(raw_data)
        if errors:
            raise ValidationError(errors)
        instance = schema.load(raw_data)
        schema.session.add(instance)
        return instance

    @property
    def schema(self) -> ModelSchema:
        return self.schema_class()

    def update(self, **raw_data) -> db.Model:
        data = self.jsonify()
        for key, val in raw_data.items():
            if key in data.keys() and val is not None:
                data[key] = val
        errors = self.schema.validate(data)
        if errors:
            raise ValidationError(errors)
        instance = self.schema.load(data)
        assert instance is self  # ensure
        self.schema.session.add(self)
        return self

    def delete(self) -> None:
        db.session.delete(self)
        self.schema.session.add(self)

    def jsonify(self, *args: typing.Tuple, **kwargs: typing.Dict) -> typing.Dict:
        return self.schema.dump(self, *args, many=False, **kwargs)

    def __str__(self):
        return self.id
