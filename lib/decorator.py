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


def is_admin(admin_tag):
    def check(func):
        def wrapper(*args, **kwargs):
            print(admin_tag)
            if admin_tag:
                re = func(*args, **kwargs)
                return re
            else:
                print("权限不足")
        return wrapper
    return check
