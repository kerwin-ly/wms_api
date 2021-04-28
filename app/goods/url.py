from . import api, view

api.add_resource(view.GoodsResource, "")
api.add_resource(view.GoodsItemResource, "/<int:goods_id>")
api.add_resource(view.GoodsListResource, "/list")
api.add_resource(view.GoodsTypeResource, "/type")
api.add_resource(view.GoodsTypeItemResource, "/type/<int:type_id>")
api.add_resource(view.GoodsTypeListResource, "/type/list")
