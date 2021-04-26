import typing
from flask_restful import Resource
from marshmallow import ValidationError

from app.common.models.goods import GoodsType, Goods
from app.goods.schema import GoodsTypeSchema, GoodsSchema
from patch import fields, parse
from utils.http import ApiResponse


class GoodsResource(Resource):
    @parse({"name": fields.String(required=True), "type_id": fields.Integer(required=True)})
    def post(self, args: typing.Dict):
        """新增商品"""
        try:
            q = Goods.create(**args)
            q.commit()
            return ApiResponse.success()
        except ValidationError as e:
            return ApiResponse.error(str(e), 400)


class GoodsListResource(Resource):
    @parse(
        {
            "page_index": fields.Integer(missing=1),
            "page_size": fields.Integer(missing=10),
            "word": fields.String(missing=""),
            "type_id": fields.Integer()
        }
    )
    def get(self, args: typing.Dict):
        """商品列表"""
        q = Goods.query \
            .join(GoodsType, Goods.type_id == GoodsType.id)
        if args['word']:
            q = q.filter(Goods.name.like(f"%{args['word']}%"))
        if (args.get('type_id')):
            q = q.filter(Goods.type_id == args['type_id'])
        count = q.count()
        offset = (args['page_index'] - 1) * args['page_size']
        items = q.offset(offset).limit(args['page_size']).all()
        result = GoodsSchema(many=True).dump(items)
        return ApiResponse.success({
            'total': count,
            'items': result
        })


class GoodsItemResource(Resource):
    @parse({"name": fields.String(required=True)})
    def put(self, args: typing.Dict, goods_id):
        """修改商品"""
        pass;

    def delete(self, goods_id):
        """删除商品"""
        item = Goods.query.filter_by(id=goods_id).one()
        item.delete()
        item.commit()
        return ApiResponse.success()

class GoodsTypeResource(Resource):
    @parse({"name": fields.String(required=True)})
    def post(self, args: typing.Dict):
        """新增分类"""
        q = GoodsType.create(**args)
        q.commit()

        return ApiResponse.success()


class GoodsTypeItemResource(Resource):
    @parse({"name": fields.String(required=True)})
    def put(self, args: typing.Dict, type_id):
        """修改分类"""
        pass;

    def delete(self, type_id: int):
        """删除分类"""
        goods_item = Goods.query.filter_by(type_id=type_id).first()
        if goods_item:
            return ApiResponse.error('该商品分类存在商品，无法删除')

        item = GoodsType.query.filter_by(id=type_id)
        item.delete()
        return ApiResponse.success()

class GoodsTypeListResource(Resource):
    @parse(
        {
            "page_index": fields.Integer(missing=1),
            "page_size": fields.Integer(missing=10),
            "word": fields.String(missing=""),
        }
    )
    def get(self, args: typing.Dict):
        """分类列表"""
        offset = (args['page_index'] - 1) * args['page_size']
        q = GoodsType.query
        if args['word']:
            q = q.filter(GoodsType.name.like(f"%{args['word']}%"))
        count = q.count()
        items = q.offset(offset).limit(args['page_size']).all()
        result = GoodsTypeSchema(many=True).dump(items)
        return ApiResponse.success({
            'total': count,
            'items': result
        })