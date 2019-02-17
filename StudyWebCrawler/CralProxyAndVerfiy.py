#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/16 21:46
# @Author  : flyhawk
# @Site    : 
# @File    : CralProxyAndVerfiy.py
# @Software: PyCharm


import requests
from lxml import etree
import logging  # log相关功能，不能总是用print那么low
import socket  # 用于设定网络连接的相关属性
import threading # 导入线程包
import queue  # 多线程传递验证通过的IP, 保证线程安全
import os
import time


class ProxyCrawlerAndVerfiy:

	def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象

		self.file_proxy_all_list = "proxy_all.txt"  # 保存 免费代理服务器网站 爬下来的所有代理IP
		self.file_proxy_valid_list = "proxy_valid.txt"  # 保存 通过验证可用的 代理IP
		self.proxy_resource_Url = "http://www.xicidaili.com/nn/"  # 用于爬取代理信息的网站
		self.verify_url = "http://www.baidu.com/"  # 用于验证Proxy IP的网站
		self.proxy_resource_page = 2   # 获取代理页面数量
		self.verify_threading_number = 10   #验证IP线程数量

		# 要为http报文分配header字段，否则很多页面无法获取
		self.http_headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
			'Accept-Encoding': 'gzip, deflate'
		}
		# 配置log信息存储的位置
		logging.basicConfig(filename='./proxy_debug.log', filemode="w", level=logging.DEBUG)
		# 3秒内没有打开web页面，就放弃等待，防止死等，不管哪种语言，都要防范网络阻塞造成程序响应迟滞，CPU经常因此被冤枉
		socket.setdefaulttimeout(3)

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

	# 获取ip
	# 解析网页，并得到网页中的代理IP,保存为文件
	def get_proxy(self, html):
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
		self.write_proxy(proxies, self.file_proxy_all_list)

	def get_html(self, url):
		header = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/67.0.3396.99 Safari/537.36",
		}
		response = requests.get(url, headers=header)
		# print(response.text)
		return response.text

	# 验证IP
	def verifyProxy(self):  # 从proxy_all.txt获取所有Proxy IP进行验证，将有效的IP存入proxy_valid.txt
		def verify_ip(ip_port_list, valid_ip_queue, id):
			index = 0
			requests.adapters.DEFAULT_RETRIES = 5
			test_proxy = requests.session()
			test_proxy.keep_alive = False

			for ip_port in ip_port_list:
				proxy_url = {'http': 'http://' + ip_port.strip('\n')}
				# request.get信息中需要填写proxies字段，字段的format={'http':'http://ip:port'}
				# 因为读回的信息每一行都有"\n"，所以需要用.strip过滤掉"\n"

				try:
					# 通过request.get获取验证页面，timeout用于防止 傻等，毕竟要验证一堆IP
					test_page = test_proxy.get(self.verify_url, headers=self.http_headers, proxies=proxy_url, timeout=(2, 3))
				except:  # 如果获取页面异常，进入这儿，再处理下一个IP
					print("Threading %d : Invaild Proxy : " % id + ip_port.strip('\n'))
					logging.info("Threading %d : Invaild Proxy : " % id + ip_port.strip('\n'))
					continue
				# 获取正常的页面返回码一般都是200，不是的话继续处理下一个IP
				if test_page.status_code != 200:
					print("Threading %d : Invaild Proxy : " % id + ip_port.strip('\n'))
					logging.info("Threading %d : Invaild Proxy : " % id + ip_port.strip('\n'))
					continue

				# 能用的IP存入proxy_valid.txt
				print("********Threading %d : Vaild Proxy : " % id + ip_port.strip('\n'))
				logging.info("********Threading %d : Vaild Proxy : " % id + ip_port.strip('\n'))
				valid_ip_queue.put(ip_port)

		# 处理抓取的IP，按线程数量进行切片，分别获得每片的起始位置，然后用不同的线程读取不同的数据块
		def slice_ip_list():
			valid_ip_queue = queue.Queue()
			verify_ip_thread = []
			# 将proxy_all.txt中所有信息读到ip_port_list中，
			with open(self.file_proxy_all_list, 'r') as fd_proxy_all:
				ip_port_list = fd_proxy_all.readlines()  # 读取全部内容

			intIPCount = len(ip_port_list)
			if intIPCount % self.verify_threading_number == 0:
				intBlock = self.verify_threading_number
				intBlockIPCount = intIPCount // self.verify_threading_number
			else:
				intBlock = self.verify_threading_number + 1
				intBlockIPCount = intIPCount // (self.verify_threading_number + 1)

			for i in range(0, intBlock):
				print("block - " + str(i))
				# verify_ip(ip_port_list[i * intBlockIPCount: (i + 1) * intBlockIPCount], valid_ip_queue)
				thread = threading.Thread(target=verify_ip, args=(
				ip_port_list[i * intBlockIPCount: (i + 1) * intBlockIPCount], valid_ip_queue, i))
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

			self.write_proxy_queue(valid_ip_queue, self.file_proxy_valid_list)
			# while not valid_ip_queue.empty():
			# 	print(valid_ip_queue.get())

		slice_ip_list()

	# 代理IP的信息存储
	def write_proxy(self, proxies, filename):
		# print(proxies)
		for proxy in proxies:
			# with as 语法的使用，可以省去close文件的过程
			with open(filename, 'a+', encoding="UTF-8") as f:
				logging.info("Writing ：%s" % proxy)
				f.write(proxy + '\n')
		logging.info("Finish Writing!!!")

	def write_proxy_queue(self, valid_ip_queue, filename):
		# print(proxies)
		while not valid_ip_queue.empty():
			proxy = valid_ip_queue.get()
			# with as 语法的使用，可以省去close文件的过程
			with open(filename, 'a+', encoding="UTF-8") as f:
				logging.info("Writing ：%s" % proxy)
				f.write(proxy)
		logging.info("Finish Writing!!!")

	def main(self):
		# 获取IP
		for i in range(1, self.proxy_resource_page + 1):
			url = self.proxy_resource_Url + str(i)
			logging.info('Crawl %s' % url)
			html = self.get_html(url)
			logging.info('parse proxy')
			self.get_proxy(html)

		self.verifyProxy()


if __name__ == '__main__':
	proxyCrawlerAndVerfiy = ProxyCrawlerAndVerfiy()
	proxyCrawlerAndVerfiy.main()

