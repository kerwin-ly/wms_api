from app.common.models.warehouse import Warehouse, WarehouseIn, WarehouseHistory, WarehouseOut


class WarehouseSchema(Warehouse.schema_class):
    class Meta:
        fields = ("id", "goods_id", "total", "goods_name", "type_id", "type_name", "num")


class WarehouseInSchema(WarehouseIn.schema_class):
    class Meta:
        fields = (
            "id",
            "goods_id",
            "total",
            "goods_name",
            "type_id",
            "type_name",
            "price",
            "in_num",
            "in_type",
            "in_code",
            "in_date",
            "exist_num",
        )


class WarehouseHistorySchema(WarehouseHistory.schema_class):
    class Meta:
        fields = ("id", "goods_id", "goods_name", "type_id", "type_name", "operation", "date", "num", "price")


class WarehouseInSchema(WarehouseHistory.schema_class):
    class Meta:
        fields = (
            "id",
            "goods_id",
            "goods_name",
            "type_id",
            "type_name",
            "price",
            "in_num",
            "in_type",
            "in_code",
            "in_date",
        )


class WarehouseSchema(Warehouse.schema_class):
    class Meta:
        fields = ("id", "goods_id", "goods_name", "type_id", "type_name", "cost", "num")


class WarehouseOutSchema(WarehouseOut.schema_class):
    class Meta:
        fields = ("id", "goods_id", "goods_name", "type_id", "type_name", "out_num", "out_code", "out_date", "out_cost")
