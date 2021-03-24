from . import api, view

api.add_resource(view.WarehouseInList, "/in/list")
api.add_resource(view.WarehouseIn, "/in")
api.add_resource(view.WarehouseOut, "/out")
