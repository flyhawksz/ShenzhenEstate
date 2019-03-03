import sys
import threading
import pymysql
# import MySQLdb
import DBUtils.PooledDB
import time
import random
import string


# CONN_INFO={'host':'localhost','user':'root','password':'111111','port':3306,'db':'','charset':'utf8'}


class MySqlHelper:
    '''
	实现数据库具体操作的类
	'''

    def __init__(self, CONN_INFO):
        try:
            import MySQLdb
        except ImportError as e:
            raise e
        try:
            # CONN_INFO={'host':'localhost','user':'root','password':'111111','port':3306,'db':'','charset':'utf8'}
            host = CONN_INFO['host']
            user = CONN_INFO['user']
            passwd = CONN_INFO['password']
            port = CONN_INFO['port']
            db = CONN_INFO['db']
            charset = CONN_INFO['charset']
            self.conn = MySQLdb.connect(host=host, user=user, db=db, passwd=passwd, port=port, charset=charset)  # 连接数据库
            self.cursor = self.conn.cursor()  # 游标对象
        except Exception as e:
            raise e

    '''
		函数名：Finish
		输入:无
		功能：提交数据库操作并关闭数据库连接
		输出：无
	'''

    def Finish(self):
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
        except Exception as e:
            raise e


connargs = {"host": "localhost", "port": "3306", "user": "root", "passwd": "123456", "db": "test"}


def init_mysql_data(conn):
    try:
        cur = conn.cursor()
        cur.execute("drop table if exists student")
        sql = "create table if not exists users(id int not null AUTO_INCREMENT PRIMARY KEY ,name char(20),age char(3))"  # 自增长
        cur.execute(sql)

        print(time.ctime())
        for i in range(1, 1000):
            random_name = ''.join(random.sample(string.ascii_letters + string.digits, 8))  # 8位随机字符
            random_age = ''.join(str(random.randint(10, 120)))  # 10-120随机字符
            value = (random_name, random_age)
            insert_sql = "insert into  users(name,age) values(%s,%s)"
            cur.execute(insert_sql, value)
            i += 1
            conn.commit()
        print(time.ctime())
    except Exception as e:
        conn.rollback()
        print("Insert fail")
    cur.close()
    conn.close()

#
# ---------------------
# 作者：meiguopai1
# 来源：CSDN
# 原文：https: // blog.csdn.net / meiguopai1 / article / details / 73799913
# 版权声明：本文为博主原创文章，转载请附上博文链接！



def test(conn):
    try:
        cursor = conn.cursor()
        count = cursor.execute("select * from student")
        rows = cursor.fetchall()
        for r in rows: pass
    finally:
        conn.close()


def testloop():
    print("testloop")
    for i in range(1000):
        conn = pymysql.connect(**connargs)
        test(conn)


def testpool():
    print("testpool")
    pooled = DBUtils.PooledDB.PooledDB(pymysql, **connargs)
    for i in range(1000):
        conn = pooled.connection()
        test(conn)


def main():
    
    # 显示调用本程序附加的参数
    # print(sys.argv)
    
    # 填充student 表
    # conn = pymysql.connect(**connargs)
    # init_mysql_data(conn)
    
    # 对比测试
    print("start:" + time.ctime() + '-' + str(time.clock()))
    start = time.time()

    # # print(sys.argv)
    # if len(sys.argv) == 1:
    # t = testloop
    # else:
    t = testpool
    #
    for i in range(5):
        threading.Thread(target=t).start()

    for i in range(5):
        threading.Thread(i).join()
    end = time.time()
    print("end:" + time.ctime() + '-' + str(time.clock()))
    print("cost:" + str(end - start))
    
if __name__ == "__main__":
    main()
