# coding=utf-8
import socket

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.lib.project import get_number_input, change_point_func
from shopping_store.settings import CASHIER_SOCKET_SERVER_ADDR


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

    def error_input(self):
        print("""
        您的输入有误！请重新输入！
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

    def remove_product(self, product):
        if product not in self.product_list:
            return False, "您的购物车中没有该商品！"

        self.product_list.remove(product)
        return True, "移除成功！"


class CustomerHandler:
    def __init__(self):
        self.db = MysqlDB()
        self.aph = CustomerPrintHandler()
        self.shopping_cart = ShoppingCart(user_id=1)  # TODO 测试代码

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
        # self.create_tcp_socket()

    def create_tcp_socket(self):
        self.skfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.skfd.connect(CASHIER_SOCKET_SERVER_ADDR)

    def register(self):
        pass

    def login(self):
        # 登录成功后，返回登录成功的user_id, 利用user_id实例化用户购物车，ShoppingCart
        pass

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

    def remove_product(self):
        """
        从购物车中移除商品
        :return:
        """
        pass

    def paying(self):
        """
        发起结算
        :return:
        """
        pass

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

    def reduce_product_count(self):
        """
        扣除库存
        :return:
        """
        pass

    def product_not_enough(self):
        """
        库存不足通知提醒
        :return:
        """
        pass

    def commit_record(self):
        """
        保存交易记录
        :return:
        """
        pass

    def export_ticket(self):
        """
        打印小票
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
            user_input = get_number_input(">>")
            point_func = self.start_menu_map.get(user_input, False)
            if not point_func:
                self.aph.error_input()
            else:
                eval(change_point_func(point_func))
