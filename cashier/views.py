# coding=utf-8
import socket
from _decimal import Decimal

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.lib.logger import Log
from shopping_store.lib.project import get_request, change_point_func
from shopping_store.settings import CASHIER_SOCKET_SERVER_ADDR, ADMIN_SOCKET_SERVER_ADDR
from threading import Thread

logger = Log("shopping_store_error")


class CashierPrintHandler:
    def main_menu(self):
        """
        开始打印信息
        :return:
        """
        print("""
        ************************
        您要做什么？
        1、结算员注册
        2、结算员登录
        ************************
        """)


class CashierHandler:
    def __init__(self):
        self.db = MysqlDB()
        self.cph = CashierPrintHandler()

        self.create_tcp_server()

    def create_tcp_server(self):
        """
        创建TCP服务
        :return:
        """
        self.skfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skfd.bind(CASHIER_SOCKET_SERVER_ADDR)
        self.skfd.listen(3)

    def success_send(self, connfd, msg):
        connfd.send("200 {}".format(msg).encode())

    def fail_send(self, connfd, msg):
        connfd.send("400 {}".format(msg).encode())

    def do_request(self, connfd, request_data):
        request_data = eval(request_data)

        if len(request_data["shopping_cards"]):
            id, pn, name = self.db.get_user_msg_from_id(request_data["user_id"])
            print("{}来结算了".format(name))
            self.success_send(connfd, "request successful.")
        else:
            self.fail_send(connfd, "您的购物车为空！")

    def sum_shopping_cards_amount(self, shopping_cards):
        """
        计算购物车中商品总价
        :param shopping_cards:
        :return:
        """
        total_amount = Decimal("0.00")
        for item in shopping_cards:
            total_amount += item["price"] * item["count"]
        return total_amount

    def do_shopping_cards(self, connfd, request_data):
        """
        计算购物车中商品总价，发送回用户端
        :param connfd:socket连接
        :param request_data:用户购物车信息
        :return:
        """
        total_amount = self.sum_shopping_cards_amount(eval(request_data)["shopping_cards"])
        self.success_send(connfd, total_amount)

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

    def send_to_udp_server(self, data):
        """
        给后台发送信息
        :return:
        """
        skfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        skfd.sendto(data.encode(), ADMIN_SOCKET_SERVER_ADDR)
        skfd.close()

    def reduce_product_count(self, product_list):
        """
        扣除库存
        :param product_list: 这里接收用户的一个支付成功的购物车列表，
        遍历里面的商品ID扣除库存（注意判断库存不能为负，否则打印log）
        :return:
        """
        success_list = list()
        fail_list = list()
        for value in product_list['shopping_cards']:
            product_id = value["product_id"]
            product_name = value["name"]
            product_count = value["count"]
            num = self.db.get_product_count(product_id)
            set_count = num - product_count
            if set_count > 0:
                self.db.update_product_count(product_id, set_count)
                success_list.append(value)
            elif set_count == 0:
                self.db.update_product_count(product_id, set_count)
                success_list.append(value)
                data = "ID是%s的%s商品库存不足" % (product_id, product_name)
                self.send_to_udp_server(data)
            else:
                fail_list.append(value)
        return {"success_list": success_list, "fail_list": fail_list}

    def do_paying(self, connfd, request_data):
        """
        处理用户支付
        :param connfd: socket连接
        :param request_data:shopping_cards_msg user_pay_money
        :return:
        """
        shopping_cards_msg, user_pay_money = request_data.split("$$")
        total_amount = self.sum_shopping_cards_amount(eval(shopping_cards_msg)["shopping_cards"])
        if Decimal(total_amount) <= Decimal(user_pay_money):
            self.reduce_product_count(shopping_cards_msg)
        else:
            self.fail_send(connfd, "支付金额不足！")

    def main_task(self, connfd, addr):
        while True:
            data = connfd.recv(1024)
            request_mode, request_data = get_request(data.decode())

            if request_mode == "REQUEST":
                self.do_request(connfd, request_data)
            elif request_mode == "SHOPPING_CARDS":
                self.do_shopping_cards(connfd, request_data)
            elif request_mode == "PAYING":
                self.do_paying(connfd, request_data)
            else:
                logger.info("结算端接收请求异常, addr:{}, error_mode:{}".format(addr, request_mode))

    def waiting_for_connect(self):
        """
        多线程启动，循环等待用户结算
        :return:
        """
        while True:
            print("等待结算中...")
            connfd, addr = self.skfd.accept()
            t = Thread(target=self.main_task, args=(connfd, addr))
            t.start()

    def login(self):
        """
        结算员登录
        :return:
        """
        pn = input("请输入手机号：")
        password = input("请输入密码：")
        status, msg, user_id = self.db.user_login(pn, password, 2)
        print(msg)

        if status:
            # 登录成功
            self.user_id = user_id
            self.waiting_for_connect()
        else:
            # 登录失败
            self.start()

    def start(self):
        """
        结算端启动函数
        :return:
        """
        self.login()


a = CashierHandler()
a.waiting_for_connect()
