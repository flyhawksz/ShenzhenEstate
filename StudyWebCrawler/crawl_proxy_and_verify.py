#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/3/2 12:27
# @Author  : flyhawk
# @Site    : 
# @File    : crawl_proxy_and_verify.py
# @Software: PyCharm

import requests
from lxml import etree
import logging  # log相关功能，不能总是用print那么low
import threading  # 导入线程包
import queue  # 多线程传递验证通过的IP, 保证线程安全
import os
import time
from Crawl import Crawler


class ProxyCrawlerAndVerfiy(Crawler):
    is_clear_all_data = False
    connargs = {"host": "localhost", "port": "3306", "user": "root", "passwd": "123456", "db": "proxyip"}
    
    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象
        Crawler.__init__(self)
        self.database_name = 'proxyip'
        self.file_proxy_all_list = "proxy_candidate.txt"  # 保存 免费代理服务器网站 爬下来的所有代理IP
        self.file_proxy_valid_list = "proxy_valid.txt"  # 保存 通过验证可用的 代理IP
        self.file_proxy_all_list_table = "proxy_candidate"  # 保存 免费代理服务器网站 爬下来的所有代理IP
        self.file_proxy_valid_list_table = "proxy_valid"  # 保存 通过验证可用的 代理IP
        self.proxy_resource_Url = "http://www.xicidaili.com/nn/"  # 用于爬取代理信息的网站
        self.verify_url = "http://www.baidu.com/"  # 用于验证Proxy IP的网站
        self.proxy_resource_page = 5  # 获取代理页面数量
        self.verify_threading_number = 10  # 验证IP线程数量
        
        # 初始化数据库连接
        try:
            if self.mysql is None:
                self.create_mysql(self.connargs)
        except Exception as e:
            print(e)

        if not self.mysql.hasThisTable(self.file_proxy_all_list_table):
            self.mysql.insert(
                "create table if not exists " + self.file_proxy_all_list_table + "(id int not null AUTO_INCREMENT PRIMARY KEY ,ip char(30))")  # 自增长

        if not self.mysql.hasThisTable(self.file_proxy_valid_list_table):
            self.mysql.insert(
                "create table if not exists " + self.file_proxy_valid_list_table + "(id int not null AUTO_INCREMENT PRIMARY KEY ,ip char(30))")  # 自增长

        if self.is_clear_all_data:
            # 初始化，删除原有文件
            if os.path.exists(self.file_proxy_all_list):
                if os.path.exists(self.file_proxy_all_list + ".bak"):
                    os.remove(self.file_proxy_all_list + ".bak")
                os.rename(self.file_proxy_all_list, self.file_proxy_all_list + ".bak")
            # os.remove(self.file_proxy_all_list)
            if os.path.exists(self.file_proxy_valid_list):
                if os.path.exists(self.file_proxy_valid_list + ".bak"):
                    os.remove(self.file_proxy_valid_list + ".bak")
                os.rename(self.file_proxy_valid_list, self.file_proxy_valid_list + ".bak")
            # os.remove(self.file_proxy_valid_list)
            
            # 删除表
            try:
                if self.mysql.hasThisTable(self.file_proxy_all_list_table):
                    # self.mysql.delete("drop table if exists " + self.file_proxy_all_list_table)
                    # self.mysql.insert("create table if not exists " + self.file_proxy_all_list_table + "(id int not null AUTO_INCREMENT PRIMARY KEY ,ip char(30))")  # 自增长
                    # 清空表
                    self.mysql.delete("truncate table " + self.file_proxy_all_list_table)
                else:
                    self.mysql.insert("create table if not exists " + self.file_proxy_all_list_table + "(id int not null AUTO_INCREMENT PRIMARY KEY ,ip char(30))")  # 自增长

                if self.mysql.hasThisTable(self.file_proxy_valid_list_table):
                    # 清空表
                    self.mysql.delete("truncate table " + self.file_proxy_valid_list_table)
                else:
                    self.mysql.insert(
                        "create table if not exists " + self.file_proxy_valid_list_table + "(id int not null AUTO_INCREMENT PRIMARY KEY ,ip char(30))")  # 自增长

            except Exception as e:
                print("TRUNCATE fail")
                # self.mysql.dispose()
    
    def get_proxies(self):
        # 获取IP
        for i in range(1, self.proxy_resource_page + 1):
            url = self.proxy_resource_Url + str(i)
            logging.info('Crawl %s' % url)
            html = self.get_html(url)
            logging.info('parse proxy')
            self.get_proxy_in_html(html)
            
    # 获取ip
    # 解析网页，并得到网页中的代理IP,保存为文件
    def get_proxy_in_html(self, html):
        # 对获取的页面进行解析
        selector = etree.HTML(html)
        # print(selector.xpath("//title/text()"))
        proxies = []
        # 信息提取
        for each in selector.xpath("//tr[@class='odd'] | //tr[@class='']"):
            # ip.append(each[0])
            # 获取IP地址,/html/body/div[1]/div[2]/table/tbody/tr[92]/td[2]
            ip = each.xpath("./td[2]/text()")[0]
            # 获取端口,/html/body/div[1]/div[2]/table/tbody/tr[92]/td[3]
            port = each.xpath("./td[3]/text()")[0]
            # 拼接IP地址，端口号
            proxy = ip + ":" + port
            # 拼接的IP地址放入到定义的空列表中
            # proxies_queue.put(proxy)
            proxies.append(proxy)
        # 计算每个页面一共有几个IP地址
        print(len(proxies))
        logging.info('Get IP %d' % len(proxies))
        # 将list中所有信息写入proxy_all.txt
        self.write_list_txtfile(proxies, self.file_proxy_all_list)
        
        # 将list中所有信息写入数据库test,表 candidate_ip
        self.write_list_into_mysql(proxies, self.file_proxy_all_list_table)
        
    # 验证IP
    def verify_proxy(self):  # 从proxy_all.txt获取所有Proxy IP进行验证，将有效的IP存入proxy_valid.txt
        def verify_ip(ip_port_list, valid_ip_queue, _id):
            index = 0
            requests.adapters.DEFAULT_RETRIES = 5
            test_proxy = requests.session()
            test_proxy.keep_alive = False
            
            for i in ip_port_list:
                if type(i) is bytes:
                    ip_port = i.decode()
                else:
                    ip_port = i
                    
                proxy_url = {'http': 'http://' + ip_port.strip('\n')}
                # request.get信息中需要填写proxies字段，字段的format={'http':'http://ip:port'}
                # 因为读回的信息每一行都有"\n"，所以需要用.strip过滤掉"\n"
                
                try:
                    # 通过request.get获取验证页面，timeout用于防止 傻等，毕竟要验证一堆IP
                    test_page = test_proxy.get(self.verify_url, headers=self.http_headers, proxies=proxy_url,
                                               timeout=(2, 3))
                except:  # 如果获取页面异常，进入这儿，再处理下一个IP
                    print("Threading %d : Invaild Proxy : %s" % (_id, ip_port.strip('\n')))
                    # logging.info("Threading %d : Invaild Proxy : %s" % (_id, ip_port.strip('\n')))
                    continue
                # 获取正常的页面返回码一般都是200，不是的话继续处理下一个IP
                if test_page.status_code != 200:
                    print("Threading %d : Invaild Proxy : %s" % (_id, ip_port.strip('\n')))
                    # logging.info("Threading %d : Invaild Proxy : %s" % (_id, ip_port.strip('\n')))
                    continue
                
                # 能用的IP存入proxy_valid.txt
                print("********Threading %d : Vaild Proxy : %s" % (_id, ip_port.strip('\n')))
                logging.info("********Threading %d : Vaild Proxy : %s" % (_id, ip_port.strip('\n')))
                valid_ip_queue.put(ip_port)
        
        # 处理抓取的IP，按线程数量进行切片，分别获得每片的起始位置，然后用不同的线程读取不同的数据块
        def slice_ip_list():
            valid_ip_queue = queue.Queue()
            verify_ip_thread = []
            ip_port_list = []
            # # 将proxy_all.txt中所有信息读到ip_port_list中，
            # with open(self.file_proxy_all_list, 'r') as fd_proxy_all:
            #     ip_port_list = fd_proxy_all.readlines()  # 读取全部内容
            
            # 从数据库取出带验证IP
            sql = 'SELECT * FROM %s;' % (self.database_name + '.' + self.file_proxy_all_list_table)
            result = self.mysql.getMany(sql, 200)  # "all", 100

            # 将MySQL的字典，转换为列表
            for it in result:
                # print(it)
                # for (key, value) in it.items():
                #     print(key + ":" + str(value))
                # print('\n')
                ip_port_list.append(it['ip'])
            
            ip_count = len(ip_port_list)
            if ip_count % self.verify_threading_number == 0:
                block = self.verify_threading_number
                ip_per_block = ip_count // self.verify_threading_number
            else:
                block = self.verify_threading_number + 1
                ip_per_block = ip_count // (self.verify_threading_number + 1)
            
            for i in range(0, block):
                print("block - " + str(i))
                # verify_ip(ip_port_list[i * intBlockIPCount: (i + 1) * intBlockIPCount], valid_ip_queue)
                thread = threading.Thread(target=verify_ip, args=(
                    ip_port_list[i * ip_per_block: (i + 1) * ip_per_block-1], valid_ip_queue, i))
                verify_ip_thread.append(thread)
            
            start_time = time.time()
            print('Start : {}'.format(start_time))
            for i in range(len(verify_ip_thread)):
                verify_ip_thread[i].start()
            
            # 等待所有线程结束
            for i in range(len(verify_ip_thread)):
                verify_ip_thread[i].join()
            
            end_time = time.time()
            print('End : {}'.format(end_time))
            print("last time: {} s".format(time.time() - start_time))
            
            # queue 转换 list
            valid_ip_list = []
            while not valid_ip_queue.empty():
                t_queue = valid_ip_queue.get()
                valid_ip_list.append(t_queue)
            # 写入TXT文件
            if len(valid_ip_list) > 0:
                print("Writting IP")
                self.write_list_txtfile(valid_ip_list, self.file_proxy_valid_list)
                
                # 写入数据库
                self.write_list_into_mysql(valid_ip_list, self.file_proxy_valid_list_table)
            else:
                print("there is no valid IP")
                logging.warning("there is no valid IP")
        # while not valid_ip_queue.empty():
        # 	print(valid_ip_queue.get())
        
        slice_ip_list()
    
    def main(self):
        self.get_proxies()
        self.verify_proxy()


if __name__ == '__main__':
    proxyCrawlerAndVerfiy = ProxyCrawlerAndVerfiy()
    proxyCrawlerAndVerfiy.main()
