#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Mysql_connect_pool_tools import MyPymysqlPool
import logging  # log相关功能，不能总是用print那么low


# 生成数据库相关表
class CreateTables:
    
    def __init__(self):
        self.conn_args = {"host": "localhost", "port": "3306", "user": "root", "passwd": "123456", "db": "szestate"}
        
        # 配置log信息存储的位置
        logging.basicConfig(filename='./CreateTables_debug.log', filemode="w", level=logging.DEBUG)
        
        logging.info("create_mysql")
        self.mysql = MyPymysqlPool(self.conn_args)

        self.t_EstateDetail = 't_EstateDetail'
        self.sql_t_EstateDetail = ('CREATE TABLE IF NOT EXISTS szEstate.t_EstateDetail ( '
            'id int not null AUTO_INCREMENT PRIMARY KEY, '
            'lianjiaID INT, '
            'cityID INT, '
            'city VARCHAR(10), '
            'districtID INT, '
            'district VARCHAR(10), '
            'bizCircleID INT, '
            'bizCircle VARCHAR(10), '
            'subStation VARCHAR(30), '
            'communityID INT, '
            'communityName VARCHAR(30), '
            'houseTitle VARCHAR(80), '
            'isDealed INT, '
            'saleDate DATETIME, '
            'callTotalPrice INT, '
            'callPrice INT, '
            'dealDate DATETIME, '
            'dealTotalPrice INT, '
            'dealPrice INT, '
            'dealDays INT, '
            'changePrice INT, '
            'takeVisit INT, '
            'concerned INT, '
            'visitedCount INT, '
            'houseType VARCHAR(30), '
            'floorNumber VARCHAR(30), '
            'buildingArea VARCHAR(30), '
            'buildingStructure VARCHAR(30), '
            'innerArea VARCHAR(30), '
            'buildingType VARCHAR(30), '
            'buildingToward VARCHAR(30), '
            'builtYear VARCHAR(30), '
            'decoration VARCHAR(30), '
            'buildingConstruction VARCHAR(30), '
            'heatWay VARCHAR(30), '
            'stairs2Family VARCHAR(30), '
            'estateRightYear VARCHAR(30), '
            'hasElevator VARCHAR(30), '
            'limitedYear VARCHAR(30), '
            'dealType VARCHAR(30), '
            'usageTpye VARCHAR(30), '
            'belongging VARCHAR(30)'
            ')')

        self.t_CommunitiesDetail = 't_CommunitiesDetail'
        self.sql_t_CommunitiesDetail = ('CREATE TABLE IF NOT EXISTS szEstate.t_CommunitiesDetail ( '
            'id int not null AUTO_INCREMENT PRIMARY KEY, '
            'cityID INT, '
            'city VARCHAR(10), '
            'districtID INT, '
            'district VARCHAR(10), '
            'bizCircleID INT, '
            'bizCircle VARCHAR(10), '
            'buildedYear VARCHAR(20), '
            'subStation VARCHAR(30), '
            'communityID INT, '
            'communityName VARCHAR(30), '
            'houseCount VARCHAR(30), '
            'dealedInNinetyDays INT, '
            'rentingNow INT'
            ')')


        self.t_bizCircle = 't_bizCircle '
        self.sql_t_bizCircle =('CREATE TABLE IF NOT EXISTS szEstate.t_bizCircle ( '
            'id int not null AUTO_INCREMENT PRIMARY KEY, '
            'cityID INT, '
            'city VARCHAR(10), '
            'districtID INT, '
            'district VARCHAR(10), '
            'bizCircleID INT, '
            'bizCircle VARCHAR(10)'
            ')')
        
        self.t_district = 't_district'
        self.sql_t_district = ('CREATE TABLE IF NOT EXISTS szEstate.t_district ( '
            'id int not null AUTO_INCREMENT PRIMARY KEY, '
            'cityID INT, '
            'city VARCHAR(10), '
            'districtID INT, '
            'district VARCHAR(10)'
            ')')
        
        self.t_city = 't_city'
        self.sql_t_city = ('CREATE TABLE IF NOT EXISTS szEstate.t_city ( '
            'id int not null AUTO_INCREMENT PRIMARY KEY, '
            'cityID INT, '
            'city VARCHAR(10)'
            ')')
 
    def __del__(self):
        if self.mysql:
            self.mysql.dispose
 
    # 生成MySQL数据库连接池
    def create_mysql(self):
        logging.info("create_mysql")
        if not self.mysql:
            self.mysql = MyPymysqlPool(self.conn_args)
 
    def create_tables(self):
        
        if not self.mysql.hasThisTable(self.t_city):
            # t = self.sql_t_city.replace("\\", "",)
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
    def __init__(self):
        self.cityID
        self.city


class district:
    def __init__(self):
        self.id  # id
        self.cityID  # 城市ID
        self.city  # 城市
        self.districtID  # 区ID
        self.district  # 区


class bizCircle:
    def __init__(self):
        self.id  # id
        self.cityID  # 城市ID
        self.city  # 城市
        self.districtID  # 区ID
        self.district  # 区
        self.bizCircleID  # 商圈ID
        self.bizCircle  # 商圈


class CommunitiesDetail:
    def __init__(self):
        self.id  # id
        self.cityID  # 城市ID
        self.city  # 城市
        self.districtID  # 区ID
        self.district  # 区
        self.bizCircleID  # 商圈ID
        self.bizCircle  # 商圈
        self.buildedYear  # 建成年份
        self.subStation  # 近地铁站
        self.communityID  # 小区ID
        self.communityName  # 小区名称
        self.houseCount  # 户型数量
        self.dealedInNinetyDays  # 90天成交
        self.rentingNow  # 正在出租


class EstateDetail:
    def __init__(self):
        self.id  # id
        self.lianjiaID  # 链家编号
        self.cityID  # 城市ID
        self.city  # 城市
        self.districtID  # 区ID
        self.district  # 区
        self.bizCircleID  # 商圈ID
        self.bizCircle  # 商圈
        self.subStation  # 近地铁站
        self.communityID  # 小区ID
        self.communityName  # 小区名称
        self.houseTitle  # 房产名称
        self.isDealed  # 已成交/在售
        self.saleDate  # 挂牌日期
        self.callTotalPrice  # 挂牌价格（万）
        self.callPrice  # 挂牌单价（元/平）
        self.dealDate  # 成交日期
        self.dealTotalPrice  # 成交价格（万）
        self.dealPrice  # 成交单价（元/平）
        self.dealDays  # 成交周期（天）
        self.changePrice  # 调价（次）
        self.takeVisit  # 带看（次）
        self.concerned  # 关注（人）
        self.visitedCount  # 浏览（次）
        self.houseType  # 房屋户型
        self.floorNumber  # 所在楼层
        self.buildingArea  # 建筑面积
        self.buildingStructure  # 户型结构
        self.innerArea  # 套内面积
        self.buildingType  # 建筑类型
        self.buildingToward  # 房屋朝向
        self.builtYear  # 建成年代
        self.decoration  # 装修情况
        self.buildingConstruction  # 建筑结构
        self.heatWay  # 供暖方式
        self.stairs2Family  # 梯户比例
        self.estateRightYear  # 产权年限
        self.hasElevator  # 配备电梯
        self.limitedYear  # 房屋年限
        self.dealType  # 交易权属
        self.usageTpye  # 房屋用途
        self.belongging  # 房权所属


if __name__ == '__main__':
    do = CreateTables()
    # do.create_mysql()
    do.create_tables()
