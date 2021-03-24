from collections import OrderedDict

"""将数组对象按序转换为远组"""


def convert_arrobj_to_tuple(extra_params):
    return tuple(map(lambda item: tuple(OrderedDict(item).values()), extra_params))
