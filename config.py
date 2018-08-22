# -*- coding: utf-8 -*-

##############################################################################
#
#
##############################################################################

import os
CLIENT_NAME = 'MaLiShopServer'#注意:这个是项目名，要跟下边的路径对应，然后数据库名也要跟这个一样
DEBUG='1'


WEBSITE_PATHR = os.path.join('/var/games/', CLIENT_NAME)
fnamer = r'/var/games/%s/%s.log' %(CLIENT_NAME,CLIENT_NAME)
ROOTR = r'/var/games'
SITE_ROOTR = r'/var/games/' + CLIENT_NAME
PDF_OUT_PATHR = r'/var/games/%s/static/data/pdf'%CLIENT_NAME
ATTACH_ROOTR = r'/var/games/%s/static/data'%CLIENT_NAME

#################数据库相关配置

scott='pgsql'#用户名
tiger = 'Y123456'#密码
host = '127.0.0.1'#地址
port='5432'#端口
################
