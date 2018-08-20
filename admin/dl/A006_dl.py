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

class cA006_dl(cBASE_DL):
    def init_data(self):
        

        self.GNL = ['','优惠券id','口令','名称','数量','优惠金额',
                    '消费满可用','每人限领','状态','开始日期','类型','结束日期']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'A006'
        pass

    def mRight(self):
            
        sql = u"""
            select  id,
                type ,
                pwd,
                name,
                numbertotle,
                money,
                use_money,
                numberpersonmax,
                status,
                datestart,
                dateend
                
                
                from coupon 
                where COALESCE(del_flag,0)!=1 and usr_id=%s
        """%self.usr_id
        self.qqid = self.GP('qqid','')
        self.status = self.GP('status','')
        # self.orderbydir = self.GP('orderbydir','')
        self.pageNo=self.GP('pageNo','')
        if self.pageNo=='':
            self.pageNo='1'
        self.pageNo=int(self.pageNo)
        # if self.qqid!='' and len(self.QNL) > 0:
        #     sql+= self.QNL + " LIKE '%%%s%%' "%(self.qqid)
        if self.qqid!='':
            sql+= "and name LIKE '%%%s%%' "%(self.qqid)
        if self.status!='':
            sql+= "and status=%s "%(self.status)
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
            select  
                type ,
                pwd,
                needscore,
                refid ,
                name,
                numbertotle,
                money,
                use_money,
                numberpersonmax,
                datestart,
                dateend,
                status,
                cid,
                ctime,
                uid,
                utime
                from coupon 
                where id=%s 
        """ % pk
        if pk != '':
            L = self.db.fetch( sql )
        return L


    
    def local_add_save(self):
        

        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        """
        
        #这些是操作权限
        #dR={'R':'','MSG':'申请单 保存成功','B':'1','isadd':'','furl':''}
        pk = self.pk
        #dR={'R':'','MSG':'','isadd':''}
        dR={'R':'','MSG':''}
        save_flag = self.REQUEST.get("save_flag").strip()
        save_flag2 = self.cookie.getcookie("__flag")

        #获取表单参数

        type = self.REQUEST.get('type','')  #优惠券类型
        pwd = self.REQUEST.get('pwd','')  #口令
        needscore = self.REQUEST.get('needscore','')  #需要积分
        refid   = self.REQUEST.get('refid','')    #优惠对象编号
        name  = self.REQUEST.get('name','')  #优惠券名称
        numbertotle = self.REQUEST.get('numbertotle', '')  # 优惠券数量
        money = self.REQUEST.get('money', '')  # 优惠券金额
        use_money = self.REQUEST.get('use_money', '')  # 消费满多少可用
        numberpersonmax = self.REQUEST.get('numberpersonmax', '')  # 每人限领多少张
        datestart = self.REQUEST.get('datestart', '')  # 生效时间
        dateend = self.REQUEST.get('dateend', '')  # 截止时间
        status = self.REQUEST.get('status')  # 状态





        
        # if not (save_flag == save_flag2):
        #     #为FALSE时,当前请求为重刷新
        #     return dR
        #
        # if danhao == '':
        #     dR['R'] = '1'
        #     dR['MSG'] = '请输入角色名字'
        
        data = {
                'type': type ,
                'pwd': pwd,#youxiao_date ,
                'needscore': needscore ,
                'refid':refid ,
                'name':name,
                'numbertotle': numbertotle,
                'money':money,
                'use_money': use_money,
                'numberpersonmax': numberpersonmax,
                'datestart':datestart,
                'dateend':dateend,
                'status':status,
                'cid': self.usr_id,
                'ctime': self.getToday(6),
                'uid': self.usr_id,
                'utime': self.getToday(6),
                'usr_id':self.usr_id

        }
        for k in list(data):
            if data[k] == '':
                data.pop(k)
        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('coupon' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('coupon' , data)
            pk = self.db.insertid('coupon_id')#这个的格式是表名_自增字段
           # dR['isadd'] = 1

        dR['pk'] = pk
        
        return dR



    def sxlx_list(self):
        sql = "select id,txt1 from mtc_t where type='SXLX' order by sort"
        l, t = self.db.select(sql)
        return l

    def jzlx_list(self):
        sql = "select id,txt1 from mtc_t where type='JZLX' order by sort"
        l, t = self.db.select(sql)
        return l

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update coupon set del_flag=1 where id= %s" % pk)
        return dR

