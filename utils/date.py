import datetime
import time


def now_date(format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(format)


"""转换为毫秒时间戳"""


def to_timestamp(date: str, format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(date, format)) * 1000
