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

class cA004_dl(cBASE_DL):
    def init_data(self):

        self.GNL = ['','名称','是否包邮','计价方式','添加时间','更新时间']

    #在子类中重新定义         
    def myInit(self):
        self.src = 'A004'
        pass

    def mRight(self):
            
        sql = u"""
            select id
                ,name
                ,case when isfree=0 then '不包邮' else '包邮' end
                ,case when feetype='0' then '按件数' else '按重量' end
                ,ctime
                ,utime from wechat_mall_logistics 
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
                    ,c.name
                    ,c.isfree
                    ,c.feetype
                    ,w.kuaidi
                    ,w.kfirstnumber
                    ,w.kfirstamount
                    ,w.kaddnumber
                    ,w.kaddamount
                    ,w.efirstnumber
                    ,w.efirstamount
                    ,w.eaddnumber
                    ,w.eaddamount
                    ,w.ems
            from wechat_mall_logistics c
            left join wechat_mall_transportation w on w.logistics_id=c.id
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
    
    def local_add_save(self):
        

        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        """
        
        #这些是操作权限
        dR={'R':'','MSG':'申请单 保存成功','B':'1','isadd':'','furl':''}  
        pk = self.pk
        #dR={'R':'','MSG':'','isadd':''}
        dR={'R':'','MSG':''}
        save_flag = self.REQUEST.get("save_flag").strip()
        save_flag2 = self.cookie.getcookie("__flag")
        
        
        #获取表单参数
        name=self.GP('name')#名称
        isfree=self.GP('isfree')#是否包邮
        feetype=self.GP('feetype')#计价方式
        kuaidi=self.GP('kuaidi',0)#快递
        ems=self.GP('ems',0)#EMS

        kfirstnumber=self.GP('kfirstnumber')#数量内
        kfirstamount=self.GP('kfirstamount')#数量内价格
        kaddnumber = self.GP('kaddnumber')  #数量外
        kaddamount=self.GP('kaddamount')#数量外价格
        efirstnumber = self.GP('efirstnumber')  #数量内
        efirstamount = self.GP('efirstamount')  #数量内价格
        eaddnumber = self.GP('eaddnumber')  #数量外
        eaddamount = self.GP('eaddamount')  # 数量外价格


        # if not (save_flag == save_flag2):
        #     #为FALSE时,当前请求为重刷新
        #     return dR
        
        # if danhao == '':
        #     dR['R'] = '1'
        #     dR['MSG'] = '请输入角色名字'
        
        data = {
                'name':name
                ,'isfree':isfree
                ,'feetype':feetype
                ,'cid': self.usr_id
                ,'ctime': self.getToday(6)
                ,'uid': self.usr_id
                ,'utime': self.getToday(6)
                ,'usr_id':self.usr_id
        }

        for k in list(data):
            if data[k] == '':
                data.pop(k)

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('wechat_mall_logistics' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('wechat_mall_logistics' , data)
            pk = self.db.insertid('wechat_mall_logistics_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        dR['pk'] = pk

        sql = "select logistics_id from wechat_mall_transportation where logistics_id =%s" % pk
        l, t = self.db.select(sql)
        if t > 0:
            sql="""update wechat_mall_transportation set kuaidi=%s,kfirstnumber=%s,kfirstamount=%s,kaddnumber=%s,
             kaddamount=%s,efirstnumber=%s,efirstamount=%s,eaddnumber=%s,eaddamount=%s,ems=%s       where logistics_id =%s
            
            """%(kuaidi,kfirstnumber,kfirstamount,kaddnumber,kaddamount,efirstnumber,efirstamount,eaddnumber,eaddamount,ems,pk)
            self.db.query(sql)
        else:
            if int(kuaidi)==1 or int(ems)==1:
                sql = """insert into wechat_mall_transportation
                (logistics_id,kuaidi,kfirstnumber,kfirstamount,kaddnumber,kaddamount,efirstnumber,efirstamount,eaddnumber,eaddamount,ems)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """ % (pk,kuaidi, kfirstnumber, kfirstamount, kaddnumber, kaddamount, efirstnumber, efirstamount, eaddnumber,eaddamount, ems)
                self.db.query(sql)
        return dR

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update wechat_mall_logistics set del_flag=1 where id= %s" % pk)
        return dR

