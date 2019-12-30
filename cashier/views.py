# coding=utf-8
import socket

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.lib.logger import Log
from shopping_store.lib.project import get_request, change_point_func
from shopping_store.settings import CASHIER_SOCKET_SERVER_ADDR
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
        id, pn, name = self.db.get_user_msg_from_id(request_data)
        print("{}来结算了".format(name))
        self.success_send(connfd, "request successful.")

    def do_shopping_cards(self, request_data):
        pass

    def do_paying(self, request_data):
        pass

    def main_task(self, connfd, addr):
        data = connfd.recv(1024)
        request_mode, request_data = get_request(data.decode())

        if request_mode == "REQUEST":
            self.do_request(connfd, request_data)
        elif request_mode == "SHOPPING_CARDS":
            self.do_shopping_cards(request_data)
        elif request_mode == "PAYING":
            self.do_paying(request_data)
        else:
            logger.info("结算端，接收请求异常, addr:{}, request_mode:{}".format(addr, request_mode))

    def waiting_for_connect(self):
        while True:
            connfd, addr = self.skfd.accept()
            t = Thread(target=self.main_task, args=(connfd, addr))
            t.start()

    def login(self):
        """
        结算员登录
        :return:
        """
        pass

    def start(self):
        """
        结算端启动函数
        :return:
        """
        self.login()
