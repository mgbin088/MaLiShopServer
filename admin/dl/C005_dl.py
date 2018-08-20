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

class cC005_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['','分类名称','分类级别','上级分类','编号',
                    '类型','图标','是否启用','添加时间','修改时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'C005'
        pass

    def mRight(self):
        pass
        sql = u"""
             select g.id
                ,g.name
                ,g.level
                --,g.pid
                ,gc.name
                ,g.key
                ,g.type
                ,g.icon
                ,case when g.isuse=0 then '是' else '否'end
                ,to_char(g.ctime,'YYYY-MM-DD HH:MM')
                ,to_char(g.utime,'YYYY-MM-DD HH:MM')
            from goods_category g
            left join goods_category gc on gc.id=g.pid
            where COALESCE(g.del_flag,0)=0 and g.usr_id=%s
            
        """%self.usr_id
        self.qqid = self.GP('qqid','')
        if self.qqid!='':
            sql+= "and g.name LIKE '%%%s%%' "%(self.qqid)
        self.pid = self.GP('pid',0)
        if int(self.pid)!=0:
            sql +="and (g.pid=%s or g.id=%s) "%(self.pid,self.pid)
        # self.orderbydir = self.GP('orderbydir','')
        # self.pageNo=self.GP('pageNo','')
        # if self.pageNo=='':self.pageNo='1'
        # self.pageNo=int(self.pageNo)
        # #ORDER BY
        # if self.orderby!='':
        #     sql+=' ORDER BY %s %s' % (self.orderby,self.orderbydir)
        # else:
        sql+="order by g.level,g.id "

        #l,t=self.db.select(sql)
        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL = [pageNo, iTotal_Page, iTotal_length, select_size]

        # menu1 = []
        #
        # for row in l:
        #     if row[2] == 1:
        #         menu1.append([row[0], row[1],row[2],row[4],row[5],row[6],row[7],row[8],row[9],row[10]])#,row['func_id']
        #         for r in l:
        #             if r[2] == 2 and r[3]==row[0]:
        #                 menu1.append([r[0], '╚═══'+r[1],r[2],r[4],r[5],r[6],r[7],r[8],r[9],r[10]])  # ,row['func_id']
        #                 for w in l:
        #                     if w[2] == 3 and w[3] == r[0]:
        #                         menu1.append([w[0],  '╚═══╚═══'+w[1],w[2],w[4],w[5],w[6],w[7],w[8],w[9],w[10]])  # ,row['func_id']
        #
        # L, iTotal_length, iTotal_Page, pageNo, select_size = self.db.list_for_grid(menu1,t,self.pageNo)
        # PL = [pageNo, iTotal_Page, iTotal_length, select_size]

        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
            select id,name,key,type,pid,icon,isuse,ctime,paixu from goods_category where id=%s
           
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
        name=self.GP('name','')#名称
        type=self.GP('type','')#类型
        pid=self.GP('pid','') #上级分类
        key=self.GP('key','')#编号
        icon=self.GP('icon','')#图标
        isuse=self.GP('isuse','')#是否启用
        paixu=self.GP('paixu',0)#排序


        # from werkzeug import secure_filename
        # try:
        #     file = self.objHandle.files['icon']
        #     if file:
        #         #filename = secure_filename(file.filename)
        #         ext = secure_filename(file.filename).split('.')[-1]
        #         timeStamp = time.time()
        #         md5name = hashlib.md5()
        #         md5name.update(str(timeStamp).encode('utf-8'))
        #         filename = md5name.hexdigest() + '.' + ext
        #         icon = filename
        #         file.save(os.path.join(public.ATTACH_ROOT, filename))
        # except:
        #     icon = self.GP('icon')  # 图标


        level=1
        if int(pid)!=0:
            sql="select level from goods_category where id=%s"%pid
            l,t=self.db.select(sql)
            if t>0:
                level=int(l[0][0])+1

        # if not (save_flag == save_flag2):
        #     #为FALSE时,当前请求为重刷新
        #     return dR
        
        # if danhao == '':
        #     dR['R'] = '1'
        #     dR['MSG'] = '请输入角色名字'
        
        data = {
                'name':name
                ,'type':type
                ,'pid':pid
                ,'key':key

                ,'isuse':isuse
                ,'paixu':int(paixu)
                ,'cid': self.usr_id
                ,'ctime': self.getToday(9)
                ,'uid': self.usr_id
                ,'utime': self.getToday(9)
                ,'usr_id':self.usr_id
                ,'level':int(level)
        }

        for k in list(data):
            if data[k] == '':
                data.pop(k)

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data['icon']=icon
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('goods_category' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data['icon'] = icon
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('goods_category' , data)
            #pk = self.db.insertid('goods_category_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        #dR['pk'] = pk
        
        return dR

    def getfllist(self):
        L=[[0,'顶级分类']]
        sql="select id,name from goods_category where usr_id=%s and COALESCE(del_flag,0)!=1 order by level,id "%self.usr_id
        l,t=self.db.select(sql)
        if t>0:
            for r in l:
                L.append(r)
        return L

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update goods_category set del_flag=1 where id= %s" % pk)
        return dR

    def setfllist(self):
        L=[[0,'请选择分类']]
        sql="select id,name from goods_category where usr_id=%s and COALESCE(del_flag,0)!=1 and level=1"%self.usr_id
        l,t=self.db.select(sql)
        if t>0:
            for r in l:
                L.append(r)
        return L