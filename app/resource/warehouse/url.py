from . import api, view

api.add_resource(view.WarehouseList, "/list")
api.add_resource(view.WarehouseBatch, "/batch")
api.add_resource(view.WarehouseInList, "/in/list")
api.add_resource(view.WarehouseIn, "/in")
api.add_resource(view.WarehouseOut, "/out")
api.add_resource(view.WarehouseOutList, "/out/list")
api.add_resource(view.WarehouseOutBatch, "/out/batch")
api.add_resource(view.WarehouseHistory, "/history")
