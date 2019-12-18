# coding=utf-8
from threading import Thread

from shopping_store.admin.views import AdminHandler


def main_start(handler):
    """
    线程一启动函数：后台主函数
    :param handler:
    :return:
    """
    handler.start()


def socket_start(handler):
    """
    线程二启动函数：UDP接收其他端消息
    :param handler:
    :return:
    """
    handler.wating_for_socket_msg()


if __name__ == '__main__':
    admin_handler = AdminHandler()

    func_list = [main_start, socket_start]
    join_list = []

    for func in func_list:
        t = Thread(target=func, args=(admin_handler,))
        t.start()
        join_list.append(t)

    [j.join() for j in join_list]
