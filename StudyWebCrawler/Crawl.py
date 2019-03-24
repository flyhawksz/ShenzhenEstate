#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/16 21:46
# @Author  : flyhawk
# @Site    :
# @File    : CralProxyAndVerfiy.py
# @Software: PyCharm


"""
爬虫父类，放置通用的方法
"""


import requests
from lxml import etree
import logging  # log相关功能，不能总是用print那么low
import socket  # 用于设定网络连接的相关属性
import codecs
from Mysql_connect_pool_tools import MyPymysqlPool


class Crawler(object):
    connargs = {"host": "localhost", "port": "3306", "user": "root", "passwd": "123456", "db": "test"}
    
    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象
        # 要为http报文分配header字段，否则很多页面无法获取
        self.http_headers = {
            # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            # 'Accept-Encoding': 'gzip, deflate'
            
            'content-type': 'charset=utf8',  # 解决response乱码
            "Accept": "text/html,application/xhtml+xml,"
                      "application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "Keep-Alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/55.0.2883.87 Safari/537.36",
            'Accept-Encoding': 'gzip, deflate'
        }

        # 配置log信息存储的位置
        logging.basicConfig(filename='./debug.log', filemode="w", level=logging.DEBUG)
        # 3秒内没有打开web页面，就放弃等待，防止死等，不管哪种语言，都要防范网络阻塞造成程序响应迟滞，CPU经常因此被冤枉
        socket.setdefaulttimeout(3)
        self.mysql = None

    def __del__(self):
        if self.mysql:
            self.mysql.dispose
        
    # 解析网页，并得到网页中的ID,保存为文件
    def get_list(self, html, xpath_rull):
        gain_list = []
        # 对获取的页面进行解析
        selector = etree.HTML(html)
        gain_list = selector.xpath(xpath_rull)
        # 计算每个页面一共有几个IP地址
        print('gain %d records' % len(gain_list))
        logging.info('Get list %d' % len(gain_list))
        return gain_list

    # 返回网页代码
    def get_html(self, url, proxy_ip=None):
        if proxy_ip:
            response = requests.get(url, headers=self.http_headers, proxy=proxy_ip)
        else:
            response = requests.get(url, headers=self.http_headers)
        # print(response.text)
        return response.text

    # 返回本地文件
    def get_local_html(self, filepath):
        f = codecs.open(filepath, 'r', 'utf-8')
        html = f.read()
        f.close()
        return html

    # 代理IP的信息存储
    def write_list_txtfile(self, list, filename):
        # print(proxies)
        for t_list in list:
            # with as 语法的使用，可以省去close文件的过程
            with open(filename, 'a+', encoding="UTF-8") as f:
                logging.info("Writing ：%s" % t_list)
                f.write(t_list + '\n')
        logging.info("Finish Writing!!!")

    def write_one_dict_into_mysql(self, table_name, dict_data):
        fields = ','.join(dict_data.keys())
        values = ','.join(dict_data.values())
        try:
            logging.info("insert into " + table_name + " (ip) values (%s);")
            self.mysql.insert(
                "insert into {table} ({key}) values ({val});".format(table=table_name, key=fields, val=values))
            # self.mysql.end()
    
        except Exception as e:
            print("Insert fail")
            logging.warning("Insert fail", e)

    def write_one_into_mysql(self, table_name, fields_tuple, value_tuple):
        fields = ','.join(fields_tuple)
        values = ','.join(value_tuple)
        try:
            logging.info("insert into " + table_name + " (ip) values (%s);")
            self.mysql.insert("insert into {table} ({key}) values ({val});".format(table=table_name, key=fields, val=values))
            # self.mysql.end()
    
        except Exception as e:
            print("Insert fail")
            logging.warning("Insert fail", e)
    
    # 如果多字段，value_list 形如 （（f1,f2,f3）, (f1,f2,f3)）
    def write_list_into_mysql(self, table_name, fields, value_list):
        try:
            logging.info("insert into " + table_name + " (%s) values (%s);")
            self.mysql.insertMany("insert into " + table_name + "  (" + fields + ") values (%s);", value_list)
            self.mysql.end()
                
        except Exception as e:
            print("Insert fail")
            logging.warning("Insert fail", e)
            
    # 生成MySQL数据库连接池
    def create_mysql(self, connargs):
        logging.info("create_mysql")
        self.mysql = MyPymysqlPool(connargs)

