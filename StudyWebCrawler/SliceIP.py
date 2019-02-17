#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/17 19:07
# @Author  : flyhawk
# @Site    : 
# @File    : SliceIP.py
# @Software: PyCharm


import os
import requests
import queue
import threading
import time

file_proxy_valid_list = "proxy_valid.txt"  # 保存 通过验证可用的 代理IP
file_proxy_all_list = "proxy_all.txt"  # 保存 免费代理服务器网站 爬下来的所有代理IP
verify_threading_number = 5   #验证IP线程数量
verify_url = "http://www.baidu.com/"  # 用于验证Proxy IP的网站
http_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept-Encoding': 'gzip, deflate'
        }


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
			test_page = test_proxy.get(verify_url, headers=http_headers, proxies=proxy_url, timeout=(2, 3))
		except:  # 如果获取页面异常，进入这儿，再处理下一个IP
			print("Threading %d : Invaild Proxy : " % id + ip_port.strip('\n'))
			continue
		# 获取正常的页面返回码一般都是200，不是的话继续处理下一个IP
		if test_page.status_code != 200:
			print("Threading %d : Invaild Proxy : " % id + ip_port.strip('\n'))
			continue

		# 能用的IP存入proxy_valid.txt
		print("********Threading %d : Vaild Proxy : " % id + ip_port.strip('\n'))
		valid_ip_queue.put(ip_port)
		# with open(file_proxy_valid_list, 'a+') as fd_proxy_valid:
		# 	fd_proxy_valid.write(ip_port.strip('\n') + " " + str(test_page.elapsed.total_seconds()) + "\n")


def main():
	valid_ip_queue = queue.Queue()
	verify_ip_thread = []
	# 将proxy_all.txt中所有信息读到ip_port_list中，
	with open(file_proxy_all_list, 'r') as fd_proxy_all:
		ip_port_list = fd_proxy_all.readlines()  # 读取全部内容

	intIPCount = len(ip_port_list)
	if intIPCount % verify_threading_number == 0:
		intBlock = verify_threading_number
		intBlockIPCount = intIPCount // verify_threading_number
	else:
		intBlock = verify_threading_number + 1
		intBlockIPCount = intIPCount // (verify_threading_number + 1)

	for i in range(0, intBlock):
		print("block - " + str(i))
		# verify_ip(ip_port_list[i * intBlockIPCount: (i + 1) * intBlockIPCount], valid_ip_queue)
		thread = threading.Thread(target=verify_ip, args=(ip_port_list[i * intBlockIPCount: (i + 1) * intBlockIPCount], valid_ip_queue, i))
		verify_ip_thread.append(thread)

	start_time = time.time()

	for i in range(len(verify_ip_thread)):
		verify_ip_thread[i].start()

	# 等待所有线程结束
	for i in range(len(verify_ip_thread)):
		verify_ip_thread[i].join()

	while not valid_ip_queue.empty():
		print(valid_ip_queue.get())



if __name__ == '__main__':
	main()
	# test()
	# print(ip_port_list)