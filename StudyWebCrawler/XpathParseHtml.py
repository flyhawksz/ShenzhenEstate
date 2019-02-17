from lxml import etree

wb_data = """
        <div>
            <ul>
                 <li class="item-0"><a href="link1.html">first item</a></li>
                 <li class="item-1"><a href="link2.html">second item</a></li>
                 <li class="item-inactive"><a href="link3.html">third item</a></li>
                 <li class="item-1"><a href="link4.html">fourth item</a></li>
                 <li class="item-0"><a href="link5.html">fifth item</a>
             </ul>
         </div>
        """


def html_test():
	html = etree.HTML(wb_data)
	print(html)
	result = etree.tostring(html)
	print(result.decode("utf-8"))


#获取某个标签的内容(基本使用)
def html_test2():
	html = etree.HTML(wb_data)
	html_data = html.xpath("/html/body/div/ul/li/a")
	print(html)
	for i in html_data:
		print(i.text)


def html_test3():
	html = etree.HTML(wb_data)
	html_data = html.xpath("//*")
	print(html)
	for i in html_data:
		if hasattr(i, 'tag'): print(i.tag + "-")
		if hasattr(i, 'attribute'): print(i.attribute + "-")
		if hasattr(i, 'text'): print(i.text)
		# print(i.tag + "-" + i.attribute + "-" + i.text)


# 打开读取html文件,
# 打印是一个列表，需要遍历
def html_test4():
	html = etree.parse('./test.html')
	html_data = html.xpath("//*")
	print(html)
	for i in html_data:
		if hasattr(i, 'tag'): print(i.tag + "-")
		if hasattr(i, 'attribute'): print(i.attribute + "-")
		if hasattr(i, 'text'): print(i.text)


# 打印指定路径下a标签的属性（可以通过遍历拿到某个属性的值，查找标签的内容）
def html_test5():
	html = etree.parse('./test.html')
	html_data1 = html.xpath("//div/ul/li/a")
	html_data = html.xpath("//div/ul/li/a/@href")
	print(html_data)
	for i in html_data:
		print(i)
	for i in html_data1:
		print(i.text)


# 查到绝对路径下a标签属性等于link2.html的内容。
def html_test6():
	html = etree.parse('./test.html')
	html_data = html.xpath("//div/ul/li/a[@href = 'link3.html']")
	html_data1 = html.xpath("//div/ul/li/a/text()")
	print(html_data)
	for i in html_data:
		print(i.text)
	for i in html_data1:
		print(i)


# 相对路径下
def html_test7():
	html = etree.parse('./test.html')
	html_data = html.xpath("//div/ul/li[last()]/a")   #xpath中要加括号
	# html_data1 = html.xpath("//div/ul/li/a/text()")
	print(html_data)
	for i in html_data:
		print(i.text)                                 #属性不加括号


def main():
	html_test7()


if __name__ == "__main__":
	main()
