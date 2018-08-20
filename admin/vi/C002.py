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


class cC002(cBASE_TPL):
    
    def setClassName(self):
        self.dl_name = 'C002_dl'


    def specialinit(self):

        self.viewid = 'C002'
        self.navTitle = '商品明细'


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
        s = self.runApp('C002_list.html')
        return s
    
    def goPartLocalfrm(self):
        self.getBreadcrumb()  # 获取面包屑
        self.navTitle = '商品管理'

        self.need_editor = 1
        self.initHiddenLocal()#初始隐藏域
        
        self.getBackBtn()
        item = self.dl.get_local_data()
        self.assign('item', item)
        pics = self.dl.get_pics_data()
        propertyids=''
        #print(item.get('propertyids'))
        try:
            if item.get('propertyids','')!='':
                propertyids=int(item.get('propertyids'))
            self.assign('property_seln', '')
        except:
            if 'None'not in item.get('propertyids'):
                propertyids=int(item.get('propertyids')[0])
                self.assign('property_seln', item.get('propertyids')[-1])


        property_sel1 = self.Html.select(self.dl.property_list(), 'property_sel1', propertyids,
                                    {'class': "form-control", 'onchange': "property_sel()"})
        self.assign('property_sel1', property_sel1)
        self.assign('pics', pics)

        self.assign({'shoplist':self.dl.shop_list()#店铺
                     ,'goodlist':self.dl.good_list()#商品分类
                     ,'logistics':self.dl.logistics_list()#物流模板
                     })

       
        s = self.runApp('C002_local.html')
        return s

    def goPartAddids(self):
        ids=self.dl.GP('ids','')
        pk = self.dl.GP('pk','')
        l=self.dl.get_ids(ids)
        p = self.dl.get_property(ids)

        M=[]
        for i in p:
            for j in l:
                if i[0]==j[0]:
                    A=str(i[0])+':'+str(j[1])+','
                    B = i[1] + '(' + j[2] + ')'
                    M.append([B,A])

        d=''
        L=self.dl.get_gg(pk)

        for k in M:
            if len(L)>0:
                for v in L:
                    if v[0]==k[0]:
                        d+='<div class="row">%s<input type="hidden" name="ggname" value="%s"><input type="hidden" name="property_child_ids" value="%s"><div class="col-sm-12 ">'%(v[0],v[0],v[1])
                        d+='原价:<input type="text" name="originalpriceext" style="width:60px;" value="%s">'%v[2]
                        d+='现价:<input type="text" name="minpriceext" style="width:60px;" value="%s">'%v[3]
                        d+= '拼团价:<input type="text" name="ptpriceext" style="width:60px;" value="%s">'%v[4]
                        d+='会员价:<input type="text" name="hypriceext" style="width:60px;" value="%s">'%v[7]
                        d += '积分:<input type="text" name="scoreext" style="width:60px;" value="%s">' % v[5]
                        d+='库存数:<input type="text" name="storesext" style="width:60px;" value="%s">'%v[6]
                        d+='</div></div><br>'
            else:
                d += '<div class="row">%s<input type="hidden" name="ggname" value="%s"><input type="hidden" name="property_child_ids" value="%s"><div class="col-sm-12 ">' % (k[0],k[0], k[1])
                d += '原价:<input type="text" name="originalpriceext" style="width:60px;" value="0">'
                d += '现价:<input type="text" name="minpriceext" style="width:60px;" value="0">'
                d += '拼团价:<input type="text" name="ptpriceext" style="width:60px;" value="0">'
                d += '会员价:<input type="text" name="hypriceext" style="width:60px;" value="0">'
                d += '积分:<input type="text" name="scoreext" style="width:60px;" value="0">'
                d += '库存数:<input type="text" name="storesext" style="width:60px;" value="0">'
                d += '</div></div><br>'

        return d

    def goPartAddsel(self):

        ids = self.dl.GP('ids', '')
        idsn = self.dl.GP('idsn', '')
        d = ''
        try:
            int(ids)

            l = self.dl.get_property_no(ids)
        except:
            return d

        try:
            a=int(idsn)
        except:
            a=''


        if len(l)>0:
            d+='<select class ="form-control" onchange="property_sel2()"  name="property_seln" >'

            for k in l:
                if a==k[0]:
                    d += '<option value="%s" selected="selected">%s</option>' % (k[0], k[1])
                else:
                    d+='<option value="%s">%s</option>'%(k[0],k[1])
            d += '</select>'

        return d

    def goPartAddidsnext(self):
        ids = self.dl.GP('ids', '')
        idsn = self.dl.GP('idsn', '')
        pk = self.dl.GP('pik', '')
        l = self.dl.get_ids(ids)
        p = self.dl.get_property(ids)
        ln = self.dl.get_ids(idsn)
        pn = self.dl.get_property(idsn)

        M = []
        Mn = []
        MM=[]
        for i in p:
            for j in l:
                if i[0] == j[0]:
                    A = str(i[0]) + ':' + str(j[1])
                    B = i[1] + '(' + j[2] + ')'
                    M.append([B, A])
        if len(pn)>0:
            for i in pn:
                for j in ln:
                    if i[0] == j[0]:
                        A = str(i[0]) + ':' + str(j[1])
                        B = i[1] + '(' + j[2] + ')'
                        Mn.append([B, A])

        if len(Mn)>0:
            for m in M:
                for n in Mn:
                    A=m[1]+','+n[1]+','
                    B=m[0]+'—'+n[0]
                    MM.append([B, A])
        else:
            MM=M

        d = ''
        L = self.dl.get_gg(pk)

        for k in MM:
            if len(L) > 0:
                for v in L:
                    if v[0] == k[0]:
                        d += '<div class="row">%s<input type="hidden" name="ggname" value="%s"><input type="hidden" name="property_child_ids" value="%s"><div class="col-sm-12 ">' % (
                        v[0], v[0], v[1])
                        d += '原价:<input type="text" name="originalpriceext" style="width:60px;" value="%s">' % v[2]
                        d += '现价:<input type="text" name="minpriceext" style="width:60px;" value="%s">' % v[3]
                        d += '拼团价:<input type="text" name="ptpriceext" style="width:60px;" value="%s">' % v[4]
                        d += '会员价:<input type="text" name="hypriceext" style="width:60px;" value="%s">' % v[7]
                        d += '积分:<input type="text" name="scoreext" style="width:60px;" value="%s">' % v[5]
                        d += '库存数:<input type="text" name="storesext" style="width:60px;" value="%s">' % v[6]
                        d += '</div></div><br>'
            else:
                d += '<div class="row">%s<input type="hidden" name="ggname" value="%s"><input type="hidden" name="property_child_ids" value="%s"><div class="col-sm-12 ">' % (
                k[0], k[0], k[1])
                d += '原价:<input type="text" name="originalpriceext" style="width:60px;" value="0">'
                d += '现价:<input type="text" name="minpriceext" style="width:60px;" value="0">'
                d += '拼团价:<input type="text" name="ptpriceext" style="width:60px;" value="0">'
                d += '会员价:<input type="text" name="hypriceext" style="width:60px;" value="0">'
                d += '积分:<input type="text" name="scoreext" style="width:60px;" value="0">'
                d += '库存数:<input type="text" name="storesext" style="width:60px;" value="0">'
                d += '</div></div><br>'

        return d


