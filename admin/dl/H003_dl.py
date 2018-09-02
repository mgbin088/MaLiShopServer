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

class cH003_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['用户ID','用户名','登录帐号','角色授权','创建人',
                    '创建时间','最后修改人','最后修改时间','最后登录时间','最后登录IP']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'H003'
        pass

    def mRight(self):


        sql = """
            select u.usr_id  --0
                ,u.usr_name  --1
                ,u.login_id  --2
                ,''--select func_rolename(u.usr_id) --3
              
                ,u1.usr_name    --5+2
                ,to_char(u.ctime,'YYYY-MM-DD')  --6+2
                ,u2.usr_name    --7+2
                ,to_char(u.utime,'YYYY-MM-DD')  --8+2
                ,u.last_login --9+2
                ,u.last_ip --10+2
             from users u
            
             left join users u1 on u1.usr_id = u.cid
             left join users u2 on u2.usr_id = u.uid
           
             where 1 = 1 
        """
        
        # if self.unit_id != 1:
        #     sql+=" and u.h_id = %s "%self.unit_id
        #
        self.qqid = self.GP('qqid','')
        self.orderby = self.GP('orderby','')
        self.orderbydir = self.GP('orderbydir','')
        self.pageNo=self.GP('pageNo','')
        if self.pageNo=='':self.pageNo='1'
        self.pageNo=int(self.pageNo)


        #ORDER BY
        if self.orderby!='':
            sql+=' ORDER BY %s %s' % (self.orderby,self.orderbydir)
        else:
            sql+=" ORDER BY u.usr_id DESC"

        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {'dept_id':2}
        sql = """
            select u.login_id --登录名
                   ,u.usr_name --用户名
                  ,u.status
                   ,u.mobile --手机
                 
                
            from users u
          
            where u.usr_id = %s
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
        login_id = self.REQUEST.get('login_id','')  #登录名
        usr_name = self.REQUEST.get('usr_name','')  #用户名
        mobile   = self.REQUEST.get('mobile','')    #手机
        status  = self.REQUEST.get('status','')  #状态
        respw =self.REQUEST.get('respw','')#恢复密码


		#判断login_id重复
        if pk != '':  #update
            sql="SELECT count(login_id) FROM users WHERE login_id='%s'  AND usr_id !=%s"%(login_id,pk)
        else:  #insert 
            sql="SELECT count(login_id) FROM users WHERE login_id='%s'"%(login_id)
        lT,iN=self.db.select(sql)
        if lT[0][0]>0:
            dR={'R':'1','MSG':'登录名已存在，保存失败!'}
            return dR
        
        if login_id == '':
            dR['R'] = '1'
            dR['MSG'] = '请输入角色名字'
            return dR


        if pk != '':  #update

            #如果是更新，就去掉cid，ctime 的处理.
            if str(respw)=='1':
                sql="""
                    update users set password = crypt('Aa123456', gen_salt('md5')),uid=%s,utime=now() where usr_id = %s
                """%(self.usr_id,pk)
                self.db.query(sql)
            sql = """
                update users set mobile='%s',status=%s,uid=%s,utime=now() where usr_id = %s
            """ % (mobile,status,self.usr_id,pk)

            self.db.query(sql)

            dR['pk'] = pk

            
        else:  #insert 
            
            #如果是插入 就去掉 uid，utime 的处理
            sql="""insert into users(login_id, password, usr_name, status, usr_type, dept_id, del_flag, isadmin, is_dept_admin, sort,cid,ctime,mobile)
            values('%s', crypt('Aa123456', gen_salt('md5')), '%s', %s, 1, 2, 0, 0, 0, 0,%s,now(),'%s');
            """%(login_id,usr_name,status,self.usr_id,mobile)
            self.db.query(sql)

        return dR


    
        
    def delete_data(self):
        
        """删除数据
        """
        
        pk = self.pk
        u = self.db.fetch("select 1 from users where usr_id= %s" % pk)
        dR={'R':'','MSG':''}
        if not u:
            dR={'R':'1','MSG':'数据不存在'}
        else:
            self.db.query("delete from users where usr_id= %s" % pk)
            self.db.query("delete from user_book where uid= %s" % pk)
            self.db.query("delete from user_info where uid= %s" % pk)
            self.db.query("update users set usr_id2=0 ,login_id=''   where  usr_id2= %s" % pk)
        return dR
    def get_status(self):
        sql="select id,txt1 from mtc_t where type='YESNO'"
        l,t=self.db.select(sql)
        return l
