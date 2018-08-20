# -*- coding: utf-8 -*-

##############################################################################
#
#
#
#
##############################################################################
"""VI_BASE Module"""


import os,importlib,urllib,time,datetime,random,jwt,hashlib
from imp import reload
from config import DEBUG,CLIENT_NAME
from qiniu import Auth, put_stream, put_data

if DEBUG=='1':
    import basic
    reload(basic)
from basic import public
cVIEWS_api=public.cVIEWS_api

# {
#     -1: u'服务器内部错误',
#     0: u'接口调用成功',
#     403: u'禁止访问',
#     405: u'错误的请求类型',
#     501: u'数据库错误',
#     502: u'并发异常，请重试',
#     600: u'缺少参数',
#     601: u'无权操作:缺少 token',
#     602: u'签名错误',
#     700: u'暂无数据',
#     701: u'该功能暂未开通',
#     702: u'资源余额不足',
#     901: u'登录超时',
#     300: u'缺少{}参数',
#     400: u'域名错误',
#     401: u'该域名已删除',
#     402: u'该域名已禁用',
#     404: u'暂无数据',
#     10000: u'微信用户未注册',
#     'ok':'success'
# }
class cVI_BASE(cVIEWS_api):

    def RQ(self, key, default=None, ctype=1):
        value = self.REQUEST.get(key, default)
        L_error = ['"', "'", '%', '#', '&', '*', '(', ')', '@', '`', '\\', ']', ',', '=', '<', '>']
        if ctype==1:
            for c in L_error:
                if c in value:
                    value=value.replace(c,'')
        # if ctype == 1 and value and isinstance(value, str):
        #     self.myaddslashes(value.strip())
        return value

    def create_token(self,usr_id,open_id,wechat_user_id):

        payloads = {
            "iss": "janedao.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 60 * 60 * 2,  # 60*60*24  一天
            "aud": "www.janedao.com",
            "usr_id": usr_id,
            "open_id": open_id,
            "wechat_user_id":wechat_user_id,
            "scopes": random.random()
        }
        encoded_jwt = jwt.encode(payloads, 'secret', algorithm='HS256')
        token = encoded_jwt.decode('utf-8')
        return token

    def check_token(self,token):
        dR = {'MSG': '', 'code': ''}

        payload = jwt.decode(token, 'secret', audience='www.janedao.com', algorithms=['HS256'])
        if not payload:
            dR['code'] = 1
            dR['MSG'] = 'token无效，无法解密'
            return dR

        if payload['iss'] != "janedao.com":
            dR['code'] = 1
            dR['MSG'] = 'token无效，iss错误'
            return dR

        if payload['exp'] < int(time.time()):
            dR['code'] = 1
            dR['MSG'] = 'token无效，exp超时'
            return dR

        if payload['aud'] != "www.janedao.com":
            dR['code'] = 1
            dR['MSG'] = 'token无效，aud错误'
            return dR

        dR['code'] = 0
        return dR

    def qiniu_Upload(self):

        file = self.objHandle.files['audio']  # request的files属性为请求中文件的数据<input 里的name="file">
        url = ''
        if file.filename.find('.') > 0:
            file_ext = file.filename.rsplit('.', 1)[1].strip().lower()

            timeStamp = time.time()
            md5name = hashlib.md5()
            md5name.update(str(timeStamp).encode('utf-8'))
            filename = md5name.hexdigest() + '.' + file_ext
            file.save(os.path.join(public.ATTACH_ROOT, filename))
            #url="static/data/%s"%filename
            url =filename
            #file = file.read()
            #url = self.qiniu_upload_file(file, filename)
        return url
    def qiniu_upload_file(self,source_file, save_file_name):

        sql='select access_key,secret_key,name, domain from qiniu where usr_id =%s '
        l,t=self.db.select(sql,self.subusr_id)
        if t==0:
            return ''
        access_key,secret_key,bucket_name,domain_prefix=l[0][0],l[0][1],l[0][2],l[0][3]
        #bucket_name 是存储空间列表名,domain_prefix是外链默认域名链接
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        token = q.upload_token(bucket_name, save_file_name)
        ret, info = put_data(token, save_file_name, source_file)
        if info.status_code == 200:
            return domain_prefix + save_file_name
        return None


