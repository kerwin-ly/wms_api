import datetime
import typing

now: typing.Callable = datetime.datetime.now


def get_now_with_format(format_string: str = "%Y%m%d%H%M%S") -> str:
    return now().strftime(format_string)


def get_today_from_now():
    return now().strftime("%Y-%m-%d")


def time_to_str_with_format(t):
    return t.strftime("%Y-%m-%d")
