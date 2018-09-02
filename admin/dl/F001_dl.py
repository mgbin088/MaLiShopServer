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

class cF001_dl(cBASE_DL):
    def init_data(self):

        self.GNL = ['','分类名称','分类级别','上级分类','编号','类型','图标',
                    '是否启用','添加时间','修改时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'F001'
        pass

    def mRight(self):
            
        sql = u"""
            select g.id
                ,g.name
                ,g.level
                ,gc.name
                ,g.key
                ,g.type
                ,g.icon
                ,case when g.isuse=0 then '是' else '否'end
                ,g.ctime
                ,g.utime 
                --,g.memo
            from cms_fl g
            left join cms_fl gc on gc.id=g.pid
            where COALESCE(g.del_flag,0)!=1 and g.usr_id=%s
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
            select id,name,key,type,pid,icon,isuse,ctime,memo from cms_fl where id=%s
           
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

        
        #获取表单参数
        name=self.GP('name')#名称
        type=self.GP('type')#类型
        pid=self.GP('pid') #上级分类
        key=self.GP('key')#编号
        memo=self.GP('memo')#图标
        isuse=self.GP('isuse')#是否启用
        paixu=self.GP('paixu') or 0#排序


        from werkzeug import secure_filename
        try:
            file = self.objHandle.files['icon']
            if file:
                ext = secure_filename(file.filename).split('.')[-1]
                timeStamp = time.time()
                md5name = hashlib.md5()
                md5name.update(str(timeStamp).encode('utf-8'))
                filename = md5name.hexdigest() + '.' + ext
                icon = filename
                file.save(os.path.join(public.ATTACH_ROOT, filename))
        except:
            icon = self.GP('icon')  # 图标


        level=1
        if int(pid)!=0:
            sql="select level from cms_fl where id=%s"%pid
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
                ,'icon':icon
                ,'isuse':isuse
                ,'paixu':int(paixu)
                ,'cid': self.usr_id
                ,'ctime': self.getToday(9)
                ,'uid': self.usr_id
                ,'utime': self.getToday(9)
                ,'usr_id':self.usr_id
                ,'level':int(level)
                ,'memo':memo
        }
        # for k in list(data):
        #     if data[k] == '':
        #         data.pop(k)


        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('cms_fl' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('cms_fl' , data)
            pk = self.db.insertid('cms_fl_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        dR['pk'] = pk
        
        return dR

    def getfllist(self):
        L=[[0,'顶级分类']]
        sql="select id,name from cms_fl where COALESCE(del_flag,0)!=1"
        l,t=self.db.select(sql)
        if t>0:
            for r in l:
                L.append(r)
        return L

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update cms_fl set del_flag=1 where id= %s" % pk)
        return dR
