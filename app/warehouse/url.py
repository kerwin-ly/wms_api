from . import api, view

api.add_resource(view.WarehouseList, "/list")
api.add_resource(view.WarehouseBatch, "/batch")
api.add_resource(view.WarehouseInList, "/in/list")
api.add_resource(view.WarehouseItemIn, "/in")
api.add_resource(view.WarehouseItemOut, "/out")
api.add_resource(view.WarehouseOutList, "/out/list")
api.add_resource(view.WarehouseOutBatch, "/out/batch")
api.add_resource(view.WarehouseItemHistory, "/history")
api.add_resource(view.WarehouseOutDownload, "/out/download")
api.add_resource(view.WarehouseHistoryDownload, "/history/download")
api.add_resource(view.WarehouseInDownload, "/in/download")
