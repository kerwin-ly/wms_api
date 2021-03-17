from enum import Enum


class EntityWarehouseIn(str, Enum):
    purchase = 0,
    gift = 1,
    surplus = 2
