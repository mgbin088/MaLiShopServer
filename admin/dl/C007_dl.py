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

class cC007_dl(cBASE_DL):
    def init_data(self):

        self.GNL = ['','标题','类型','是否展示','发布时间','内容']



    #在子类中重新定义         
    def myInit(self):
        self.src = 'C007'
        pass

    def mRight(self):
            
        sql = u"""
            select id
                ,title
                ,type
                ,case when isshow=0 then '是' else '否' end 
                ,ctime
                ,content
            from notice 
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
        title=self.GP('title')#标题
        type=self.GP('type')#类型
        isshow=self.GP('isshow')#是否展示
        #container=self.GP('container')#内容
        container = self.GP('text_contents', '')  # 详情介绍



        
        if not (save_flag == save_flag2):
            #为FALSE时,当前请求为重刷新
            return dR
        
        # if danhao == '':
        #     dR['R'] = '1'
        #     dR['MSG'] = '请输入角色名字'
        
        data = {
                'title':title
                ,'type':type
                ,'isshow':int(isshow)
                ,'content':container
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

            self.db.update('notice' , data , " id = %s " % pk)

        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')

            self.db.insert('notice' , data)
            pk = self.db.insertid('notice_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        dR['pk'] = pk
        
        return dR


    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update notice set del_flag=1 where id= %s" % pk)
        return dR
