# -*- coding: utf-8 -*-

##############################################################################
#
#
#
##############################################################################
"""
检查token，注册，登录，参数设置接口,Banner,商品分类,地址相关接口，收藏相关接口


"""

from imp import reload
from config import DEBUG,CLIENT_NAME
if DEBUG=='1':
    import api.VI_BASE
    reload(api.VI_BASE)
from api.VI_BASE             import cVI_BASE
from basic.wxbase import wx_minapp_login,WXBizDataCrypt
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import hashlib,time,json

class cBASE_TPL(cVI_BASE):

    def goPartbegin(self):
        a='你很调皮哦'
        return self.jsons({'code':000000000,'data':a})


    def goPartchecktoken(self): #检查token
        token = self.REQUEST.get('token','')
        if token=='' or token=='None':
            return self.jsons(({'code': 300, 'msg': self.error_code[300].format('token')}))


        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql=" select token from wechat_mall_access_token where token='%s' and usr_id=%s"%(token,self.subusr_id)
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})

        return self.jsons({'code': 0, 'msg': 'success'})

    def goPartregister(self): #注册
        #print('login,llllllllllllll')
        code = self.REQUEST.get('code','')
        encrypted_data = self.REQUEST.get('encryptedData','')
        rawData = self.REQUEST.get('rawData','')
        iv = self.REQUEST.get('iv','')
        signature = self.REQUEST.get('signature','')

        if not code or code=='' or code=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('code')})

        if not encrypted_data or encrypted_data =='' or encrypted_data =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('encryptedData')})

        if not iv or iv=='' or iv=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('iv')})

        if not rawData or rawData=='' or rawData=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('rawData')})

        if not signature or signature=='' or signature=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('signature')})

        sql = "select appid,secret  from mall where usr_id=%s" % self.subusr_id
        l, t = self.db.select(sql)

        if t == 0:
            return self.jsons({'code': 404, 'msg': '请到后台填写‘微信设置’'})
        app_id = l[0][0]
        secret = l[0][1]

        api=wx_minapp_login(app_id,secret)
        session_info = api.get_session_info(code=code)
        session_key = session_info.get('session_key')

        crypt = WXBizDataCrypt(app_id, session_key)
        # 解密得到 用户信息
        user_info = crypt.decrypt(encrypted_data, iv)
        try:
            register_ip=self.objHandle.headers["X-Real-IP"]
        except:
            register_ip = self.objHandle.remote_addr
        data={
            'name': user_info['nickName'],
            'open_id': user_info['openId'],
            'gender': user_info['gender'],
            'language': user_info['language'],
            'country': user_info['country'],
            'province': user_info['province'],
            'city': user_info['city'],
            'avatar_url': user_info['avatarUrl'],
            'register_ip': register_ip,
            'usr_id':self.subusr_id,
            'create_date':self.getToday(9),
            'del_flag':0
        }
        sqll = "select id  from wechat_mall_user where open_id='%s' and  usr_id=%s" % (user_info['openId'], self.subusr_id)
        #print(sqll,'6666666666')
        lT, iN = self.db.select(sqll)
        if iN == 0:
            self.db.insert('wechat_mall_user', data)
            sqll = "select id  from wechat_mall_user where open_id='%s'and usr_id=%s and  COALESCE(del_flag,0)=0" % (user_info['openId'], self.subusr_id)
            l,t = self.db.select(sqll)
            if t>0:#如果注册送积分增加积分
                jf="select score from score_send where usr_id=%s and COALESCE(del_flag,0)=0 and code=1  "% self.subusr_id
                f,g=self.db.select(jf)
                if g>0:
                    now_amount=int(f[0][0])
                    sqs="select now_amount from integral_log where  usr_id=%s and wechat_user_id=%s order by id desc"%(self.subusr_id,l[0][0])
                    k,h=self.db.select(sqs)
                    if h>0:
                        now_amount+=int(k[0][0])
                    ql="""insert into  integral_log(usr_id,wechat_user_id,type,typestr,in_out,inoutstr,amount,now_amount,cid,ctime)
                        values(%s,%s,%s,'%s',%s,'%s',%s,%s,%s,now())
                    """%(self.subusr_id,l[0][0],0,'注册赠送',0,'收入',int(f[0][0]),now_amount,l[0][0])
                    self.db.query(ql)
            return self.jsons({'code': 0, 'msg': 'success'})
        self.db.update('wechat_mall_user', data,'id=%s'%lT[0][0])
        sqll = "select id  from wechat_mall_user where open_id='%s'and usr_id=%s and COALESCE(del_flag,0)=0" % (user_info['openId'], self.subusr_id)
        #print(sqll)
        l, t = self.db.select(sqll)
        if t > 0:# 如果注册送积分增加积分
            jf = "select score from score_send where usr_id=%s and COALESCE(del_flag,0)=0 and code=1  " % self.subusr_id
            f, g = self.db.select(jf)
            if g > 0:
                now_amount = int(f[0][0])
                sqs = "select now_amount from integral_log where  usr_id=%s and wechat_user_id=%s order by id desc" % (self.subusr_id, l[0][0])
                k, h = self.db.select(sqs)
                if h > 0:
                    now_amount += int(k[0][0])
                ql = """insert into  integral_log(usr_id,wechat_user_id,type,typestr,in_out,inoutstr,amount,now_amount,cid,ctime)
                                        values(%s,%s,%s,'%s',%s,'%s',%s,%s,%s,now())
                    """ % (self.subusr_id, l[0][0], 0, '注册赠送', 0, '收入', int(f[0][0]), now_amount, l[0][0])
                self.db.query(ql)
        return self.jsons({'code': 0, 'msg': 'success'})

    def goPartlogin(self):#登录
        code=self.REQUEST.get('code','')

        if code=='' or code=='None':
            return self.jsons({'code': 300, 'data': {'msg': self.error_code[300].format('code')}})

        sql="select appid,secret  from mall where usr_id=%s"%self.subusr_id
        l,t=self.db.select(sql)

        if t==0:
            return self.jsons({'code': 404, 'msg': '请到后台填写‘微信设置’'})
        app_id = l[0][0]
        secret = l[0][1]

        api = wx_minapp_login(app_id, secret)
        session_info = api.get_session_info(code=code)

        if session_info.get('errcode'):
            return self.jsons({'code': -1, 'msg': self.error_code[-1], 'data': session_info.get('errmsg')})
        open_id = session_info['openid']
        session_key=session_info['session_key']

        sqll = "select id  from wechat_mall_user where open_id='%s' and  usr_id=%s and COALESCE(del_flag,0)=0" % (open_id,self.subusr_id)

        lT,iN=self.db.select(sqll)
        if iN==0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        wechat_user_id=lT[0][0]
        try:
            ip=self.objHandle.headers["X-Real-IP"]
        except:
            ip = self.objHandle.remote_addr

        sqli=" update wechat_mall_user set last_login=now(),ip='%s' where  id =%s and usr_id=%s "%(ip,lT[0][0],self.subusr_id)
        self.db.query(sqli)

        sqlt="select id,token from wechat_mall_access_token where open_id ='%s' and usr_id=%s"%(open_id,self.subusr_id)
        li,i=self.db.select(sqlt)

        if i==0:
            token=self.create_token(self.subusr_id, open_id, wechat_user_id)
            # token_max_hours = 2
            # s = Serializer(self.SECRET_KEY, expires_in=token_max_hours * 3600)
            # timestamp = time.time()
            # temp = s.dumps({'openid': open_id,'iat': timestamp})
            # token=temp.decode('ascii')#原来转为字符串
            #print(token)
            #ken = s.loads(token)#{'openid': open_id}

            data={
                'open_id': open_id,
                'session_key': session_key,
                'token':token,
                'usr_id':self.subusr_id,
                'create_date': self.getToday(9)
            }
            self.db.insert('wechat_mall_access_token',data)
            sqlt = "select id,token from wechat_mall_access_token where open_id ='%s' and usr_id=%s" % (open_id, self.subusr_id)
            l,t = self.db.select(sqlt)
        else:

            # token_max_hours = 2
            # s = Serializer(self.SECRET_KEY, expires_in=token_max_hours * 3600)
            # timestamp = time.time()
            # temp = s.dumps({'openid': open_id, 'iat': timestamp})
            # token = temp.decode('ascii')  # 原来转为字符串
            token = self.create_token(self.subusr_id, open_id, wechat_user_id)
            data = {
                'open_id': open_id,
                'session_key': session_key,
                'token': token,
                'create_date': self.getToday(9)

            }
            self.db.update('wechat_mall_access_token', data, "open_id ='%s' and usr_id=%s"%(open_id,self.subusr_id))
            sqlt = "select id,token from wechat_mall_access_token where open_id ='%s' and usr_id=%s" % (
            open_id, self.subusr_id)
            l, t = self.db.select(sqlt)
        try:
            access_token=l[0][1]
            uid=wechat_user_id
        except:
            access_token='None'
            uid=0

        return self.jsons({'code':0,'data':{'token': access_token,'uid':uid}})

    def goPartget_config(self):#参数设置接口  ok
        key=self.RQ('key', '')

        sql="select id,usr_id,key,datetype,content,remark,to_char(ctime,'YYYY-MM-DD HH:MM')ctime,to_char(utime,'YYYY-MM-DD HH:MM')utime from config_set  where usr_id=%s and key='%s' and COALESCE(del_flag,0)=0"%(self.subusr_id,key)
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 404,'msg':self.error_code[404]})
        for i in l:
            L={'creatAt':i[6],'dateType':i[3],'id':i[0],'key':i[2],'remark':i[5],'updateAt':i[7],'userId':i[1],'value':i[4]}
        return self.jsons({'code':0,'data':L,'msg':self.error_code['ok']})


    def goPartbanner_list(self):#Banner管理接口 OK
        type = self.RQ('type', '')

        sql="SELECT D.id,D.title,D.status,D.remark,D.linkurl,D.pic,D.paixu,to_char(ctime,'YYYY-MM-DD HH:MM'),D.usr_id,businessid,type FROM banner D where COALESCE(D.del_flag,0)=0 and D.usr_id = %s"%self.subusr_id
        if type != '':
            sql+="and type='%s'"%type
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        L=[]
        for i in l:
            statusStr='隐藏'
            if i[2]==0:
                statusStr='显示'
            a={'businessId':i[9],'dateAdd':i[7],'id':i[0],'linkUrl':i[4],'paixu':i[6],'picUrl':i[5],'remark':i[3],'status':i[2],'statusStr':statusStr,'title':i[1],'userId':i[8],'type':i[10]}
            L.append(a)
        return self.jsons({'code': 0, 'data': L,'msg':self.error_code['ok']})


    def goPartcategory_all(self):#商品分类接口
        sql="select id,usr_id,name,paixu,pid,icon,isuse,key,level,type,to_char(ctime,'YYYY-MM-DD HH:MM') from goods_category where COALESCE(del_flag,0)=0 and usr_id=%s  order by paixu"%self.subusr_id
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        L=[]
        for i in l:
            icon=i[5]
            L.append({'id':i[0],'name':i[2],'dateAdd':[10],'icon':icon,'isUse':i[6],'key':i[7],'level':i[8],'paixu':i[3],'pid':i[4],'type':i[9],'userId':i[1]})
        return self.jsons({'code':0,'data':L,'msg':self.error_code['ok']})

    def goPartaddress_default(self):
        token = self.REQUEST.get('token', '')

        if token == '' or token == 'None' or token == None:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 300, 'msg': 'token 无效，请重新登录'})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = l[0][0]
        sql = """select w.id,w.is_default,w.cityid,w.linkman,w.districtid,w.phone,w.postcode
                    ,w.address,w.provinceid,p.id,c.id,a.id,COALESCE(w.status,0),to_char(w.ctime,'YYYY-MM-DD HH:MM'),to_char(w.utime,'YYYY-MM-DD HH:MM')
                from wechat_mall_address w
                left join wechat_mall_province p on p.name=w.provinceid 
                left join wechat_mall_city c on c.name=w.cityid
                left join wechat_mall_district a on a.name=w.districtid
                where  COALESCE(w.is_default,0)=1 and COALESCE(w.del_flag,0)=0 and wechat_user_id=%s and usr_id=%s
        """ % (mall_user_id, self.subusr_id)
        # print(sql)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})

        A = l[0]
        if A[12] == int(0):
            statusStr = '启用'
        else:
            statusStr = '禁用'
        return self.jsons({
            "code": 0,
            "data": {
                "address": A[7],
                "areaStr": A[11],
                "cityId": A[2],
                "cityStr": A[10],
                "code": A[6],
                "dateAdd": A[13],
                "dateUpdate": A[14],
                "districtId": A[4],
                "id": A[0],
                "isDefault": 'true',
                "linkMan": A[3],
                "mobile": A[5],
                "provinceId": A[8],
                "provinceStr": A[9],
                "status": A[12],
                "statusStr": statusStr,
                "uid": mall_user_id,
                "userId": self.subusr_id
            },
            "msg": "success"
        })

    def goPartaddress_detail(self):
        token = self.REQUEST.get('token', '')
        id = self.RQ('id', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        if id == '' or id == 'None' or id == None:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 300, 'msg': 'token 无效，请重新登录'})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = l[0][0]
        sql = """select w.id,w.is_default,w.cityid,w.linkman,w.districtid,w.phone,w.postcode
                    ,w.address,w.provinceid,p.id,c.id,a.id,COALESCE(w.status,0),to_char(w.ctime,'YYYY-MM-DD HH:MM'),to_char(w.utime,'YYYY-MM-DD HH:MM')
                from wechat_mall_address w
                left join wechat_mall_province p on p.name=w.provinceid 
                left join wechat_mall_city c on c.name=w.cityid
                left join wechat_mall_district a on a.name=w.districtid
                where  COALESCE(w.del_flag,0)=0 and wechat_user_id=%s and usr_id=%s and w.id=%s 
        """ % (mall_user_id, self.subusr_id, id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})

        A = l[0]
        if A[12] == int(0):
            statusStr = '启用'
        else:
            statusStr = '禁用'
        return self.jsons({
            "code": 0,
            "data": {
                "address": A[7],
                "areaStr": A[11],
                "cityId": A[2],
                "cityStr": A[10],
                "code": A[6],
                "dateAdd": A[13],
                "dateUpdate": A[14],
                "districtId": A[4],
                "id": A[0],
                "isDefault": 'true',
                "linkMan": A[3],
                "mobile": A[5],
                "provinceId": A[8],
                "provinceStr": A[9],
                "status": A[12],
                "statusStr": statusStr,
                "uid": mall_user_id,
                "userId": self.subusr_id
            },
            "msg": "success"
        })

    def goPartaddress_add(self):
        token = self.REQUEST.get('token', '')
        id = self.RQ('id', '')
        provinceId = self.RQ('province', '')
        cityId = self.RQ('city', '')
        districtId = self.RQ('district', '')
        linkMan = self.RQ('linkMan', '')
        address = self.RQ('address', '')
        mobile = self.RQ('mobile', '')
        code = self.RQ('code', '')
        isDefault = self.RQ('isDefault', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if id == '' or id == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})
        if provinceId == '' or provinceId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('provinceId')})
        if cityId == '' or cityId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('cityId')})
        if districtId == '' or districtId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('districtId')})
        if linkMan == '' or linkMan == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('linkMan')})
        if address == '' or address == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('address')})
        if mobile == '' or mobile == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('mobile')})
        if code == '' or code == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('code')})
        if isDefault == '' or isDefault == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('isDefault')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 300, 'msg': 'token 无效，请重新登录'})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = l[0][0]
        if str(isDefault) == 'true':
            isDefault = 1
        else:
            isDefault = 0

        data = {
            "address": address,
            "cityid": cityId,
            "postcode": code,
            "ctime": self.getToday(9),
            "districtid": districtId,
            "is_default": isDefault,
            "linkman": linkMan,
            "phone": mobile,
            "provinceid": provinceId,
            "usr_id": self.subusr_id,
            "cid": mall_user_id,
            "wechat_user_id": mall_user_id
        }
        self.db.insert('wechat_mall_address', data)

        sql = "select id from wechat_mall_address where usr_id=%s and wechat_user_id=%s order by id desc" % (
        self.subusr_id, mall_user_id)
        l, t = self.db.select(sql)
        if t > 0:
            if str(isDefault) == '1':
                self.db.query(
                    "update wechat_mall_address set is_default=0 where wechat_user_id=%s and usr_id=%s and id!=%s " % (
                        mall_user_id, self.subusr_id, l[0][0]))
            return self.jsons({'code': 0, 'msg': self.error_code['ok']})

        return self.jsons({'code': 404, 'msg': self.error_code[404]})

    def goPartaddress_update(self):

        token = self.REQUEST.get('token', '')
        id = self.RQ('id', '')
        provinceId = self.RQ('province', '')
        cityId = self.RQ('city', '')
        districtId = self.RQ('district', '')
        linkMan = self.RQ('linkMan', '')
        address = self.RQ('address', '')
        mobile = self.RQ('mobile', '')
        code = self.RQ('code', '')
        isDefault = self.RQ('isDefault', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if id == '' or id == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})
        # if provinceId == '' or provinceId == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('provinceId')})
        # if cityId == '' or cityId == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('cityId')})
        # if districtId == '' or districtId == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('districtId')})
        # if linkMan == '' or linkMan == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('linkMan')})
        # if address == '' or address == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('address')})
        # if mobile == '' or mobile == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('mobile')})
        # if code == '' or code == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('code')})
        # if isDefault == '' or isDefault == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('isDefault')})
        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 300, 'msg': 'token 无效，请重新登录'})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = l[0][0]
        if str(isDefault) == 'true':
            isDefault = 1
        else:
            isDefault = 0
        if not provinceId:
            if isDefault == 1:
                self.db.query(
                    "update wechat_mall_address set is_default=1 where wechat_user_id=%s and usr_id=%s and id=%s " % (
                    mall_user_id, self.subusr_id, id))
                self.db.query(
                    "update wechat_mall_address set is_default=0 where wechat_user_id=%s and usr_id=%s and id!=%s " % (
                        mall_user_id, self.subusr_id, id))
                return self.jsons({'code': 0, 'msg': self.error_code['ok']})
        data = {
            "address": address,
            "cityid": cityId,
            "postcode": code,
            "utime": self.getToday(9),
            "districtid": districtId,
            "is_default": isDefault,
            "linkman": linkMan,
            "phone": mobile,
            "provinceid": provinceId,
            "usr_id": self.subusr_id,
            "uid": mall_user_id,
            "wechat_user_id": mall_user_id
        }

        try:
            self.db.update('wechat_mall_address', data, 'id=%s' % id)
            if isDefault == 1:
                self.db.query(
                    "update wechat_mall_address set is_default=0 where wechat_user_id=%s and usr_id=%s and id!=%s " % (
                    mall_user_id, self.subusr_id, id))
            return self.jsons({'code': 0, 'msg': self.error_code['ok']})
        except:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})

    def goPartaddress_list(self):
        token = self.REQUEST.get('token', '')
        # id = self.RQ('id')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 300, 'msg': 'token 无效，请重新登录'})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = l[0][0]
        sql = """select w.id,w.is_default,w.cityid,w.linkman,w.districtid,w.phone,w.postcode
                            ,w.address,w.provinceid,p.id,c.id,a.id,COALESCE(w.status,0),to_char(w.ctime,'YYYY-MM-DD HH:MM'),to_char(w.utime,'YYYY-MM-DD HH:MM')
                        from wechat_mall_address w
                        left join wechat_mall_province p on p.name=w.provinceid 
                        left join wechat_mall_city c on c.name=w.cityid
                        left join wechat_mall_district a on a.name=w.districtid 
                        where COALESCE(w.del_flag,0)=0 and wechat_user_id=%s and usr_id=%s order by w.is_default desc ,w.id asc
                """ % (mall_user_id, self.subusr_id)
        l, t = self.db.select(sql)
        # print(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})
        L = []
        for A in l:
            if A[12] == int(0):
                statusStr = '启用'
            else:
                statusStr = '禁用'
            if str(A[1]) == '1':
                L.append({
                    "address": A[7],
                    "areaStr": A[11],
                    "cityId": A[2],
                    "cityStr": A[10],
                    "code": A[6],
                    "dateAdd": A[13],
                    "dateUpdate": A[14],
                    "districtId": A[4],
                    "id": A[0],
                    "isDefault": 'true',
                    "linkMan": A[3],
                    "mobile": A[5],
                    "provinceId": A[8],
                    "provinceStr": A[9],
                    "status": A[12],
                    "statusStr": statusStr,
                    "uid": mall_user_id,
                    "userId": self.subusr_id
                })
            else:

                L.append({
                    "address": A[7],
                    "areaStr": A[11],
                    "cityId": A[2],
                    "cityStr": A[10],
                    "code": A[6],
                    "dateAdd": A[13],
                    "dateUpdate": A[14],
                    "districtId": A[4],
                    "id": A[0],
                    "linkMan": A[3],
                    "mobile": A[5],
                    "provinceId": A[8],
                    "provinceStr": A[9],
                    "status": A[12],
                    "statusStr": statusStr,
                    "uid": mall_user_id,
                    "userId": self.subusr_id
                })
        return self.jsons({"code": 0, "data": L, "msg": "success"})

    def goPartaddress_delete(self):
        token = self.REQUEST.get('token', '')
        id = self.RQ('id', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if id == '' or id == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 300, 'msg': 'token 无效，请重新登录'})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = l[0][0]

        sql = "select id from wechat_mall_address where usr_id=%s and id=%s and wechat_user_id=%s" % (
        self.subusr_id, id, mall_user_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        sql = "update wechat_mall_address set del_flag=1 where usr_id=%s and id=%s and wechat_user_id=%s" % (
        self.subusr_id, id, mall_user_id)
        self.db.query(sql)
        return self.jsons({'code': 0, 'msg': self.error_code['ok']})


    def goPartfav_list(self):#收藏列表接口
        token = self.REQUEST.get('token', '')
        name=self.RQ('nameLike','')
        if token=='' or token =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l,t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t==0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})


        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n= self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})
        L = []
        mall_user_id = m[0][0]
        fvl="select id,gid,gname,gpic,cid,to_char(ctime,'YYYY-MM-DD HH:MM') from shouchang where usr_id=%s and wechat_user_id=%s and  COALESCE(del_flag,0)=0"%(self.subusr_id,mall_user_id)
        if name!='':
            fvl +="and gname='%%%s%%' "%name

        lt,ni=self.db.select(fvl)
        if ni==0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        for v in lt:
            L.append({'dateAdd':v[5],'goodsId':v[1],'goodsName':v[2],'id':v[0],'pic':v[3],'userId':self.subusr_id,'uid':mall_user_id})
        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})


    def goPartfav_add(self):#添加收藏接口
        token = self.REQUEST.get('token', '')
        goodsid=self.RQ('goodsId','')

        if token=='' or token =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if goodsid=='' or goodsid =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsid')})
        try:
            goodsid=int(goodsid)
        except:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsid')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l,t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t==0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n= self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        fvl="select id,gid,gname,gpic,cid,to_char(ctime,'YYYY-MM-DD HH:MM') from shouchang where usr_id=%s and wechat_user_id=%s and gid=%s"%(self.subusr_id,mall_user_id,goodsid)

        lt,ni=self.db.select(fvl)
        if ni>0:
            sqls = "select name,pic from goods_info where id=%s" % goodsid
            f, r = self.db.select(sqls)
            if r == 0:
                return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsId')})
            self.db.query("update shouchang set gname='%s',gpic='%s',del_flag=0,uid=%s,utime=now() where usr_id=%s and wechat_user_id=%s and gid=%s"%(f[0][0],f[0][1],mall_user_id,self.subusr_id,mall_user_id,goodsid))
        else:
            sqls="select name,pic from goods_info where id=%s"%goodsid
            f,r =self.db.select(sqls)
            if r==0:
                return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsId')})

            sqla="""insert into shouchang(usr_id,wechat_user_id,gid,gname,gpic,cid,ctime)
                 values(%s,%s,%s,'%s','%s',%s,now())"""%(self.subusr_id,mall_user_id,goodsid,f[0][0],f[0][1],mall_user_id)
            self.db.query(sqla)
        return self.jsons({'code': 0,'msg': self.error_code['ok']})


    def goPartfav_del(self):#取消收藏接口
        token = self.REQUEST.get('token', '')
        goodsid=self.REQUEST.get('goodsId','')
        id = self.REQUEST.get('id','')
        if token=='' or token =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if (goodsid=='' or goodsid =='None') and  (id=='' or id =='None'):
            return self.jsons({'code': 300, 'msg': self.error_code[300]})
        try:
            if goodsid:
                goodsid=int(goodsid)
            if id:
                id=int(id)
        except:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsId')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l,t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t==0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n= self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        fvl="select id,gid,gname,gpic,cid,to_char(ctime,'YYYY-MM-DD HH:MM') from shouchang where usr_id=%s and wechat_user_id=%s and gid=%s"%(self.subusr_id,mall_user_id,goodsid)

        lt,ni=self.db.select(fvl)
        if ni==0:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsId')})
        sqls="update shouchang set del_flag=1,uid=%s,utime=now() where usr_id=%s and wechat_user_id=%s"%(mall_user_id,self.subusr_id,mall_user_id)
        if id:
            sqls+=" and id=%s"%id
        if goodsid:
            sqls+=" and gid=%s"%goodsid
        self.db.query(sqls)

        return self.jsons({'code': 0,'msg': self.error_code['ok']})



    def goPartget_login(self): #
        # token = self.REQUEST.get('token', '')
        #
        #
        # if token == '' or token == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        #
        # l, t = self.db.select(
        #     "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        # if t == 0:
        #     return self.jsons({'code': 901, 'msg': self.error_code[901]})
        #

        L, T = self.db.select("select appid,secret,mchid,mchkey from mall where usr_id=%s" % self.subusr_id)
        if T == 0:
            return self.jsons({'code': 10000, 'msg': '请到后台微信设置里进行设置微信APPID和secret'})
        app_id = L[0][0]


        L={'id':app_id,'stoken':'sdfsapdfijsafjoijasfojsadflm'}
        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})




