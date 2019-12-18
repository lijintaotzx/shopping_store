# coding=utf-8
import hashlib

import pymysql

from shopping_store.lib.decorator import try_db_sql
from shopping_store.settings import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    DATABASE,
    CHARSET,
)


class MysqlDB:
    def __init__(
            self,
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=DATABASE,
            charset=CHARSET
    ):
        self.db = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset=charset
        )

        self.cursor = self.db.cursor()

    def password_encryption(self, password):
        """
        密码加密（MD5）
        :param password:密码
        :return:加密后的密码
        """
        h = hashlib.md5()
        h.update(password.encode())
        return h.hexdigest()

    def user_register_cheker(self, pn, role):
        """
        检查用户是否可以注册
        :param pn: 用户手机号
        :param role: 用户角色
        :return: True or False
        """
        sql = "SELECT * FROM user WHERE pn={} AND role={}".format(pn, role)
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return len(data) == 0

    # @try_db_sql
    def user_register(self, name, password, pn, role=0):
        """
        用户注册
        :param name: 用户名称
        :param password: 用户密码
        :param pn: 用户手机号
        :param role: 用户角色（0：普通用户（顾客），1：商店管理员，2：收银员）默认为普通用户
        :return: 注册结果
        """
        if not self.user_register_cheker(pn, role):
            return False, "对不起，您的手机号已经被注册！请勿重复注册！"

        sql = "INSERT INTO user (name, password, pn, role) VALUES ('{}', '{}', '{}', {});".format(
            name,
            self.password_encryption(password),
            pn,
            role
        )
        self.cursor.execute(sql)
        self.db.commit()
        return True, "恭喜您！注册成功！"

    def user_login(self, pn, password):
        """
        用户登录
        :param pn: 用户手机号
        :param password: 用户密码
        :return: 登录结果
        """
        sql = "SELECT name, pn, password FROM user WHERE pn={}".format(pn)
        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        if not len(data):
            return False, "用户不存在！"

        name, pn, md5_password = data[0]
        login_success_msg = (True, "您好！{}！".format(name))
        login_error_msg = (False, "对不起，密码错误！")
        return login_success_msg if md5_password == self.password_encryption(password) else login_error_msg

    def remove_db_product(self, product_id):
        sql = "UPDATE product SET is_del=True WHERE product_id={}".format(product_id)
        self.cursor.execute(sql)
        self.db.commit()
        select_sql = "SELECT is_del FROM product where product_id={}".format(product_id)
        self.cursor.execute(select_sql)
        data = self.cursor.fetchone()
        if data[0]:
            return "商品ID：{}已下架!".format(product_id)
        else:
            return "商品ID：{}下架失败!".format(product_id)
