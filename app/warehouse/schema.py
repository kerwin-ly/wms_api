from app.common.models.warehouse import Warehouse, WarehouseIn, WarehouseHistory


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
        fields = ("goods_id", "goods_name", "type_id", "type_name", "operation", "date", "num")
