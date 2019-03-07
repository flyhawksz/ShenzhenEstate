#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Mysql_connect_pool_tools import MyPymysqlPool
import logging  # log相关功能，不能总是用print那么low


# 生成数据库相关表
class CreateTables:
    
    def __init__(self):
        # 配置log信息存储的位置
        logging.basicConfig(filename='./debug.log', filemode="w", level=logging.DEBUG)
        
        logging.info("create_mysql")
        self.mysql = MyPymysqlPool(self.connargs)
        
        self.connargs = {"host": "localhost", "port": "3306", "user": "root", "passwd": "123456", "db": "test"}

        self.t_EstateDetail = 't_EstateDetail'
        self.sql_t_EstateDetail = '''
        CREATE TABLE IF NOT EXISTS szEstate.t_EstateDetail ( 
        id INT COMMENT 'id',
        lianjiaID INT COMMENT '链家编号',
        cityID INT COMMENT '城市ID',
        city VARCHAR(10) COMMENT '城市',
        districtID INT COMMENT '区ID',
        district VARCHAR(10) COMMENT '区',
        bizCircleID INT COMMENT '商圈ID',
        bizCircle VARCHAR(10) COMMENT '商圈',
        subStation VARCHAR(30) COMMENT '近地铁站',
        communityID INT COMMENT '小区ID',
        communityName VARCHAR(30) COMMENT '小区名称',
        house-title VARCHAR(80) COMMENT '房产名称',
        isDealed INT COMMENT '已成交/在售',
        saleDate DATETIME COMMENT '挂牌日期',
        callTotalPrice INT COMMENT '挂牌价格（万）',
        callPrice INT COMMENT '挂牌单价（元/平）',
        dealDate DATETIME COMMENT '成交日期',
        dealTotalPrice INT COMMENT '成交价格（万）',
        dealPrice INT COMMENT '成交单价（元/平）',
        dealDays INT COMMENT '成交周期（天）',
        changePrice INT COMMENT '调价（次）',
        takeVisit INT COMMENT '带看（次）',
        concerned INT COMMENT '关注（人）',
        visitedCount INT COMMENT '浏览（次）',
        houseType VARCHAR(30) COMMENT '房屋户型',
        floorNumber VARCHAR(30) COMMENT '所在楼层',
        buildingArea VARCHAR(30) COMMENT '建筑面积',
        buildingStructure VARCHAR(30) COMMENT '户型结构',
        innerArea VARCHAR(30) COMMENT '套内面积',
        buildingType VARCHAR(30) COMMENT '建筑类型',
        buildingToward VARCHAR(30) COMMENT '房屋朝向',
        builtYear VARCHAR(30) COMMENT '建成年代',
        decoration VARCHAR(30) COMMENT '装修情况',
        buildingConstruction VARCHAR(30) COMMENT '建筑结构',
        heatWay VARCHAR(30) COMMENT '供暖方式',
        stairs2Family VARCHAR(30) COMMENT '梯户比例',
        estateRightYear VARCHAR(30) COMMENT '产权年限',
        hasElevator VARCHAR(30) COMMENT '配备电梯',
        limitedYear VARCHAR(30) COMMENT '房屋年限',
        dealType VARCHAR(30) COMMENT '交易权属',
        usageTpye VARCHAR(30) COMMENT '房屋用途',
        belongging VARCHAR(30) COMMENT '房权所属',
        )
        -----Create table [t_EstateDetail] end.
        '''

        self.t_CommunitiesDetail = 't_CommunitiesDetail'
        self.sql_t_CommunitiesDetail = '''
        CREATE TABLE IF NOT EXISTS szEstate.t_CommunitiesDetail ( 
        id INT COMMENT 'id',
        cityID INT COMMENT '城市ID',
        city VARCHAR(10) COMMENT '城市',
        districtID INT COMMENT '区ID',
        district VARCHAR(10) COMMENT '区',
        bizCircleID INT COMMENT '商圈ID',
        bizCircle VARCHAR(10) COMMENT '商圈',
        buildedYear VARCHAR(20) COMMENT '建成年份',
        subStation VARCHAR(30) COMMENT '近地铁站',
        communityID INT COMMENT '小区ID',
        communityName VARCHAR(30) COMMENT '小区名称',
        houseCount VARCHAR(30) COMMENT '户型数量',
        dealedInNinetyDays INT COMMENT '90天成交',
        rentingNow INT COMMENT '正在出租'
        )
        -----Create table [t_CommunitiesDetail] end.
        '''

        self.t_bizCircle = 't_bizCircle '
        self.sql_t_bizCircle = '''
        CREATE TABLE IF NOT EXISTS szEstate.t_bizCircle ( 
        id INT COMMENT 'id',
        cityID INT COMMENT '城市ID',
        city VARCHAR(10) COMMENT '城市',
        districtID INT COMMENT '区ID',
        district VARCHAR(10) COMMENT '区',
        bizCircleID INT COMMENT '商圈ID',
        bizCircle VARCHAR(10) COMMENT '商圈'
        )
        -----Create table [t_bizCircle] end.
        '''
        self.t_district = 't_district'
        self.sql_t_district = '''
        CREATE TABLE IF NOT EXISTS szEstate.t_district ( 
        id INT COMMENT 'id',
        cityID INT COMMENT '城市ID',
        city VARCHAR(10) COMMENT '城市',
        districtID INT COMMENT '区ID',
        district VARCHAR(10) COMMENT '区'
        )
        -----Create table [t_district] end.
        '''
        
        self.t_city = 't_city'
        self.sql_t_city = '''
        CREATE TABLE IF NOT EXISTS szEstate.t_city ( 
        id INT COMMENT 'id',
        cityID INT COMMENT '城市ID',
        city VARCHAR(10) COMMENT '城市'
        )
        -----Create table [t_city] end.
        '''
 
    def __del__(self):
        if self.mysql:
            self.mysql.dispose
 
    # 生成MySQL数据库连接池
    def create_mysql(self, connargs):
        logging.info("create_mysql")
        self.mysql = MyPymysqlPool(connargs)
 
    def create_tables(self):
        
        if not self.mysql.hasThisTable(self.t_city):
            self.mysql.insert(self.sql_t_city)
 
        if not self.mysql.hasThisTable(self.t_district):
            self.mysql.insert(self.sql_t_district)

        if not self.mysql.hasThisTable(self.t_bizCircle):
            self.mysql.insert(self.sql_t_bizCircle)

        if not self.mysql.hasThisTable(self.t_CommunitiesDetail):
            self.mysql.insert(self.sql_t_CommunitiesDetail)
            
        if not self.mysql.hasThisTable(self.t_EstateDetail):
            self.mysql.insert(self.sql_t_EstateDetail)
            
class entiy_city:
    pass


