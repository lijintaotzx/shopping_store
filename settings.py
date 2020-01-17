# coding=utf-8

# MySQL相关配置信息
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASSWORD = "123456"
DATABASE = 'shopping_store'
CHARSET = 'utf8'

# Socket相关配置信息
ADMIN_SOCKET_SERVER_ADDR = ("0.0.0.0", 10022)
CASHIER_SOCKET_SERVER_ADDR = ("0.0.0.0", 10023)

# 异常日志文件路径
LOG_PATH = {
    "mysql_error": "/Users/tzx/test/tn/mysql_error.log",
    "shopping_store_error": "/Users/tzx/test/tn/shopping_store_error.log"
}

# 缺货库存输出文件路径
LACKED_PRODUCT_PATH = "/Users/tzx/test/shopping_store/"
USER_TICKET_PATH = "/Users/tzx/test/shopping_store/"
