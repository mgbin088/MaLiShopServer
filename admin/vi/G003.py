# -*- coding: utf-8 -*-
##############################################################################
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



class cG003(cBASE_TPL):
    
    def setClassName(self):
        #设定要实例的 dl类和TPL类，为空则继承基类，可以能过判断part的值来设置不同的类名
        '''
        if self.part == 'xxx':
            self.dl_name = 'xxx_dl'
        '''
        self.dl_name = 'G003_dl'
        self.inframe = 1
    def specialinit(self):
        self.viewid = 'G003'

    def goPartList(self):
      
        self.assign('NL',self.dl.GNL)
        self.navTitle = '采购订单'
        self.getBreadcrumb() #获取面包屑

        L = self.dl.mRight()
        self.assign('item',L)

        #self.getPagination(PL)
        s = self.runApp('G003_list.html')
        return s
    

    
    def goPartLocalfrm(self):
        self.navTitle = 'API工厂同步设置'

        self.need_editor = 1
        self.getBreadcrumb() #获取面包屑
        self.initHiddenLocal()#初始隐藏域
       
        self.getBackBtn()

        self.item = self.dl.get_local_data()
        self.assign('item', self.item)

        s = self.runApp('G003_local.html')
        return s

    def goPartsync_data(self):
        dR=self.dl.sync_data()
        return self.jsons(dR)
    
    
    
        
 