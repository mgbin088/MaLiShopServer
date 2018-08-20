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

class cD002_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['团号ID','拼团ID','商品ID','手机号码','昵称',
                    '参与人数','状态','开团时间','更新时间','到期时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'D002'
        pass

    def mRight(self):
            
        sql = """
            select o.id
                ,p.goodsid
                 ,o.now_num
                 ,''
                ,p.numberpersion
                ,p.timeouthours
                ,case when p.status=0 then '正常' else '禁用' end 
                ,p.datestart
                ,p.dateend
            from open_pt o
            left join pt_set p on p.id=o.pt_id  
            where COALESCE(o.del_flag,0)!=1 and o.usr_id=%s
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
            select id
                ,title
                ,type
                ,isshow
                ,content  
            from notice 
            where  id=%s
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
        goodsid=self.GP('goodsid')#商品id
        numbersucccess=self.GP('numbersucccess')#已成团数
        numberpersion=self.GP('numberpersion')#几人成团
        timeouthours=self.GP('timeouthours')#超时小时
        status = self.GP('status')  # 状态
        datestart = self.GP('datestart')  # 开始时间
        dateend = self.GP('dateend')  # 结束时间




        
        if not (save_flag == save_flag2):
            #为FALSE时,当前请求为重刷新
            return dR
        
        # if danhao == '':
        #     dR['R'] = '1'
        #     dR['MSG'] = '请输入角色名字'
        
        data = {
                'goodsid':int(goodsid)
                ,'numbersucccess':int(numbersucccess)
                ,'numberpersion':int(numberpersion)
                ,'timeouthours':int(timeouthours)
                ,'status': int(status)
                , 'datestart': datestart
                , 'dateend': dateend
                ,'cid': self.usr_id
                ,'ctime': self.getToday(9)
                ,'uid': self.usr_id
                ,'utime': self.getToday(9)
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

            self.db.update('pt_set' , data , " id = %s " % pk)

        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')

            self.db.insert('pt_set' , data)
            pk = self.db.insertid('pt_set_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        dR['pk'] = pk
        
        return dR
