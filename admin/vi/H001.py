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
DEBUG , CLIENT_NAME=public.DEBUG,public.CLIENT_NAME

if DEBUG=='1':
    import admin.vi.BASE_TPL
    reload(admin.vi.BASE_TPL)
from admin.vi.BASE_TPL             import cBASE_TPL

class cH001(cBASE_TPL):
    
    def setClassName(self):
        #设定要实例的 dl类和TPL类，为空则继承基类，可以能过判断part的值来设置不同的类名
        '''
        if self.part == 'xxx':
            self.dl_name = 'xxx_dl'
        '''
        self.dl_name = 'H001_dl'
        self.inframe = 1
    def specialinit(self):
        self.viewid = 'H001'

    def goPartList(self):
        self.initHiddenLocal()  # 初始隐藏域
        self.navTitle = '个人账号管理' #% self.objHandle.method
        self.getBreadcrumb() #获取面包屑
        info = self.dl.getInfo()
        self.assign('info',info)

        s = self.runApp('H001_list.html')
        return s
    
    
    
    
        
 