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

class cE001_dl(cBASE_DL):
    def init_data(self):

        self.GNL = ['','用户编号','注册来源','手机号码','昵称','省份','城市',
                    '头像','注册时间','注册IP','登录时间','登录IP','状态',
                    '是否会员','会员开始时间','会员到期时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'E001'
        pass

    def mRight(self):
            
        sql = u"""
            select id
                ,register_type
                ,phone
                ,name
                ,province
                ,city
                ,avatar_url
                ,create_date
                ,register_ip
                ,last_login
                ,ip
                ,status  
                ,case when COALESCE(hy_flag,0)=0 then '否' else '是' end   --会员状态0否1是
                ,hy_ctime --会员开始时间
                ,hy_etime     --会员到期时间
            from wechat_mall_user 
            where usr_id=%s and del_flag=0
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
            select c.id
                    
                    
                  
                  
            from menu_func c
            
            where  c.id=%s
           
        """ % pk
        if pk != '':
            L = self.db.fetch( sql )

        return L
    

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update wechat_mall_user set del_flag=1 where id= %s" % pk)
        return dR
