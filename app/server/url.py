from . import api, view

api.add_resource(view.ServerAddResource, "")
api.add_resource(view.ServerListResource, "/list")
api.add_resource(view.ServerItemResource, "/<int:server_id>")