# coding=utf-8
import datetime
import getpass
import socket
from _decimal import Decimal

from shopping_store.db_handler.mysql_db import MysqlDB
from shopping_store.lib.logger import Log
from shopping_store.lib.project import (
    get_request,
    user_input,
)
from shopping_store.settings import (
    CASHIER_SOCKET_SERVER_ADDR,
    ADMIN_SOCKET_SERVER_ADDR,
    USER_TICKET_PATH,
)
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
        self.user_id = None  # 正在结算的用户ID
        self.user_name = None  # 正在结算的用户名
        self.cashier_id = None  # 结算员ID

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
            self.user_id = id
            self.user_name = name
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

    def sum_shopping_cards_profit(self, shopping_cards):
        total_profit = Decimal("0.00")
        for item in shopping_cards:
            profit = self.db.get_profit_by_product_id(item["product_id"])
            total_profit += profit * item["count"]
        return total_profit

    def commit_record(self, commit_record):
        """
        保存交易记录
        :return:
        """
        total_amount = self.sum_shopping_cards_amount(commit_record["success_list"])
        total_profit = self.sum_shopping_cards_profit(commit_record["success_list"])
        order_id = self.db.create_order_record(self.user_id, self.cashier_id, total_amount, total_profit)
        for item in commit_record["success_list"]:
            self.db.create_order_detail(order_id, item["product_id"], item["count"], item["price"])
        return order_id

    def get_export_ticket_paths(self):
        """
        打印小票文件路径及文件
        :return:
        """
        t = datetime.datetime.now()
        str_t1 = t.strftime("%Y-%m-%d_%H:%M:%S")
        return USER_TICKET_PATH + str_t1 + ".txt"

    def export_ticket(self, order_id, pay_result, total_amount, user_pay_money, money_return):
        """
        打印小票
        :return:
        """
        id, pn, name = self.db.get_user_msg_from_id(self.cashier_id)

        file_path = self.get_export_ticket_paths()
        f = open(file_path, 'w+')
        f.write('                消费单' + '\n')
        f.write("-------------***********-------------" + "\n")
        f.write("结算单号:                  %s" % order_id + "\n")
        for into in pay_result["success_list"]:
            f.write('商品名：{}，单价：{}元，个数：{}个\n'.format(into["name"], into["price"], into['count']))
        f.write(
            "应付:                    %s" % total_amount + '\n'
                                                         "实付:                    %s" % user_pay_money + '\n'
                                                                                                        "找零:                    %s" % money_return + "\n")
        f.write("结算员：{}（ID：{}）\n".format(name, id))
        f.write("结算时间：{}".format(datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')))
        f.flush()
        f.close()
        return "小票已保存至:{}".format(file_path)

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
        money_return = Decimal(user_pay_money) - Decimal(total_amount)  # 计算找零金额
        if money_return >= 0:
            # 结算、减库存
            pay_result = self.reduce_product_count(eval(shopping_cards_msg))
            if len(pay_result.get("success_list", False)):
                # 创建订单记录
                order_id = self.commit_record(pay_result)
                # 打印小票
                ticket_msg = self.export_ticket(order_id, pay_result, total_amount, user_pay_money, money_return)
                self.success_send(connfd, ticket_msg)
                # print("{}结算完成".format(self.user_name))
            else:
                # 结算内容全部失败
                self.fail_send(connfd, "订单库存被抢付，支付失败。")
        else:
            self.fail_send(connfd, "支付金额不足！")

    def main_task(self, connfd, addr):
        while True:
            data = connfd.recv(1024)
            try:
                request_mode, request_data = get_request(data.decode())
            except Exception as info:
                logger.info(info)
                continue

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
        pn = user_input("请输入手机号：")
        password = getpass.getpass("请输入密码：")
        status, msg, user_id = self.db.user_login(pn, password, 2)
        print(msg)

        if status:
            # 登录成功
            self.cashier_id = user_id
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
