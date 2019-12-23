# coding=utf-8
import re
import socket
from _decimal import Decimal

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.lib.project import (
    match_pn,
    change_point_func,
    get_number_input)
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
        5、查看订单详情
        6、商品下架
        7、计算收益
        8、添加收银员
        9、缺货库存列表
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

    def product_detail_for_admin(self, product_detail):
        """
        管理员的商品详情
        :return:
        """
        name, description, source_price, price, product_id, count = product_detail
        result = "商品名：{}，备注：{}，进价：{}，售价：{}，商品id：{}，库存：{} ".format(
            name, description, source_price, price, product_id, count
        )
        print(result)
        return result

    def get_order_list(self, order):
        """
        打印订单列表
        :param order:
        :return:
        """
        user_msg, profit, order_id, cashier_msg, amount, create_time = order
        result = "订单ID：{}，订单金额：{}，订单收益：{}，用户：{}（ID：{}），结算员：{}（ID：{}），订单创建时间：{} ".format(
            order_id,
            amount,
            profit,
            user_msg[1],
            user_msg[0],
            cashier_msg[1],
            cashier_msg[0],
            create_time,
        )
        print(result)

    def get_order_detail(self, order_detail):
        result = "商品ID：{}，商品名称：{}，商品描述：{}，购买数量：{}，购买价格：{}".format(
            *order_detail
        )
        print(result)


class AdminHandler:
    # TODO 设置类变量有问题，暂时没有解决方案
    __admin_user_tag = False

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
            "5": "get_order_detail",  # 查看订单详情
            "6": "remove_product",  # 商品下架
            "7": "check_profit",  # 计算收益
            "8": "add_cashier",  # 添加结算员
            "9": "lacked_product_list",  # 缺货库存列表
        }

        # 创建UPD Socket连接
        self.create_udp_socket()
        # self.__admin_user_tag = False

    def create_udp_socket(self):
        """
        创建UDP socket连接
        :return:
        """
        self.skfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.skfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skfd.bind(ADMIN_SOCKET_SERVER_ADDR)

    def check_pn(self, pn, role):
        if not self.db.user_register_cheker(pn, role):
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
        self.check_pn(pn, 1)
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
            __admin_user_tag = True
            self.admin_menu_handler()
        else:
            # 登录失败
            self.start()

    def check_product_desc(self, desc):
        """
        获取新添商品描述
        :return:
        """
        if not desc:
            desc = "暂无商品描述"
        return desc

    def product_id_str(self, name):
        """
        获取商品ID
        :param name: 商品名称
        :return: 商品ID:数字
        """
        num = 0
        for i in str(name):
            num += ord(i)
        return num

    def price_compare(self, source_price, price):
        """
        比较商品进价，售价大小
        :param source_price: 商品进价
        :param price: 商品售价
        :return: True 或者 False
        """
        return source_price < price

    def get_name(self):
        """
        判断新添商品名称是否重复
        :return: 新添商品名称
        """
        while True:
            name = input("请输入新添商品名称:")
            if not self.db.check_product_name(name):
                print("商品名称重复")
                continue
            else:
                return name

    def get_price(self):
        """
        录入新添商品进价，售价
        :return: 商品进价，售价
        """
        while True:
            source_price = get_number_input("请输入新添商品进价:", is_float=True)
            price = get_number_input("请输入新添商品售价:", is_float=True)
            if not self.price_compare(source_price, price):
                print("售价有误")
                continue
            else:
                return source_price, price

    def add_product(self):
        """
        添加新商品
        :return:商品信息（名称，描述，进价，售价，数量，ID）
        """
        name = self.get_name()
        source_price, price = self.get_price()
        count = get_number_input("请输入数量：")
        description = self.check_product_desc(input("请输入新添商品描述："))
        product_id = self.product_id_str(name)
        print(self.db.add_db_product((name, description, source_price, price, count, product_id)))

    def get_product_list(self):
        """
        获取商品列表（管理员）
        :return:
        """
        data = self.db.get_product_list_db(is_admin=True)
        for product in data:
            self.aph.product_detail_for_admin(product)

    def change_product_count(self):
        """
        修改库存
        :return:
        """
        while True:
            product_id = get_number_input("请输入更改库存的商品的ID(输入q退出)：")
            if product_id == "q":
                break
            if self.db.judge_product_id(product_id):
                change_count = get_number_input("调整商品库存为：")
                self.db.change_product_count_db(product_id, change_count)
            else:
                continue

    # @is_admin(__admin_user_tag)
    def add_cashier(self):
        """
        添加结算员
        :return:
        """
        pn = input("请输入结算员手机号：")
        self.check_pn(pn, 2)
        name = input("请输入结算员姓名：")
        # password = getpass.getpass("请输入密码：")
        password = input("请输入结算员密码：")
        status, msg = self.db.user_register(name, password, pn, role=2)
        print(msg)

    def lacked_product_list(self):
        pass

    def remove_product(self):
        product_id = input("请输入下架商品的ID：")
        print(self.db.remove_db_product(product_id))

    def format_datetime(self, input_date):
        formater = r"^[1-9]\d{0,3}-(1[0-2]|0?[1-9])-(3[01]|[12]\d|0?[1-9])$"
        return re.match(formater, input_date)

    def affirm_time(self):
        """
        匹配返回用户输入的时间段
        :return:
        """
        while True:
            order_begin = input("请输入要查询订单的开始时间:")
            order_end = input("请输入要查询订单的结束时间:")
            if self.format_datetime(order_begin) and self.format_datetime(order_end):
                return order_begin, order_end
            else:
                print("输入有误 !格式:'2019-10-10'!")
                continue

    def get_order_list(self):
        """
        获取订单列表
        :return:
        """
        order_begin, order_end = self.affirm_time()
        data = self.db.get_order_list_db(order_begin, order_end)

        for order in data:
            user_id, profit, order_id, cashier_id, amount, create_time = order
            # 补充订单中用户和结算员的详细信息
            order_info = (
                self.db.get_user_msg_from_id(user_id),  # 根据ID补充用户信息
                profit,
                order_id,
                self.db.get_user_msg_from_id(cashier_id),  # 根据ID补充结算员ID
                amount,
                create_time,
            )

            self.aph.get_order_list(order_info)

    def check_profit(self):
        """
        计算收益(刘梓威)
        """
        order_begin, order_end = self.affirm_time()
        data = self.db.get_order_list_db(order_begin, order_end)
        profit = Decimal(0.00)
        for product in data:
            profit += product[1]

        result = "%s到%s的收益为%s元" % (order_begin, order_end, profit)
        print(result)

    def get_order_detail(self):
        """
        获取订单详情
        :return:
        """
        order_id = get_number_input("请输入订单ID：")
        data = self.db.get_order_details_db(order_id)
        for order_detail in data:
            self.aph.get_order_detail(order_detail)

    def admin_menu_handler(self):
        """
        登录成功后主菜单
        :return:
        """
        while True:
            # TODO 注销退出
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
