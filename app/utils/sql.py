import os
import configparser
import pymysql

from config.settings import ROOT_DIR

db = None


def get_db_config():
    config_path = os.path.join(ROOT_DIR, "config", "sql.ini")
    conf = configparser.ConfigParser()
    conf.read(config_path)
    print("conf", conf, config_path)

    return {
        "host": conf.get("database", "host"),
        "port": conf.getint("database", "port"),
        "user": conf.get("database", "user"),
        "pwd": conf.get("database", "pwd"),
        "db": conf.get("database", "db"),
        "charset": conf.get("database", "charset"),
    }


class SQLManager(object):
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        DB_CONFIG = get_db_config()
        self.conn = pymysql.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            passwd=DB_CONFIG["pwd"],
            db=DB_CONFIG["db"],
            use_unicode=True,
            charset=DB_CONFIG["charset"]
        )
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 查询多条数据
    def get_list(self, sql, args=None):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchall()
        return result

    # 查询单条数据
    def get_one(self, sql, args=None):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchone()
        return result

    # 执行单条SQL语句
    def moddify(self, sql, args=None):
        self.cursor.execute(sql, args)
        self.conn.commit()

    # 执行多条SQL语句
    def multi_excute(self, sql, args=None):
        self.cursor.executemany(sql, args)
        self.conn.commit()
        print(dict(self.cursor))

    # 创建单条记录的语句
    def create(self, sql, args=None):
        self.cursor.execute(sql, args)
        self.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    # 关闭数据库cursor和连接
    def close(self):
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


sql_manager = SQLManager()
