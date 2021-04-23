from app.common.models.server import Server

"""服务器列表"""
class ServerItemSchema(Server.schema_class):

    class Meta:
        fields = ("id", "name", "ip", "port", "username")

"""服务器详情"""
class ServerSchema(Server.schema_class):

    class Meta:
        fields = ("id", "name", "ip", "port", "username", "password")