# -*- coding: utf-8 -*-

##############################################################################
#
#
#
##############################################################################
"""BIZ_BASE Module"""


import time,hashlib
from imp import reload
import basic
reload(basic)
from basic import public
DEBUG,CLIENT_NAME=public.DEBUG,public.CLIENT_NAME

if DEBUG=='1':
    import admin.dl.MODEL_DL
    reload(admin.dl.MODEL_DL)
from admin.dl.MODEL_DL             import cMODEL_DL
from qiniu import Auth, put_stream, put_data
#需要填写你的 Access Key 和 Secret Key
#access_key = app.config['QINIU_ACCESS_KEY']
#secret_key = app.config['QINIU_SECRET_KEY']
#构建鉴权对象
#q = Auth(access_key, secret_key)
#要上传的空间
#bucket_name = app.config['QINIU_BUCKET_NAME']
#domain_prefix = app.config['QINIU_DOMAIN']

class cBASE_DL(cMODEL_DL):

    def qiniu_Upload(self):

        file = self.objHandle.files['file']  # request的files属性为请求中文件的数据<input 里的name="file">
        url = ''
        if file.filename.find('.') > 0:
            file_ext = file.filename.rsplit('.', 1)[1].strip().lower()

            timeStamp = time.time()
            md5name = hashlib.md5()
            md5name.update(str(timeStamp).encode('utf-8'))
            filename = md5name.hexdigest() + '.' + file_ext
            file = file.read()
            url = self.qiniu_upload_file(file, filename)
        return url
    def qiniu_upload_file(self,source_file, save_file_name):

        sql='select access_key,secret_key,name, domain from qiniu where usr_id =%s '
        l,t=self.db.select(sql,self.usr_id)
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




