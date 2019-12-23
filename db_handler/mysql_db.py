# coding=utf-8
import hashlib

import pymysql

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

    def check_product_name(self, product_name):
        """
        查询新添加的product_name是否重复
        :param product_name: 新添加的商品名称
        :return: True or False
        """
        sql = "select count(*) from `product` where name = '{}';".format(product_name)
        self.cursor.execute(sql)
        num = self.cursor.fetchall()
        if num[0][0] == 0:
            return True
        else:
            return False

    def add_db_product(self, add_product):
        """
        # TODO
        :param add_product:
        :return:
        """
        try:
            sql = "INSERT INTO `product` " \
                  "(`name`, `description`, `source_price`, `price`, `count`,`product_id`) " \
                  "VALUES {};".format(add_product)
            self.cursor.execute(sql)
            self.db.commit()
            return "新商品添加成功！"
        except:
            self.db.rollback()
            return "新商品添加失败！"

    def get_product_list_db(self, is_admin=False):
        if is_admin:
            sql = "SELECT name,description,source_price,price,product_id,count FROM product"
        else:
            sql = "SELECT name,description,price,product_id,count FROM product"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def change_product_count_db(self, product_id, change_count):
        sql1 = "UPDATE product set count = %s WHERE product_id = %s" % (change_count, product_id)
        self.cursor.execute(sql1)
        self.db.commit()
        sql2 = "SELECT count FROM product WHERE product_id =%s" % product_id
        self.cursor.execute(sql2)
        product = self.cursor.fetchone()

        print("修改成功！当前库存:{}".format(product[0]))

    def judge_product_id(self, product_id):
        """
        判断product_id是否存在
        :param product_id:
        :return: Ｔrue or Ｆalse
        """
        sql = "SELECT name,count FROM product WHERE product_id = %s" % product_id
        self.cursor.execute(sql)
        fetch_result = self.cursor.fetchone()
        if fetch_result:
            name, count = fetch_result
            print("您修改的商品名称:{},当前库存:{}".format(name, count))
            return True
        else:
            print("商品ID不存在！")
            return False

    def get_order_list_db(self, order_begin, order_end):
        """
        获取订单列表(刘梓威)
        sql语句
        :param order_begin: 开始时间
        :param order_end: 结束时间
        :return: 订单记录的信息(元组的形式)
        """
        sql = "SELECT user_id, profit, order_id, cashier_id, amount, create_time FROM order_record WHERE create_time BETWEEN '{}' AND '{}';".format(
            order_begin,
            order_end
        )
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_user_msg_from_id(self, user_id):
        """
        获取用户基本信息
        :param user_id:用户ID
        :return: 用户信息元组
        """
        sql = "SELECT id, pn, name FROM user WHERE id={}".format(user_id)
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def get_order_details_db(self, order_id):
        """
        获取订单详情
        :param order_id: 订单ID
        :return:
        """
        sql = "SELECT product.product_id, product.name, product.description, order_record_detail.count, order_record_detail.price " \
              "FROM order_record_detail, product " \
              "WHERE order_record_detail.product_id=product.id AND order_record_detail.order_id={};".format(order_id)
        self.cursor.execute(sql)
        return self.cursor.fetchall()
