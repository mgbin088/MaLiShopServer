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

class cB002_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['','编号','类型','KEY','值','备注','添加时间','更新时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'B002'
        pass

    def mRight(self):
            
        sql = u"""
            select id,datetype,key,content,remark,ctime,utime from config_set  where COALESCE(del_flag,0)!=1 and usr_id= %s
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
        #     sql+=" ORDER BY r.role_id DESC"
        
        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
            select id,datetype,key,content,remark,ctime,utime from config_set  where id= %s
           
        """ % pk
        if pk != '':
            L = self.db.fetch( sql )

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
        datetype=self.GP('datetype')#类型
        key=self.GP('key')#编码
        content=self.GP('content')#参数值
        remark=self.GP('remark')#备注


        
        data = {
                'dateType':int(datetype)
                ,'key':key
                ,'content':content
                ,'remark':remark
                ,'usr_id':self.usr_id


        }
        # for k in list(data):
        #     if data[k] == '':
        #         data.pop(k)

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.

            data['uid']=self.usr_id
            data['utime']= self.getToday(9)

            self.db.update('config_set' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data['cid']= self.usr_id
            data['ctime']= self.getToday(9)
            
            self.db.insert('config_set' , data)
            pk = self.db.insertid('config_set_id')#这个的格式是表名_自增字段

        #self.listdata_save(pk,danhao)
        dR['pk'] = pk
        
        return dR

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update config_set set del_flag=1 where id= %s" % pk)
        return dR

