# coding=utf-8
import socket
from _decimal import Decimal

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.lib.logger import Log
from shopping_store.lib.project import get_number_input, change_point_func, get_request, match_pn
from shopping_store.settings import CASHIER_SOCKET_SERVER_ADDR

logger = Log("shopping_store_error")


class CustomerPrintHandler:
    """
    界面菜单打印
    """

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
        1、用户注册
        2、用户登录
        ************************
        """)

    def customer_memu(self):
        """
        用户可操作菜单
        :return:
        """
        print("""
                *******用户操作菜单*******

                1、添加商品到购物车
                2、从购物车中移除商品
                3、查看我的购物车
                4、发起结算

                ************************
                """)

    def error_input(self):
        print("""
        您的输入有误！请重新输入！
        """)

    def connect_to_cashier_error(self):
        print("""
        创建与结算端的TCP连接失败!
        """)

    def paying_error(self, msg):
        print(
            """
            结算失败: {}
            """.format(msg)
        )

    def password_compare_error(self):
        print("""
                对不起，两次输入密码不一致！
                """)

    def error_pn(self):
        print("""
        对不起！请输入正确的手机号！
        """)

    def exist_pn(self):
        print("""
        对不起，您的手机号已经被注册！请勿重复注册！
        """)


class Product:
    """
    商品
    """

    def __init__(self, product_id, name, price, count):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.count = count


class ShoppingCart:
    """
    购物车
    """

    def __init__(self, user_id):
        self.__user_id = user_id
        self.product_list = []

    def my_product_list(self):
        """
        返回购物车中的商品信息
        :return:
        """
        return self.product_list

    def add_product(self, product):
        self.product_list.append(product)

    def remove_product(self, product_id):
        """
        移除商品出购物车
        :param product_id:
        :return:
        """
        for product in self.product_list:
            if product.product_id == product_id:
                self.product_list.remove(product)
                return True, "移除成功！"

        return False, "您的购物车中没有该商品！"


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
        self.user_id = 1
        self.shopping_cart = ShoppingCart(user_id=1)  # TODO 测试代码

    def create_tcp_socket(self):
        try:
            self.skfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.skfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.skfd.connect(CASHIER_SOCKET_SERVER_ADDR)
        except Exception as error:
            self.aph.connect_to_cashier_error()
            logger.error("创建与结算端的TCP连接失败,msg:%s" % error)

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
        self.check_pn(pn, 0)
        name = input("请输入姓名：")
        # password = getpass.getpass("请输入密码：")
        password1 = input("请输入密码：")
        password2 = input("请再输入一次密码：")
        if password1 != password2:
            self.aph.password_compare_error()
            self.start()

        status, msg = self.db.user_register(name, password1, pn)
        print(msg)

    def login(self):
        """
        用户端 用户登录
        :return:
        """
        # 登录成功后，返回登录成功的user_id, 利用user_id实例化用户购物车，ShoppingCart
        pn = input("请输入手机号：")
        password = input("请输入密码：")
        status, msg, user_id = self.db.user_login(pn, password, 0)
        print(msg)
        if status:
            # 登录成功
            while True:
                self.aph.customer_memu()
                user_input = input(">>")
                point_func = self.customer_menu_map.get(user_input)
                if not point_func:
                    self.aph.error_input()
                else:
                    eval(change_point_func(point_func))

    def get_add_product_input(self):
        """
        获取用户添加到购物车的输入商品
        :return:
        """
        while True:
            product_id = get_number_input("请输入购买的商品ID：")
            result = self.db.get_product_msg(product_id)
            if not result:
                print("您输入的商品ID有误！")
                continue
            else:
                product_id, name, description, source_price, price, count = result
                user_input_count = get_number_input("请输入购买的商品个数：")
                if int(count) < user_input_count:
                    print("商品库存不足！")
                    continue
                else:
                    return product_id, name, price, user_input_count

    def add_product(self):
        """
        添加商品到购物车
        :return:
        """
        product_id, name, price, user_input_count = self.get_add_product_input()
        self.shopping_cart.add_product(
            Product(
                product_id=product_id,
                name=name,
                price=price,
                count=user_input_count,
            )
        )
        # print(self.transform_shopping_cards())

    def remove_product(self):
        """
        从购物车中移除商品
        :return:
        """
        product_id = get_number_input("请输入需要移除的商品ID：")
        status, msg = self.shopping_cart.remove_product(product_id)
        print(msg)

    def transform_shopping_cards(self):
        return {
            "user_id": self.user_id,
            "shopping_cards": [
                product.__dict__ for product in self.shopping_cart.product_list
            ]
        }

    def send_shopping_cards(self):
        request_data = "SHOPPING_CARDS {}".format(self.transform_shopping_cards())
        self.skfd.send(request_data.encode())

    def paying(self):
        """
        发起结算
        :return:
        """
        self.create_tcp_socket()
        request_data = "REQUEST {}".format(self.transform_shopping_cards())
        self.skfd.send(request_data.encode())

        status_code, msg = get_request(self.skfd.recv(1024).decode())

        if status_code == "200":
            self.send_shopping_cards()
            status_code, msg = self.skfd.recv(1024).decode()
            if status_code == "200":
                # TODO 范竹雲
                pass
            else:
                self.aph.paying_error(msg)
        else:
            self.aph.paying_error(msg)

    def get_product_list(self):
        """
        获取商品信息列表
        :return:
        """
        pass

    def get_my_shopping_carts(self):
        """
        获取我的购物车商品列表
        :return:
        """
        pass

    def start(self):
        """
        客户端启动函数
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
