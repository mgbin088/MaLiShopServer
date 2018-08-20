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

if DEBUG=='1':
    import admin.vi.BASE_TPL
    reload(admin.vi.BASE_TPL)
from admin.vi.BASE_TPL             import cBASE_TPL

class cB001(cBASE_TPL):
    
    def setClassName(self):
        self.dl_name = 'B001_dl'
    def specialinit(self):
        self.viewid = 'B001'

        self.navTitle = 'Banner管理'


    def initPagiUrl(self):
        qqid = self.REQUEST.get('qqid','')
        url = self.sUrl
        if qqid:
            url += "&qqid=%s" % qqid
        return url

    def goPartList(self):
        self.getBreadcrumb()  # 获取面包屑
        self.assign('NL',self.dl.GNL)
        PL,L = self.dl.mRight()
        self.assign('dataList',L)
        self.getPagination(PL)
        s = self.runApp('B001_list.html')
        return s
    
    def goPartLocalfrm(self):

        self.need_editor = 1
        self.initHiddenLocal()#初始隐藏域
        self.getBreadcrumb()  # 获取面包屑
        self.getBackBtn()

        item = self.dl.get_local_data()
        self.assign('item',item)
        s = self.runApp('B001_local.html')
        return s


    