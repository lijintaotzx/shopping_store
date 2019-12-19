# coding=utf-8
import socket

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.settings import CASHIER_SOCKET_SERVER_ADDR


class CustomerPrintHandler:
    def __init__(self):
        pass


class CustomerHandler:
    def __init__(self):
        self.db = MysqlDB()
        self.aph = CustomerPrintHandler()

        # 主函数映射方法
        self.start_menu_map = {
            "1": "register",  # 注册
            "2": "login",  # 登录
        }

        # 用户菜单函数映射
        self.customer_menu_map = {
            "1": "add_product",  # 添加商品到购物车
            "2": "remove_product",  # 从购物车中移除商品
            "3": "get_my_orders",  # 查看我的购物车
            "4": "paying",  # 发起结算
        }
        # 创建TCP Socket连接
        self.create_tcp_socket()

    def create_tcp_socket(self):
        self.skfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skfd.connect(CASHIER_SOCKET_SERVER_ADDR)
