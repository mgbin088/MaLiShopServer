# -*- coding: utf-8 -*-
##############################################################################
#

#
##############################################################################

from imp import reload
from config import DEBUG,CLIENT_NAME
from basic import  public
user_menu=public.user_menu

if DEBUG=='1':
    import admin.vi.VI_BASE
    reload(admin.vi.VI_BASE)
from admin.vi.VI_BASE             import cVI_BASE

import time

from flask import make_response,redirect

class clogin(cVI_BASE):

    def setClassName(self):

        #设定要实例的 dl类和TPL类，为空则继承基类，可以能过判断part的值来设置不同的类名
        self.dl_name = ''
    def specialinit(self):
        self.viewid='login'
    def goPartList(self):
        
        error = self.REQUEST.get('error','')
        msg = ''
        if error=='1':
            msg="无此用户，请联系管理员！"
        elif error=='2':
            msg="密码输入错误，请重新输入！"
        elif error=='ip':
            msg="IP非法, 登录用户已采用绑定IP登录, 您可以从登录页重新登录."
        elif error=='only':
            msg="此帐号已被独占使用, 请联系登录者注销后, 您才可以再次登录!"
        elif error == '3':
            msg = "此帐号已被停用, 请联系管理员!"
        self.assign('msg',msg)
        #return '1'
        s = self.runApp('login.html')
        return s
    
    def goPartDologin(self):

        login_id = self.dl.GP('inputname','')
        password = self.dl.GP('inputPassword','')

        lT = self.dl.login(login_id , password)

        cookid='%s_pw'%(login_id)
        cookname='loginmode_%s' % CLIENT_NAME
        

        if lT:
            usr_id=lT[0][0]
            usr_name=lT[0][1]

            result = self.dl.cookie.isetcookie("__session" , usr_id)
            
            self.dl.checkuser(usr_id)

            menu1,menu2,menu3 = self.dl.getSysMenu(usr_id)
            if usr_id in user_menu:
                user_menu[usr_id] = {
                    'menu1':menu1,'menu2':menu2,'menu3':menu3
                }
            else:
                user_menu.update( {usr_id:{
                    'menu1':menu1,'menu2':menu2,'menu3':menu3
                }} )
            
            

            sql="UPDATE users SET  cookid=newid(),last_login='%s',last_ip='%s',use_count=use_count+1 WHERE usr_id=%s" %(self.dl.getToday(7),self.objHandle.remote_addr,usr_id)
            self.dl.db.query(sql)
            sql="select cookid from users where usr_id=%s"%usr_id
            lT,iN=self.dl.db.select(sql)
            cookid=lT[0][0] 

            sub1id=1301
            sUrl='admin/home'

            response = make_response(redirect(sUrl))


            self.save_login_cookies(response,cookid,cookname)
            self.save_login_cookies(response , '%s_%s'%(usr_id,cookid),'administrator_yjyzj')

        else:
            sql=" select usr_id from users where login_id = '%s'  limit 1 "%login_id

            lT,iN=self.dl.db.select(sql)
            if iN == 0:
                error='1'
            else:
                sql=" select usr_id from users where login_id = '%s' and  password= crypt('%s', password)  limit 1 "%(login_id,password)
                l,t=self.dl.db.select(sql)
                if t>0:
                    error = '3'
                else:
                    error='2'
            sUrl='admin/login/?error=%s'%error
            response = make_response(redirect(sUrl))

        return response

    def save_login_cookies(self,response,cookid,cookname='administrator_yjyzj'):
        #response.cookies[cookname]=cookid
        response.set_cookie(cookname, value=cookid)


    def goPartLogout(self):
        response = make_response(redirect("admin?viewid=login"))
        self.dl.cookie.clearcookie(response)
        return response

    def goPartGologin(self):

        login_id = self.dl.GP('inputname', '')
        password = self.dl.GP('inputPassword', '')

        lT = self.dl.login(login_id, password)

        cookid = '%s_pw' % (login_id)
        cookname = 'loginmode_%s' % CLIENT_NAME

        if lT:
            usr_id = lT[0][0]
            usr_name = lT[0][1]

            result = self.dl.cookie.isetcookie("__session", usr_id)

            self.dl.checkuser(usr_id)

            menu1, menu2, menu3 = self.dl.getSysMenu(usr_id)
            if usr_id in user_menu:
                user_menu[usr_id] = {
                    'menu1': menu1, 'menu2': menu2, 'menu3': menu3
                }
            else:
                user_menu.update({usr_id: {
                    'menu1': menu1, 'menu2': menu2, 'menu3': menu3
                }})

            sql = "UPDATE users SET  cookid=newid(),last_login='%s',last_ip='%s',use_count=use_count+1 WHERE usr_id=%s" % (
            self.dl.getToday(7), self.objHandle.remote_addr, usr_id)
            self.dl.db.query(sql)
            sql = "select cookid from users where usr_id=%s" % usr_id
            lT, iN = self.dl.db.select(sql)
            cookid = lT[0][0]

            sub1id = 1301
            sUrl = 'houtai?viewid=home'

            response = make_response(redirect(sUrl))
            #response.headers['Access-Control-Allow-Origin'] = '*'
            self.save_login_cookies(response, cookid, cookname)
            self.save_login_cookies(response, '%s_%s' % (usr_id, cookid), 'administrator_yjyzj')
            code=0
            import jwt
            import time
            import random
            payloads = {
                "iss": "janedao.com",
                "iat": int(time.time()),
                "exp": int(time.time()) + 60 * 30,#60*60*24  一天
                "aud": "www.janedao.com",
                 "usr_id": usr_id,
                "usr_name":usr_name,
                "scopes": random.random()
            }
            encoded_jwt = jwt.encode(payloads, 'secret', algorithm='HS256')
            token = encoded_jwt.decode('utf-8')


        else:

            code,token = 1,'000'

        return self.jsons({'code':code,'malitoken':token})

    def goPartcheck(self):
        toekn = self.objHandle.headers.get('malitoken', '')

        code = 0
        import jwt
        import time
        import random
        payloads = {
            "iss": "janedao.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400 * 7,
            "aud": "www.janedao.com",
            "usr_id": 1,
            "usr_name": '超级管理员',
            "scopes": random.random()
        }
        if toekn=='' or toekn==None:
            code = 1
            return self.jsons({'code': code, 'msg': 'malitoken无效','token':1})
        payload = jwt.decode(toekn, 'secret', audience='www.janedao.com', algorithms=['HS256'])
        if not payload:
            code=1
            return self.jsons({'code': code, 'msg': 'malitoken无效','token':2})
        if payload['iss']!="janedao.com":
            code = 1
            return self.jsons({'code': code, 'msg': 'malitoken无效','token':3})
        if payload['exp']<int(time.time()):
            code = 1
            return self.jsons({'code': code, 'msg': 'malitoken无效','token':4})
        if payload['aud']!="www.janedao.com":
            code = 1
            return self.jsons({'code': code, 'msg': 'malitoken无效','token':5})
        try:
            usr_id=payload['usr_id']
            usr_name=payload['usr_name']
        except:
            code = 1
            return self.jsons({'code': code, 'msg': 'malitoken无效'})
        sql="select usr_id from users where usr_id=%s and usr_name='%s'"%(usr_id,usr_name)
        l,t=self.dl.db.select(sql)
        if t==0:
            code = 1
            return self.jsons({'code': code, 'msg': 'malitoken无效'})
        return self.jsons({'code': code, 'msg': 'ok'})