# -*- coding: utf-8 -*-

##############################################################################
#
#
#
##############################################################################

from imp import reload
import basic
reload(basic)
from basic import public
DEBUG,CLIENT_NAME=public.DEBUG,public.CLIENT_NAME
 


if DEBUG == '1':
    import admin.dl.BASE_DL
    reload(admin.dl.BASE_DL)
from admin.dl.BASE_DL  import cBASE_DL
import hashlib , os , time , random

 
class cC002_dl(cBASE_DL):
    
    def init_data(self):

        self.GNL = ['', '商品编号', '店铺', '分类', '标题','图片','状态',
                    '推荐状态','总库存','原价','最低价','商品数据']

        
        self.src = 'C002'


    def mRight(self):
            
        sql = """
            SELECT
                D.id,
                s.name,--D.shopid ,
                g.name,--D.categoryid,
               
                D.name,
                D.pic,
                case when D.status=0 then '上架' else '下架' end,
                D.recommendstatus,
                D.stores,
                D.originalprice ,
                D.minprice ,
                D.characteristic
                
                --to_char(D.ctime,'YYYY-MM-DD HH:MM'),
                --to_char(D.utime,'YYYY-MM-DD HH:MM')
            FROM goods_info D
            left join shopname  s on s.id=D.shopid and s.usr_id=D.usr_id
            left join goods_category g on g.id=D.categoryid and D.usr_id=g.usr_id
           where COALESCE(D.del_flag,0)!=1 and  D.usr_id=%s
        """%self.usr_id
        

        if self.orderby != '':
            sql += ' ORDER BY %s %s' % (self.orderby, self.orderbydir)
        else:
            sql += " ORDER BY D.id DESC"
        #print(sql)
        L, iTotal_length, iTotal_Page, pageNo, select_size = self.db.select_for_grid(sql, self.pageNo)
        PL = [pageNo, iTotal_Page, iTotal_length, select_size]
        return PL, L
    
    def get_local_data(self):
        #这里请获取表单所有内容。包括gw_doc表的title

        L = {}
        sql="""
             SELECT
                D.id,
                D.categoryid,
                D.barcode,
                D.videoid,
                D.name,
                D.characteristic,
                D.paixu,
                D.status,
                D.pic,
                D.content,
                D.originalprice,
                D.minprice,
                D.stores,
                D.numberorders,
                D.weight,
                D.datestartstr,
                D.dateendstr,
                D.see,
                D.pt,
                D.buyamount,
                D.recommendstatus,
                D.propertyids,
                D.hyprice,
                D.ptprice 
                           
                --to_char(D.ctime,'YYYY-MM-DD HH:MM'),
                --to_char(D.utime,'YYYY-MM-DD HH:MM')
            FROM goods_info D
           where D.id=%s
        """%self.pk
        if self.pk != '':
            L = self.db.fetch(sql)

        return L

    def get_pics_data(self):
        L = []
        sql = """
               select pic from goods_pics where goods_id=%s
                """ % self.pk
        if self.pk != '':
            l,t= self.db.select(sql)
            if t>0:
                for i in l:
                    L.append(i[0])

        return L
    def local_add_save(self):
        
        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        pk 已经传进来  是 gw_doc 的 ID 请勿弄错
        """

        # 这些是表单值
        dR = {'R':'', 'MSG':'提交成功'}
        pk=self.pk
        shopid=self.GP('shopid',0)#所属店铺
        categoryid = self.GP('categoryid',0)#商品分类
        barcode =self.GP('barcode','')#条码编号
        videoid = self.GP('videoid', '')#视频编号
        name = self.GP('name', '')#商品名称
        characteristic = self.GP('characteristic', '')#商品特色
        logisticsid=self.GP('logisticsid','')#选择物流模板
        paixu = self.GP('paixu', '')#排序
        recommendstatus = self.GP('recommendstatus','')#是否推荐
        status = self.GP('status', '')#商品状态
        content = self.GP('text_contents', '')#详情介绍

        originalprice=self.GP('originalprice','')#原价
        minprice=self.GP('minprice','')#现价
        hyprice = self.GP('hyprice', '')  # 现价
        stores=self.GP('stores','')#库存数
        numberorders=self.GP('numberorders','')#订单数
        weight=self.GP('weight','')#商品重量
        datestartstr=self.GP('datestartstr','')#起售时间
        dateendstr=self.GP('dateendstr','')#停售时间
        see=self.GP('see','')#浏览量
        buyamount=self.GP('buyamount','')#订单数
        pt = self.GP('pt','')  # 是否拼团
        ptprice = self.GP('ptprice', '')  # 拼团价

        property_sel1=self.GP('property_sel1','')#规格尺寸1
        propertyids=property_sel1
        property_seln = self.GP('property_seln','')  # 规格尺寸1
        if property_seln!='':
            propertyids=str(property_sel1)+','+str(property_seln)


        data = {
            'shopid': shopid,
            'categoryid': categoryid,
            'barcode': barcode,
            'videoid': videoid,
            'name': name,
            'characteristic': characteristic,
            'logisticsid': logisticsid,
            'paixu': paixu,
            'recommendstatus': recommendstatus,
            'status': status,
            'content': content,
            'originalprice': originalprice,
            'minprice': minprice,
            'stores': stores,
            'numberorders': numberorders,
            'weight': weight,
            'datestartstr': datestartstr,
            'dateendstr': dateendstr,
            'see': see,
            'buyamount': buyamount,
            'propertyids ': propertyids,
            'pt':pt,
            'hyprice':hyprice,
            'ptprice':ptprice

        }

        # for k in list(data):
        #     if data[k] == '':
        #         data.pop(k)

        if pk != '':  # update
            data['uid']=self.usr_id
            data['utime'] = self.getToday(9)
            self.db.update('goods_info' , data , " id = %s " % self.pk)

        else:  # insert
            data['usr_id']= self.usr_id
            data['cid'] = self.usr_id
            data['ctime'] = self.getToday(9)
            self.db.insert('goods_info' , data)
            pk = self.db.insertid('goods_info_id')  # 这个的格式是表名_自增字段
            # dR['isadd'] = 1
            #
        dR['pk'] = pk
        self.save_pics(pk)
        self.save_gg(pk)
            
        return dR

    def save_pics(self,pk):


        try:

            files = self.REQUEST.getlist('pics')

            if files:
                sqldel = "delete from goods_pics where goods_id=%s " % pk
                self.db.query(sqldel)
                sql=""
                i=0
                for file in files:
                    if i==0:
                        sqlu="update goods_info set pic=%s where id=%s"
                        self.db.query(sqlu,[file,pk])
                    else:
                        if sql == '':
                            sql+="insert into goods_pics(goods_id,pic,cid,ctime)values(%s,'%s',%s,now())"%(pk,file,self.usr_id)
                        else:
                            sql += ",(%s,'%s',%s,now())" % (pk,file,self.usr_id)
                    i+=1
                if sql!='':
                    self.db.query(sql)
        except:
            pass

    def save_gg(self,pk):
        ggname = self.REQUEST.getlist('ggname')  # 原价
        originalpriceext = self.REQUEST.getlist('originalpriceext')  # 原价
        minpriceext = self.REQUEST.getlist('minpriceext')  # 现价
        ptpriceext =  self.REQUEST.getlist('ptpriceext')  # 拼团价
        scoreext = self.REQUEST.getlist('scoreext')  # 积分
        storesext = self.REQUEST.getlist('storesext')  # 库存数
        property_child_ids  = self.REQUEST.getlist('property_child_ids')  # 规格


        sqldel = "delete from wechat_mall_goods_property_child_price where goods_id=%s " % pk
        self.db.query(sqldel)
        sql = ''
        for i in range(len(ggname)):
            if ggname[i] != '':
                if scoreext[i] == '':
                    scoreext[i] = 0
                if sql == '':
                    sql = """ insert into wechat_mall_goods_property_child_price(usr_id,goods_id,ggname,originalpriceext,minpriceext,scoreext,storesext,ptpriceext,property_child_ids,cid,ctime)
                                               values (%s,%s,'%s',%s,%s,%s,%s,%s,'%s',%s,now())
                                           """ % (self.usr_id,pk,ggname[i], originalpriceext[i], minpriceext[i], scoreext[i],storesext[i], ptpriceext[i],property_child_ids[i],self.usr_id)
                else:
                    sql += ",(%s,%s,'%s',%s,%s,%s,%s,%s,'%s',%s,now())" % (self.usr_id,pk,ggname[i], originalpriceext[i], minpriceext[i], scoreext[i],storesext[i],ptpriceext[i],property_child_ids[i], self.usr_id)
        if sql != '':
            self.db.query(sql)


        
    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update goods_info set del_flag=1 where id= %s" % pk)
        return dR

    def good_list(self):
        sql="select id,name from goods_category where usr_id=%s and COALESCE(del_flag,0)!=1"%self.usr_id
        l,t=self.db.select(sql)
        return l

    def shop_list(self):
        sql="select id,name from shopname where usr_id =%s"%self.usr_id
        l,t=self.db.select(sql)
        return l

    def logistics_list(self):
        sql="select id,name from wechat_mall_logistics where usr_id =%s"%self.usr_id
        l,t=self.db.select(sql)
        return l
    def property_list(self):
        sql = "select id,name from wechat_mall_goods_property where usr_id =%s and COALESCE(del_flag,0)!=1 order by paixu" % self.usr_id
        l, t = self.db.select(sql)
        L=[]
        if t>0:
            L.append(['','请选择规格'])
            for i in l:
                L.append(i)
        return L

    def get_property(self,pid):
        L = []
        if pid!='':
            L_ids = pid.split(',')

            for i in L_ids:
                sql="select id, name from wechat_mall_goods_property where id = %s "%i
                l, t = self.db.select(sql)
                if t > 0:
                    for j in l:
                        L.append(j)
        return L

    def get_ids(self,ids):

        L=[]
        if ids!='':
            sql=" select property_id,id, cname from wechat_mall_goods_property_child where property_id =%s"%(ids)
            l,t=self.db.select(sql)
            if t>0:
                for j in l:
                    L.append(j)
        return L

    def get_gg(self,pk):

        L=[]
        if pk!='':
            sql="select ggname,property_child_ids,originalpriceext,minpriceext,ptpriceext,scoreext,storesext,hypriceext from wechat_mall_goods_property_child_price where goods_id = %s"%pk
            l,t=self.db.select(sql)
            if t>0:
                L=l
        return L

    def get_property_no(self,pid):

        sql = "select id,name from wechat_mall_goods_property where usr_id =%s and id!=%s and COALESCE(del_flag,0)!=1 order by paixu" %(self.usr_id,pid)
        l, t = self.db.select(sql)
        L = []
        if t > 0:
            L.append(['', '请选择规格'])
            for i in l:
                L.append(i)
        return L

