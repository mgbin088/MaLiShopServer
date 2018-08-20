# -*- coding: utf-8 -*-
##############################################################################
#

#
##############################################################################


from imp import reload
import basic
reload(basic)
from basic import public
DEBUG=public.DEBUG

if DEBUG=='1':
    import admin.vi.BASE_TPL
    reload(admin.vi.BASE_TPL)
from admin.vi.BASE_TPL             import cBASE_TPL



class cG005(cBASE_TPL):
    
    def setClassName(self):
        #设定要实例的 dl类和TPL类，为空则继承基类，可以能过判断part的值来设置不同的类名
        '''
        if self.part == 'xxx':
            self.dl_name = 'xxx_dl'
        '''
        self.dl_name = 'G005_dl'
        self.inframe = 1
    def specialinit(self):
        self.viewid = 'G005'

    def goPartList(self):

        self.assign('NL',self.dl.GNL)
        self.navTitle = '采购订单'
        self.getBreadcrumb() #获取面包屑
        PL,L = self.dl.mRight()
        self.assign('dataList',L)

        self.getPagination(PL)
        s = self.runApp('G005_main.html')
        return s
    
    def initPagiUrl(self):
        lb_code = self.REQUEST.get('lb_code','')
        brand_id = self.REQUEST.get('brand_id','')
        status = self.REQUEST.get('status','')
        ctype = self.REQUEST.get('ctype','')
        qqid = self.REQUEST.get('qqid','')
        url = self.sUrl
        if qqid:
            url += "&qqid=%s" % qqid
        if lb_code:
            url += "&lb_code=%s" % lb_code
        if brand_id:
            url += "&brand_id=%s" % brand_id
        if status:
            url += "&status=%s" % status
        if ctype:
            url += "&ctype=%s" % ctype
        return url
    
    def goPartLocalfrm(self):
        self.navTitle = '商城公告'

        self.need_editor = 1
        self.getBreadcrumb() #获取面包屑
        self.initHiddenLocal()#初始隐藏域

        self.getBackBtn()

        self.item = self.dl.get_local_data(self.pk)
        self.assign('item', self.item)

        s1 = self.Html.editor(self.item.get('content',''),'container', '1000px', '300px')
        self.assign('editor', s1)

        fl = self.dl.getfllist()
        fllist = self.Html.select(fl, 'fenlei', self.item.get('fenlei', 0), {'class': 'form-control'})
        self.assign('fllist', fllist)

        s = self.runApp('G005_local.html')
        return s
    
    
    
        
 