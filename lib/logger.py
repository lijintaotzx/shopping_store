# coding=utf-8
import datetime

from shopping_store.settings import LOG_PATH


class Log:
    """
    项目Log
    """

    def __init__(self, log_type):
        self.log_type = log_type
        self.log_path = LOG_PATH.get(self.log_type, False)

    def get_time_now(self):
        return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    def format_msg(self, msg_type, msg):
        return "{}-异常级别:{}-->{}\n".format(self.get_time_now(), msg_type, msg)

    def info(self, info_msg):
        f = open(self.log_path, "a+")
        f.write(self.format_msg("info", info_msg))
        f.close()

    def error(self, info_msg):
        f = open(self.log_path, "a+")
        f.write(self.format_msg("error", info_msg))
        f.close()
