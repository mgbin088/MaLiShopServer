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

class cC003_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['','名称','排序','添加时间','更新时间','备注']

    #在子类中重新定义         
    def myInit(self):
        self.src = 'C003'
        pass

    def mRight(self):
            
        sql = u"""
            select id,name,paixu,ctime,utime 
            from wechat_mall_goods_property 
            where COALESCE(del_flag,0)!=1 and usr_id=%s
        """%self.usr_id
        # self.qqid = self.GP('qqid','')
        # self.orderby = self.GP('orderby','')
        # self.orderbydir = self.GP('orderbydir','')
        # self.pageNo=self.GP('pageNo','')
        # if self.pageNo=='':self.pageNo='1'
        # self.pageNo=int(self.pageNo)
        # if self.qqid!='' and len(self.QNL) > 0:
        #     sql+= self.QNL + " LIKE '%%%s%%' "%(self.qqid)
        # #ORDER BY
        # if self.orderby!='':
        #     sql+=' ORDER BY %s %s' % (self.orderby,self.orderbydir)
        # else:
        sql+=" ORDER BY id DESC"
        
        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
            select c.name,c.paixu   
            from wechat_mall_goods_property c
            
            where  c.id=%s
           
        """ % pk
        if pk != '':
            L = self.db.fetch( sql )
        # else:
        #     timeStamp = time.time()
        #     timeArray = time.localtime(timeStamp)
        #     danhao = time.strftime("%Y%m%d%H%M%S", timeArray)
        #
        #     #L['danhao']='cgdd'+danhao
        #     L['danhao'] = ''
        return L

    def get_sec_data(self,pk):
        L = []
        sql = """
                select c.cname,c.remark,c.cpaixu  
                from wechat_mall_goods_property_child c
                where  c.property_id=%s
                """ % pk
        if pk != '':
            l,t= self.db.select(sql)
            if t>0:
                L=l

        return L
    def local_add_save(self):
        

        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        """
        
        #这些是操作权限
        dR={'R':'','MSG':'申请单 保存成功','B':'1','isadd':'','furl':''}  
        pk = self.pk
        #dR={'R':'','MSG':'','isadd':''}
        dR={'R':'','MSG':''}

        
        
        #获取表单参数
        name=self.GP('name')#名称
        paixu=self.GP('paixu')#排序

        if paixu=='':
            paixu=0

        
        data = {
                'name':name
                ,'paixu':int(paixu)
                ,'usr_id':self.usr_id
                ,'cid': self.usr_id
                ,'ctime': self.getToday(6)
                ,'uid': self.usr_id
                ,'utime': self.getToday(6)
        }
        # for k in list(data):
        #     if data[k] == '':
        #         data.pop(k)

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('wechat_mall_goods_property' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('wechat_mall_goods_property' , data)
            pk = self.db.insertid('wechat_mall_goods_property_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        self.sec_save(pk)
        dR['pk'] = pk
        
        return dR

    def sec_save(self,pk):

        # 获取表单参数
        cname = self.REQUEST.getlist('cname')  # 名称
        cpaixu = self.REQUEST.getlist('cpaixu')  # 排序
        remark = self.REQUEST.getlist('remark')#备注

        sqldel = "delete from wechat_mall_goods_property_child where property_id=%s " % pk
        self.db.query(sqldel)
        sql = ''
        for i in range(len(cname)):
            if cname[i] != '':
                if cpaixu[i]=='':
                    cpaixu[i]=0
                if sql == '':
                    sql = """ insert into wechat_mall_goods_property_child(property_id ,cname,cpaixu,remark,cid,ctime)
                                        values (%s,'%s',%s,'%s',%s,now())
                                    """ % (pk, cname[i],cpaixu[i], remark[i],self.usr_id)
                else:
                    sql += ",(%s,'%s',%s,'%s',%s,now())" % (pk, cname[i], int(cpaixu[i]), remark[i],self.usr_id)
        if sql != '':
            self.db.query(sql)

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update wechat_mall_goods_property set del_flag=1 where id= %s" % pk)
        return dR

