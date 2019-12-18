# coding=utf-8
import re


def match_pn(pn):
    """
    正则匹配手机格式
    :param pn: 手机号
    :return: True or False
    """
    return re.match(r"^1[3578]\d{9}$", pn)


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
