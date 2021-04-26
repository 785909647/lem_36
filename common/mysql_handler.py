import pymysql
from common.yaml_handler import yaml_conf_sql
from pymysql.cursors import DictCursor

class ReadMysqlData(object):
    '''连接数据库类'''
    def __init__(self,count=None):
        '''count 为True 连接生产环境数据库  否则连接测试环境数据库'''
        if count:
            # 连接到数据库
            self.con = pymysql.connect(
                host=yaml_conf_sql["yield_sql"]["host"],
                port=yaml_conf_sql["yield_sql"]["port"],
                user=yaml_conf_sql["yield_sql"]["user"],
                password=yaml_conf_sql["yield_sql"]["password"],
                database=yaml_conf_sql["yield_sql"]["database"],
                charset='utf8',
                cursorclass = DictCursor)
        else:
            self.con = pymysql.connect(
                host=yaml_conf_sql["test_sql"]["host"],
                port=yaml_conf_sql["test_sql"]["port"],
                user=yaml_conf_sql["test_sql"]["user"],
                password=yaml_conf_sql["test_sql"]["password"],
                database=yaml_conf_sql["test_sql"]["database"],
                charset='utf8',
                cursorclass = DictCursor)
        # 创建游标
        self.cur = self.con.cursor()

    def find_one(self, sql):
        """
        返回找到的第一条数据
        :param sql:
        :return:
        """
        self.cur.execute(sql)
        self.con.commit()
        return self.cur.fetchone()

    def find_all(self, sql):
        """
        返回找到的所有数据
        :param sql:
        :return:
        """
        self.cur.execute(sql)
        return self.cur.fetchall()

    def close(self):
        """断开连接"""
        self.cur.close()
        self.con.close()
#
# #

class MD():
    """上下文管理sql链接"""

    def __enter__(self,
            host="8.129.91.152",
            port=3306,
            user="future",
            password="123456",
            charset ="utf8",
            cursorclass=DictCursor):
        self.con = pymysql.connect(host=host,port=port,user=user,password=password,charset=charset,cursorclass=cursorclass)#连接数据库
        self.cur = self.con.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cur.close()
        self.con.close()

    def query(self,sql,one=True):
        self.cur.execute(sql)
        self.con.commit()
        if one:
            return self.cur.fetchone()
        return self.cur.fetchall()












