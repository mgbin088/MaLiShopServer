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

class cH002_dl(cBASE_DL):
    def init_data(self):
        self.GNL = ['角色ID','角色名','排序号','备注','创建人',
                    '创建时间','最后修改人','最后修改时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'H002'
        pass

    def mRight(self):
            
        sql = u"""
        select r.role_id                                   -- 0 角色id 
              ,r.role_name                                 -- 1 角色名
              ,COALESCE(r.sort,0) sort                       -- 2 排序
             
              ,COALESCE(r.memo,null) memo                      -- 4 备注 
              ,COALESCE(u1.usr_name,null) cUser                -- 5 创建人
              ,case when r.ctime is null then              
                         ''
                    else to_char(r.ctime,'YYYY-MM-DD')
               end  as ctime                               -- 6 创建时间
              ,COALESCE(u2.usr_name,null) uUser                -- 7 最后修改人
              ,case when r.utime is null then              
                         ''
                    else to_char(r.utime,'YYYY-MM-DD')
               end  as utime                               -- 8 最后修改时间
        from roles r 
      
        left join users u1 on r.cid = u1.usr_id
        left join users u2 on r.uid = u2.usr_id
        where 1 = 1
          
        """
        self.qqid = self.GP('qqid','')
        self.orderby = self.GP('orderby','')
        self.orderbydir = self.GP('orderbydir','')
        self.pageNo=self.GP('pageNo','')
        if self.pageNo=='':self.pageNo='1'
        self.pageNo=int(self.pageNo)
        if self.qqid!='' and len(self.QNL) > 0:
            sql+= self.QNL + " LIKE '%%%s%%' "%(self.qqid)
        #ORDER BY 
        if self.orderby!='':
            sql+=' ORDER BY %s %s' % (self.orderby,self.orderbydir)
        else:
            sql+=" ORDER BY r.role_id DESC"

        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
        select COALESCE (role_name,'') as role_name
              ,COALESCE (sort,null)      as sort
              ,COALESCE (dept_id,null)   as dept_id
              ,COALESCE (memo,'')      as memo
          from roles
         where role_id = '%s'
        """ % pk
        if pk != '':
            L = self.db.fetch( sql )
        return L

    def getMenuRoleList(self,roleId=0):
        
        """获取权限列表，默认显示全部菜单的权限情况，如果有 roleid 就显示对应这个roleId的情况
        """
        
        L = []
        
        sql = """
        select * from  p_getMenuRightList(%s);
        """ % roleId
        lT,iN = self.db.fetchall(sql)
        L = []
        for e in lT:
            if e not in L:
                L.append(e)
        return L

    def local_add_save(self):
        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        """
        #这些是操作权限
        seeList = self.REQUEST.getlist('see')
        addList = self.REQUEST.getlist('add')
        delList = self.REQUEST.getlist('del')
        updList = self.REQUEST.getlist('upd')
        
        seeStr = ''
        addStr = ''
        delStr = ''
        updStr = ''


        if seeList not in ['',None,0] and type(seeList)==list:
            seeStr = ','.join(seeList)
        else:
            seeStr = seeList
        
        if addList not in ['',None,0] and type(addList)==list:
            addStr = ','.join(addList)
        else:
            addStr = addList
            
        if delList not in ['',None,0] and type(delList)==list:
            delStr = ','.join(delList)
        else:
            delStr = delList
            
        if updList not in ['',None,0] and type(updList)==list:
            updStr = ','.join(updList)
        else:
            updStr = updList
        
        pk = self.pk
        dR={'R':'','MSG':''}


        from random import Random
        import time
        
        ranCode = str(Random(time.time()).random())[2:]
        
        #获取表单参数
        roleName = self.REQUEST.get('roleName','')  #角色名
        sort     = self.REQUEST.get('sort','')      #排序号
        dept_id  = self.REQUEST.get('dept_id','')  #部门id
        memo     = self.REQUEST.get('memo','')      #备注
        
        

        
        if roleName == '':
            dR['R'] = '1'
            dR['MSG'] = '请输入角色名字'
        
        data = {
                'role_name' : roleName , 
                'sort'      : sort , 
               # 'dept_id'   : dept_id ,
               # 'memo'      : memo ,
                'cid'       : self.usr_id,
                'ctime'     : self.getToday(6),
                'uid'       : self.usr_id,
                'utime'     : self.getToday(6),
                'random'    : ranCode
        }

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            
            data.pop('cid')
            data.pop('ctime')
            data.pop('random')

            self.db.update('roles' , data , " role_id = %s " % pk)
            
        else:  #insert 
            
            #如果是插入 就去掉 uid，utime 的处理
            
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('roles' , data)
            
        #保存权限列表修改情况
        if pk not in ['',None,'Null']:
            roleId = pk
        else:
            sql = """ select role_id from roles where random='%s' """%ranCode

            lT,iN=self.db.select(sql)

            if iN > 0:
                roleId = lT[0][0]
            else:
                roleId = 0

        rs = self.saveRoleMenuList(roleId,seeStr,addStr,delStr,updStr)
        
        if rs == 'error':
            dR['R'] = '1'
            dR['MSG'] = '角色权限列表保存失败'
        
        return dR

    def saveRoleMenuList(self,roleId,seeStr,addStr,delStr,updStr):
        
        """保存权限列表
        """
        if seeStr == '':
            seeStr = '0'
        if addStr == '':
            addStr = '0'
        if delStr == '':
            delStr = '0'
        if updStr == '':
            updStr = '0'
        result = 'error' #返回标志
        
        if roleId not in [0,'','Null',None] :
            #sql="select * from p_save_roleMenu(%s, '%s','%s','%s','%s',%s)"%(roleId,seeStr,addStr,delStr,updStr,self.usr_id)
            sql = "select * from  p_save_roleMenu(%s, '%s','%s','%s','%s',%s)" % (roleId, seeStr, addStr, delStr, updStr, self.usr_id)
            self.db.query(sql)
            #self.db.saverolemenu(sql)
            #self.db.select(sql)
            
            result = 'ok' #执行没问题就算成功了
        
        return result
        
    def delete_data(self):
        
        """删除数据
        """
        
        pk = self.pk
        u = self.db.fetch("select 1 from roles where role_id= %s" % pk)
        dR={'R':'','MSG':''}
        if not u:
            dR={'R':'1','MSG':'数据不存在'}
        else:
            self.db.query("delete from roles where role_id= %s" % pk)
            self.db.query("delete from role_menu where role_id = %s "%pk)
            self.db.query("delete from usr_role where role_id = %s "%pk)
        return dR


