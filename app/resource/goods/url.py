from . import api, view

api.add_resource(view.GoodsResource, "")
api.add_resource(view.GoodsItemResource, "/<int:goods_id>")
api.add_resource(view.GoodsListResource, "/list")
