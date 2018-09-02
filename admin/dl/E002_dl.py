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

class cE002_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['','编号','手机号码','昵称','是否默认','所在地',
                    '联系人','邮编','状态','添加时间','更新时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'E002'
        pass

    def mRight(self):
            
        sql = u"""
            select w.id
                ,w.phone
                ,wu.name
                ,w.is_default
                ,w.provinceid 
               -- ,w.cityid 
               -- ,w.districtid 
                ,w.linkman 
                ,w.postcode 
                ,w.status
                ,w.ctime 
                ,w.utime
            from wechat_mall_address w
            left join wechat_mall_user  wu on wu.id=w.wechat_user_id
            where  COALESCE(w.del_flag,0)!=1 and w.usr_id =%s
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
        else:
            timeStamp = time.time()
            timeArray = time.localtime(timeStamp)
            danhao = time.strftime("%Y%m%d%H%M%S", timeArray)

            #L['danhao']='cgdd'+danhao
            L['danhao'] = ''
        return L
    

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}

        self.db.query("update wechat_mall_address set del_flag=1 where id= %s" % pk)
        return dR
