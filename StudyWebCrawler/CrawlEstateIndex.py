#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/16 21:46
# @Author  : flyhawk
# @Site    :
# @File    : CralProxyAndVerfiy.py
# @Software: PyCharm

from lxml import etree
import logging  # log相关功能，不能总是用print那么low
import threading  # 导入线程包
import time
from Crawl import Crawler
import entity_class
import random
from concurrent.futures import ThreadPoolExecutor


class CrawlerLianjiaEsatesIndex(Crawler):

    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象

        Crawler.__init__(self)
        
        # 初始化数据库连接
        try:
            if self.mysql is None:
                self.create_mysql(self.connargs)
        except Exception as e:
            print(e)
            
        self.thread_lock = threading.Lock()
        self.database_name = 'szestate'
        self.proxy_all_list_table = self.database_name + ".proxy_candidate"  # 保存 免费代理服务器网站 爬下来的所有代理IP
        self.proxy_valid_list_table = self.database_name + ".proxy_valid"  # 保存 通过验证可用的 代理IP
        
        self.dealed_esate_candidate_table = self.database_name + ".dealed_esate_candidate"  # 保存 通过验证可用的 代理IP
        
        self.file_all_list = "estates_all.txt"  # 保存 免费代理服务器网站 爬下来的所有代理IP
        self.proxy_resource_Url = ""  # 用于爬取代理信息的网站
        self.resource_page_number = 1  # 获取页面数量
        self.threading_pool_size = 10  # 抓取页面线程数量+

        self.list_url = "https://sz.lianjia.com/chengjiao/"
        self.detail_rul = ""

        self.index_url_list = []
        self.create_url_list()
        # print(self.index_url_list)
        
        self.proxy_list = []
        self.get_proxy_list()
        self.proxy_pool_list = self.proxy_list

        self.mysql.insert(
            "create table if not exists " + self.dealed_esate_candidate_table
            + "(id int not null AUTO_INCREMENT PRIMARY KEY ,estate_id char(30), esate_name char(30), url char(150))")  # 自增长

    # 获取房产ID
    # 解析网页，并得到网页中的ID,保存为文件
    def get_estates_list(self, url):
        estate_list = []
        proxy_ip = ""
        fields = ('id', 'name', 'url')
        # print("Threading %d crawl %s" % threading.currentThread().ident, url)
        
        # 从 proxy 池中随机取一代理
        err = 0
        # 当池中 proxy 为空，等2秒
        while len(self.proxy_pool_list) < 1:
            err += 1
            time.sleep(2)
            # 超过10次，抛出错误
            if err > 10:
                raise Exception("proxy error!!!")
            
        self.thread_lock.acquire()
        proxy_ip = random.choice(self.proxy_pool_list)
        # 避免重复
        self.proxy_pool_list.remove(proxy_ip)
        self.thread_lock.release()
        
        try:
            # html = self.get_local_html('test.html')
            html = self.get_html(url, proxy_ip)
            # print("Threading %d crawl %s" % thread_id, url)
        except:
            print("Threading %d crawl %s FAIL!!!" % threading.currentThread().ident, url)
        else:
            selector = etree.HTML(html)
            # 信息提取 ， /html/body/div[5]/div[1]/ul/li
            for each in selector.xpath("//html/body/div[5]/div[1]/ul/li"):
                # 获取房产详细页面,/html/body/div[5]/div[1]/ul/li[1]/div/div[1]/a
                estate_detail_url = each.xpath("./div/div[1]/a/@href")[0]
                # 获取ID,/html/body/div[1]/div[2]/table/tbody/tr[92]/td[3]
                estate_id = (estate_detail_url.strip().split('/')[-1]).split('.')[0]
                # 获取名称
                estate_name = each.xpath("./div/div[1]/a/text()")[0]
                
                estate = 'id:"{}", name:"{}" , url:"{}"'.format(estate_id, estate_name, estate_detail_url)
                # self.write_one_dict_into_mysql(self.dealed_esate_candidate_table, estate)
                estate_list.append((estate_id, estate_name, estate_detail_url))
        
        self.write_list_into_mysql(self.dealed_esate_candidate_table, fields, estate_list)
        
        # 该线程使用完proxy, 归还池
        self.thread_lock.acquire()
        self.proxy_pool_list.append(proxy_ip)
        self.thread_lock.release()
        # 冷却2秒
        time.sleep(2)

    # 根据链家页面，生成 成交列表 的链接
    def create_url_list(self):
        self.index_url_list.append("https://sz.lianjia.com/chengjiao/")
        for i in range(2, self.resource_page_number + 2):
            self.index_url_list.append("https://sz.lianjia.com/chengjiao/pg" + str(i))
    
    # 取得 proxy 列表
    def get_proxy_list(self):
        sql = 'SELECT * FROM %s;' % self.proxy_valid_list_table
        result = self.mysql.getMany(sql, 200)  # "all", 100
        if len(result) < 1:
            raise Exception("there is no proxy to use!!!")
    
        # 将MySQL的字典，转换为列表
        for it in result:
            self.proxy_list.append(it['ip'])

    def main(self):
        executor = ThreadPoolExecutor(max_workers=self.threading_pool_size)
        executor.map(self.get_estates_list, self.index_url_list)
        # executor.
        # executor.shutdown()
        # executor.shutdown(wait=True)


if __name__ == '__main__':
    # 构建连接列表
    clawler = CrawlerLianjiaEsatesIndex()
    clawler.main()
