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

class cH001_dl(cBASE_DL):
    #在子类中重新定义         
    def myInit(self):
        self.src = 'H001'
        pass

    def getInfo(self):
        uid = self.usr_id
        info  =  self.db.fetch("""
        select login_id , usr_name , usr_id , mobile from users where usr_id = %s
        """ % uid)
        return info

    def local_add_save(self):
        dR={'R':'','MSG':'申请单 保存成功','B':'1','isadd':'','furl':''}  
        usr_name = self.GP('usr_name')
        mobile = self.GP('mobile')
        oldpassword = self.GP('oldpassword')
        password = self.GP('password')
        password2 = self.GP('password2')


        # data = {
        #     'usr_name' : self.urldecode(usr_name) , 'mobile':mobile
        # }
        if password != '' :
            if password2 != password:
                dR['R'] = '1'
                dR['MSG'] = '确认密码必须和新密码相同'
                return dR

            l,t=self.db.select("select usr_id from users where usr_id = '%s' and password = crypt('%s', password);"%(self.usr_id,oldpassword))
            if t<1:
                dR['R'] = '1'
                dR['MSG'] = '您的旧密码输入错误'
                return dR

            sql = "update users set usr_name='%s',mobile='%s',password= crypt('%s', gen_salt('md5')) where usr_id=%s" % (
            usr_name, mobile, password, self.usr_id)
            self.db.query(sql)
            return dR
        else:
            #self.db.update('users',data,' usr_id = %s'  % self.usr_id)
            dR['R'] = '1'
            dR['MSG'] = '密码不能为空'
            return dR

