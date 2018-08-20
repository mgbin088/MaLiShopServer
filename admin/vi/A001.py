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



class cA001(cBASE_TPL):
    
    def setClassName(self):
        #设定要实例的 dl类和TPL类，为空则继承基类，可以能过判断part的值来设置不同的类名
        '''
        if self.part == 'xxx':
            self.dl_name = 'xxx_dl'
        '''
        self.dl_name = 'A001_dl'
        self.inframe = 1
    def specialinit(self):
        self.viewid = 'A001'

    def goPartList(self):

        self.assign('NL',self.dl.GNL)
        self.navTitle = '店铺信息'
        self.getBreadcrumb() #获取面包屑
        PL,L = self.dl.mRight()
        self.assign('dataList',L)
        self.getPagination(PL)
        s = self.runApp('A001_list.html')
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
        self.navTitle = '店铺信息'

        self.need_editor = 1
        self.getBreadcrumb() #获取面包屑
        self.initHiddenLocal()#初始隐藏域
        self.getBackBtn()

        self.item = self.dl.get_local_data(self.pk)
        self.assign('item', self.item)
        latitude=self.item.get('latitude',39.916527)
        longitude = self.item.get('longitude',116.397128)
        self.assign('latitude', latitude)
        self.assign('longitude', longitude)



        #所在地址联动选择
        province = self.Html.select(self.dl.get_provinceid_data(), 'provinceid', '',
                                 {'class': "form-control", 'onchange': "province()", 'id': 'parentid'})
        self.assign('province', province)

        city = self.Html.select(self.dl.get_cityid_data(), 'cityid', '',
                                    {'class': "form-control", 'onchange': "city()", 'id': 'cityid'})
        self.assign('city', city)

        area = self.Html.select(self.dl.get_cityid_data(), 'districtid', '',
                                {'class': "form-control", 'id': 'areaid'})
        self.assign('area', area)

        # 产品类型select
        # sptype = self.dl.getlx_type(3, '', '--请选择--')
        ZT=[['0','正常'],['1','禁用']]
        status = self.Html.select(ZT, 'status', '', {'class': "form-control"})
        self.assign('status', status)
        s = self.runApp('A001_local.html')
        return s

    def goPartGetcity(self):

        aa=self.dl.get_cityid_data(self.dl.GP('parentid'))

        return self.jsons({'aa':aa})

    def goPartGetarea(self):

        aa=self.dl.get_areaid_data(self.dl.GP('cityid'))

        return self.jsons({'aa':aa})
    
    
        
 