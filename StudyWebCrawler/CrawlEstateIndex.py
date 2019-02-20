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
import queue  # 多线程传递验证通过的IP, 保证线程安全
import os
import time
import codecs
from Crawl import Crawler


class CrawlerLianjiaEsatesIndex(Crawler):

    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象

        Crawler.__init__(self)

        self.file_all_list = "estates_all.txt"  # 保存 免费代理服务器网站 爬下来的所有代理IP
        self.proxy_resource_Url = ""  # 用于爬取代理信息的网站
        self.resource_page_number = 2  # 获取页面数量
        self.crawl_threading_number = 10  # 抓取页面线程数量+

        self.list_url = ""
        self.detail_rul = ""


    # 获取房产ID
    # 解析网页，并得到网页中的ID,保存为文件
    def get_estate_id(self, html):
        # 对获取的页面进行解析
        selector = etree.HTML(html)
        # print(selector.xpath("//title/text()"))
        estate_index = []
        # 信息提取 ， /html/body/div[5]/div[1]/ul/li
        for each in selector.xpath("//html/body/div[5]/div[1]/ul/li"):
            # 获取房产详细页面,/html/body/div[5]/div[1]/ul/li[1]/div/div[1]/a
            estate_detail_url = each.xpath("./div/div[1]/a/@href")[0]
            # 获取ID,/html/body/div[1]/div[2]/table/tbody/tr[92]/td[3]
            estate_id = (estate_detail_url.strip().split('/')[-1]).split('.')[0]
            # 获取名称
            estate_name = each.xpath("./div/div[1]/a/text()")[0]
            estate = 'id:{}, name:{} , url:{}'.format(estate_id, estate_name, estate_detail_url)
            estate_index.append(estate)
        # 计算每个页面一共有几个IP地址
        print(len(estate_index))
        logging.info('Get estate list %d' % len(estate_index))
        # 将list中所有信息写入proxy_all.txt
        self.write_list_txtfile(estate_index, self.file_all_list)


    def get_estates_list(self, url, list_queue, thread_id):
        print("Threading %d crawl %s" % thread_id, url)
        try:
            # html = self.get_local_html('test.html')
            html = self.get_html(url)
            print("Threading %d crawl %s" % thread_id, url)
        except:
            print("Threading %d crawl %s FAIL!!!" % thread_id, url)
        else:
            estate_list = self.get_list(html, "//html/body/div[5]/div[1]/ul/li")
            for each in estate_list:
                # 获取房产详细页面,/html/body/div[5]/div[1]/ul/li[1]/div/div[1]/a
                estate_detail_url = each.xpath("./div/div[1]/a/@href")[0]
                # 获取ID,/html/body/div[1]/div[2]/table/tbody/tr[92]/td[3]
                estate_id = (estate_detail_url.strip().split('/')[-1]).split('.')[0]
                # 获取名称
                estate_name = each.xpath("./div/div[1]/a/text()")[0]
                estate = 'id:"{}", name:"{}" , url:"{}"'.format(estate_id, estate_name, estate_detail_url)
                list_queue.put(estate)
        # self.write_list_txtfile(estate_index, "estates_list.txt")


    def get_estate_detail(self, url, detail_queue, thread_id):
        print("Threading %d crawl %s" % thread_id, url)
        try:
            # html = self.get_local_html('test.html')
            html = self.get_html(url)
            print("Threading %d crawl %s" % thread_id, url)
        except Exception as e:
            print("Threading %d crawl %s FAIL!!!" % thread_id, url)
        else:
            estate_detail = self.get_list(html, "//html/body/div[5]/div[1]/ul/li")
        finally:
            pass;

        estate = 'id:"{}", name:"{}" , url:"{}"'.format(estate_id, estate_name, estate_detail_url)
        list_queue.put(estate)



    # 处理抓取的IP，按线程数量进行切片，分别获得每片的起始位置，然后用不同的线程读取不同的数据块
    def slice_list_and_multiple_threading_get_list(self,target_function, target_list):
        _queue = queue.Queue()
        crawl_thread = []

        # 计算目标数量，如能被线程整除，则分块
        target_count = len(target_list)
        if target_count % self.crawl_threading_number == 0:
            block_count = self.crawl_threading_number
            block_target_count = target_count // self.crawl_threading_number
        else:
            block_count = self.crawl_threading_number + 1
            block_target_count = target_count // (self.crawl_threading_number + 1)

        for i in range(0, block_count):
            print("block - " + str(i))
            # verify_ip(ip_port_list[i * intBlockIPCount: (i + 1) * intBlockIPCount], valid_ip_queue)
            thread = threading.Thread(target=target_function, args=(
                target_list[i * block_target_count: (i + 1) * block_target_count], _queue, i))
            crawl_thread.append(thread)

        start_time = time.time()
        print('Start : {}'.format(start_time))
        for i in range(len(crawl_thread)):
            crawl_thread[i].start()

        # 等待所有线程结束
        for i in range(len(crawl_thread)):
            crawl_thread[i].join()

        end_time = time.time()
        print('End : {}'.format(end_time))
        print("last time: {} s".format(time.time() - start_time))

        # self.write_proxy_queue(detail_queue, self.file_proxy_valid_list)

    # while not valid_ip_queue.empty():
    # 	print(valid_ip_queue.get())

    def main(self):



if __name__ == '__main__':
    clawler = CrawlerLianjiaEsatesIndex()
    clawler.main()
