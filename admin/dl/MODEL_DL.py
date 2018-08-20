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
cMODEL_ad=public.cMODEL_ad
from qiniu import Auth, put_stream, put_data
#需要填写你的 Access Key 和 Secret Key
#access_key = app.config['QINIU_ACCESS_KEY']
#secret_key = app.config['QINIU_SECRET_KEY']
#构建鉴权对象
#q = Auth(access_key, secret_key)
#要上传的空间
#bucket_name = app.config['QINIU_BUCKET_NAME']
#domain_prefix = app.config['QINIU_DOMAIN']

class cMODEL_DL(cMODEL_ad):

    def getmtcdata(self, type, df='', title='请选择'):
        if title != '':
            L = [['', title, '']]
        else:
            L = []
        if type != '':
            sql = "select id,txt1 from mtc_t where type='%s' order by sort" % type
            lT, iN = self.db.select(sql)
            if iN > 0:
                for e in list(lT):
                    id, txt = e
                    b = ''
                    if str(df) == str(id):
                        b = ' selected="selected"'
                    L.append([id, txt, b])
        return L

    def getmtctxt(self, type, sDF):
        s = ''
        if type != '' and sDF != '':
            sql = "select txt1 from mtc_t where type='%s' and id=%s" % (type, sDF)
            lT, iN = self.db.select(sql)
            if iN > 0:
                s = lT[0][0]
        return s

    def save_upload_file(self, pk, src):

        # file_pk = self.REQUEST.get('file_pk')
        file_pk = self.REQUEST.getlist("file_pk")
        if file_pk:
            if isinstance(file_pk, list):
                sql = ''
                for v in file_pk:
                    sql += '''update file_pic set SRC='%s' , m_id = %s where seq = %s;
                    ''' % (src, pk, v)
                if sql != '':
                    self.db.query(sql)
            else:
                sql = "update file_pic set SRC='%s' , m_id = %s where seq = %s" % (src, pk, file_pk)
                self.db.query(sql)

    def get_upload_file(self, pk):
        if pk and self.src:
            sql = '''
            select fp.seq , fp.file_name , fp.file_size , fp.is_pic ,u.usr_name , to_char(fp.ctime,'YYYY-MM-DD') , fp.fname 
            from file_pic fp left join users u on u.usr_id = fp.cid where fp.m_id = %s  and fp.src = '%s' order by fp.seq asc
            ''' % (pk, self.src)
            L, t = self.db.select(sql)
            return L
        else:
            return []







