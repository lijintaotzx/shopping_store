# coding=utf-8
from shopping_store.lib.logger import Log

mysql_logger = Log("mysql_error")


def try_db_sql(func):
    def wapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as err:
            mysql_logger.info(err)
            return "MySQL数据库异常！"
        return result

    return wapper
