# coding=utf-8
import socket

from shopping_store.db_handler.myql_db import MysqlDB
from shopping_store.lib.project import (
    match_pn,
    change_point_func,
)
from shopping_store.settings import ADMIN_SOCKET_SERVER_ADDR


class AdminPrintHandler:
    def __init__(self):
        pass

    def main_menu(self):
        """
        开始打印信息
        :return:
        """
        print("""
        ************************
        您要做什么？
        1、管理员注册
        2、管理员登录
        ************************
        """)

    def admin_menu(self):
        """
        管理员菜单打印信息
        :return:
        """
        print("""
        ************************
        您要做什么？
        1、获取商品信息列表
        2、添加新商品
        3、调整商品库存
        4、查看订单列表
        5、商品下架
        6、计算收益
        7、添加收银员
        ************************
        """)

    def error_input(self):
        print("""
        您的输入有误！请重新输入！
        """)

    def error_pn(self):
        print("""
        对不起！请输入正确的手机号！
        """)

    def exist_pn(self):
        print("""
        对不起，您的手机号已经被注册！请勿重复注册！
        """)

    def password_compare_error(self):
        print("""
        对不起，两次输入密码不一致！
        """)


class AdminHandler:
    def __init__(self):
        self.db = MysqlDB()
        self.aph = AdminPrintHandler()

        # 主函数方法映射
        self.start_menu_map = {
            "1": "register",  # 注册
            "2": "login",  # 登录
        }
        # 管理员菜单函数映射
        self.admin_menu_map = {
            "1": "get_product_list",  # 获取商品信息列表
            "2": "add_product",  # 添加新商品
            "3": "change_product_count",  # 调整商品库存
            "4": "get_order_list",  # 查看订单列表
            "5": "remove_product",  # 商品下架
            "6": "check_profit",  # 计算收益
            "7": "add_cashier",  # 添加结算员
            "8": "lacked_product_list",  # 缺货库存列表
            "9": "get_order_detail",  # 查看订单详情
        }

        # 创建UPD Socket连接
        self.create_udp_socket()
        self.__admin_user_tag = False

    def create_udp_socket(self):
        """
        创建UDP socket连接
        :return:
        """
        self.skfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skfd.bind(ADMIN_SOCKET_SERVER_ADDR)

    def check_admin_pn(self, pn):
        if not self.db.user_register_cheker(pn, 1):
            self.aph.exist_pn()
            self.start()

        if not match_pn(pn):
            self.aph.error_pn()
            self.start()

    def register(self):
        """
        用户注册
        :return:
        """
        pn = input("请输入手机号：")
        self.check_admin_pn(pn)
        name = input("请输入姓名：")
        # password = getpass.getpass("请输入密码：")
        password1 = input("请输入密码：")
        password2 = input("请再输入一次密码：")
        if password1 != password2:
            self.aph.password_compare_error()
            self.start()

        status, msg = self.db.user_register(name, password1, pn, role=1)
        print(msg)

    def login(self):
        """
        用户登录
        :return:
        """
        pn = input("请输入手机号：")
        # password = getpass.getpass("请输入密码：")
        password = input("请输入密码：")
        status, msg = self.db.user_login(pn, password)
        print(msg)

        if status:
            # 登录成功
            self.admin_menu_handler()
            self.__admin_user_tag = True
        else:
            # 登录失败
            self.start()

    def get_product_list(self):
        pass

    def add_product(self):
        pass

    def change_product_count(self):
        pass

    def get_order_list(self):
        pass

    def check_profit(self):
        pass

    def add_cashier(self):
        pass

    def lacked_product_list(self):
        pass

    def get_order_detail(self):
        pass

    def remove_product(self):
        product_id = input("请输入下架商品的ID：")
        print(self.db.remove_db_product(product_id))

    def admin_menu_handler(self):
        """
        登录成功后主菜单
        :return:
        """
        self.aph.admin_menu()
        user_input = input(">>")
        point_func = self.admin_menu_map.get(user_input)
        if not point_func:
            self.aph.error_input()
        else:
            eval(change_point_func(point_func))

    def wating_for_socket_msg(self):
        """
        UDP等待接收消息
        :return:
        """
        while True:
            data, addr = self.skfd.recvfrom(1024)
            print("您有新的消息！来自{}，消息内容：{}".format(addr, data.decode()))
            # request_mode, content = self.get_request(data)
            # print(request_mode)

    def start(self):
        """
        启动函数
        :return:
        """
        while True:
            self.aph.main_menu()
            user_input = input(">>")
            point_func = self.start_menu_map.get(user_input, False)
            if not point_func:
                self.aph.error_input()
            else:
                eval(change_point_func(point_func))
