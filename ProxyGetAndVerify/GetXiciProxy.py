# coding=utf-8
# <<<Web crawler I>>> : Get & Verify Proxy , written by HuangYu 20180814

import re  # 正则表达式库，用来匹配网页元素
import socket  # 用于设定网络连接的相关属性
# import sys
import requests  # 用于进行HTTP的相关处理，urllib库用起来还是比较烦的，requests用起来so easy
import logging  # log相关功能，不能总是用print那么low


class ProxyProber:

    def __init__(self):  # 类的初始化函数，在类中的函数都有个self参数，其实可以理解为这个类的对象

        self.file_proxy_all_list = "proxy_all.txt"  # 保存 免费代理服务器网站 爬下来的所有代理IP
        self.file_proxy_valid_list = "proxy_valid.txt"  # 保存 通过验证可用的 代理IP
        self.proxy_resource = "http://www.xicidaili.com/wn/"  # 用于爬取代理信息的网站
        self.verify_url = "http://www.baidu.com/"  # 用于验证Proxy IP的网站

        # 要为http报文分配header字段，否则很多页面无法获取
        self.http_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
            'Accept-Encoding': 'gzip, deflate'
        }
        # 配置log信息存储的位置
        logging.basicConfig(filename='./proxy_debug.log', filemode="w", level=logging.DEBUG)
        # 3秒内没有打开web页面，就放弃等待，防止死等，不管哪种语言，都要防范网络阻塞造成程序响应迟滞，CPU经常因此被冤枉
        socket.setdefaulttimeout(3)

    def getWebInfoByRe(self, context):  # 用于通过正则表达式取页面中的关键信息，context是页面内容
        ip_port_list = []
        get_ip_re = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")  # 取页面中所有格式为“数字.数字.数字.数字”的数据存入IP列表
        ip_list = get_ip_re.findall(str(context))
        get_port_raw_re = re.compile("<td>\d{2,5}</td>")  # 取页面中所有的格式为“<td>数字</td>”的数据存入Port草稿列表
        port_list_raw = get_port_raw_re.findall(str(context))
        get_port_re = re.compile("\d{5}|\d{4}|\d{2}")  # 取上一批数据中所有的 “数字” 存入Port列表
        port_list = get_port_re.findall(str(port_list_raw))

        if ip_list is None:
            return None
        if port_list is None:
            return None
        if len(ip_list) != len(port_list):  # 理论上IP和Port应该成对出现，没有再做太多的容错处理
            return None

        for index in range(len(ip_list)):  # 将IP和Port列表中的数据一一匹配成“IP:Port”的格式存入list
            ip_port_list.append(str(ip_list[index]) + ":" + str(port_list[index]))

        return ip_port_list

    def getProxyResource(self, url):  # 获取代理服务器网站信息，并保存

        if len(url) == 0:
            print("Url is null!")
            return

        requests.adapters.DEFAULT_RETRIES = 5
        proxy_resource_request = requests.session()
        proxy_resource_request.keep_alive = False
        # 获取url内容
        try:
            proxy_resource_result = proxy_resource_request.get(url, headers=self.http_headers)
        except:
            print("proxy_resource can't get!!!")
            return
        # 页面内容存入log文件，爬页面的时候，都要获取页面源码分析其中的关键元素；当然，你也可以使用浏览器的debug组件分析
        logging.debug(proxy_resource_result.content)

        # 开始提取页面中的IP和Port列表
        proxy_list = self.getWebInfoByRe(proxy_resource_result.content)

        # 统计list元素个数
        print(len(proxy_list))

        if len(proxy_list) == 0:
            print("Get Proxy fail!")
            return

        # 将list中所有信息写入proxy_all.txt
        fd_proxy_all = open(self.file_proxy_all_list, 'w')

        # with as 语法的使用，可以省去close文件的过程
        with open(self.file_proxy_all_list, 'w') as fd_proxy_all:
            for ip_port in proxy_list:
                fd_proxy_all.write(str(ip_port) + "\n")

    def verifyProxy(self):  # 从proxy_all.txt获取所有Proxy IP进行验证，将有效的IP存入proxy_valid.txt
        index = 0
        requests.adapters.DEFAULT_RETRIES = 5
        test_proxy = requests.session()
        test_proxy.keep_alive = False

        # 将proxy_all.txt中所有信息读到ip_port_list中，
        with open(self.file_proxy_all_list, 'r') as fd_proxy_all:
            ip_port_list = fd_proxy_all.readlines()  # 读取全部内容

        # 创建一个新的proxy_valid.txt
        try:
            fd_proxy_valid = open(self.file_proxy_valid_list, 'w')
        except:
            print("proxy_valid.txt open is fail!")
            return
        finally:
            fd_proxy_valid.close()

        for ip_port in ip_port_list:
            proxy_url = {'http': 'http://' + ip_port.strip(
                '\n')}  # request.get信息中需要填写proxies字段，字段的format={'http':'http://ip:port'}
            # 因为读回的信息每一行都有"\n"，所以需要用.strip过滤掉"\n"

            index += 1
            print(str(index))

            try:
                # 通过request.get获取验证页面，timeout用于防止 傻等，毕竟要验证一堆IP
                test_page = test_proxy.get(self.verify_url, headers=self.http_headers, proxies=proxy_url,
                                           timeout=(2, 3))
            except:  # 如果获取页面异常，进入这儿，再处理下一个IP
                print("Invaild Proxy : " + ip_port.strip('\n'))
                continue
            # 获取正常的页面返回码一般都是200，不是的话继续处理下一个IP
            if test_page.status_code != 200:
                print("Invaild Proxy : " + ip_port.strip('\n'))
                continue

            # 能用的IP存入proxy_valid.txt
            print("*********Vaild Proxy : " + ip_port.strip('\n'))
            with open(self.file_proxy_valid_list, 'a') as fd_proxy_valid:
                fd_proxy_valid.write(ip_port.strip('\n') + " " + str(test_page.elapsed.total_seconds()) + "\n")


if __name__ == "__main__":
    prober_handler = ProxyProber()
    # prober_handler.getProxyResource(sys.argv[1])
    # prober_handler.getProxyResource("http://www.xicidaili.com/wn/")
    prober_handler.getProxyResource(prober_handler.proxy_resource)  # 对象名=self，看到这就可以理解类里的self是什么了。
    prober_handler.verifyProxy()

