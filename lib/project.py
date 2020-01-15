# coding=utf-8
import re

from shopping_store.lib.logger import Log

logger = Log("shopping_store_error")


def get_number_input(msg, is_float=False):
    """
    封装input函数，判断类型是否正确
    :param msg:
    :param is_float:
    :return:
    """
    err_msg = "您的输入有误！请重新输入！"
    while True:
        user_input = input(msg)
        if not user_input:
            continue

        if user_input == "q":
            return user_input

        if is_float:
            try:
                return float(user_input)
            except Exception as err:
                logger.info("用户输入错误，msg:{}".format(err))
                print(err_msg)
                continue
        else:
            try:
                return int(user_input)
            except Exception as err:
                logger.info("用户输入错误，msg:{}".format(err))
                print(err_msg)
                continue


def user_input(msg):
    while True:
        user_input = input(msg)
        if not user_input:
            continue
        else:
            return user_input


def match_pn(pn):
    """
    正则匹配手机格式
    :param pn: 手机号
    :return: True or False
    """
    return True if re.match(r"^1[3578]\d{9}$", pn) else False


def format_datetime(input_date):
    """
    匹配用户输入的日期格式
    :param input_date: 2019-10-03
    :return: True or False
    """
    formater = r"^[1-9]\d{0,3}-(1[0-2]|0?[1-9])-(3[01]|[12]\d|0?[1-9])$"
    return re.match(formater, input_date)


def change_point_func(point_func):
    """
    改变目标类函数为可执行格式
    :param point_func:
    :return:
    """
    return "self." + point_func + "()"


def get_request(request):
    """
    将接收到的消息内容拆分，返回元组，方便拆包
    :param request:接收到的消息内容
    :return:拆分后的元组消息内容
    """
    return tuple(request.split(" ", 1))
