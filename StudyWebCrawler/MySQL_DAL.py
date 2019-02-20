#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/2/18 23:00
# @Author  : flyhawk
# @Site    : 
# @File    : MySQL_DAL.py
# @Software: PyCharm


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

	'''
		函数名：CreateDB
		输入:数据库名称
		功能：创建数据库
		输出：无
	'''

	def CreateDB(self, db):
		try:
			self.cursor.execute('drop database if exists %s' % db)
			self.cursor.execute('create database %s' % db)
			self.Finish()
		except Exception as e:
			raise e

	'''
		函数名：ExecuteNoQuery
		输入:待执行的非查询SQL语句
		功能：执行sql语句
		输出：受影响的行数
	'''

	def ExecuteNoQuery(self, SQLstring):
		try:
			count = self.cursor.execute(SQLstring)
			self.Finish()
			return count
		except Exception as e:
			raise e

	'''
		函数名：ExecuteQuery
		输入:待执行的查询SQL语句
		功能：执行sql语句
		输出：查询的结果集
	'''

	def ExecuteQuery(self, SQLstring):
		try:
			self.cursor.execute(SQLstring)
			result = self.cursor.fetchall()  # 接收全部的返回结果行
			self.Finish()
			return result
		except Exception as e:
			raise e


'''
函数名：GetStringFromList
输入:待合并的列表
功能：把列表进行合并
输出：合并后的字符串  
'''


def GetStringFromList(list):
	str = ''
	for elem in list:
		str += elem
	return str
