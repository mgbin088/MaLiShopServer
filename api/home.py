# -*- coding: utf-8 -*-
##############################################################################
#
#
#
#
#
##############################################################################



from imp import reload
from config import DEBUG

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from weixin import WXAPPAPI
from weixin.lib.wxcrypt import WXBizDataCrypt
import hashlib,time,json,datetime
from .pay import WeixinPay
from .helper import md5_constructor as md5
from .wxpay import WxPay, get_nonce_str, dict_to_xml, xml_to_dict

if DEBUG == '1':
    import api.BASE_TPL
    reload(api.BASE_TPL)
from api.BASE_TPL            import cBASE_TPL

class chome(cBASE_TPL):


    def goPartgoods_list(self):#商品列表
        #page int 获取第几页数据，不传该参数默认为1  X
        #pageSize int  每页获取多少条数据，不传该参数默认为50  X
        #shopId  int  获取指定店铺的商品数据，不传获取全部商品；0 获取未归类店铺商品；其他数字为指定的店铺编号下的商品 X
        #categoryId int 获取指定分类下的商品 X
        #recommendStatus  int 推荐状态：不传该参数获取所有商品；0  为一般商品；1 为推荐商品 X
        #nameLike String  商品名称关键词模糊搜索  X
        #barCode  String  商品条码 X
        #orderBy String 排序规则：priceUp  商品升序，priceDown 商品倒序，ordersUp  销量升序，ordersDown  销量降序 X
        #pingtuan Boolean  true  为拉取支持拼团的商品 X

        shopid = self.RQ('shopId', '')
        lb_id = self.RQ('categoryId', '')
        recommendStatus = self.RQ('recommendStatus', '')
        nameLike = self.RQ('nameLike', '')
        barCode = self.RQ('barCode', '')
        orderBy = self.RQ('orderBy', '')
        pingtuan = self.RQ('pingtuan', '')
        if pingtuan=='true':
            pt=1
        else:
            pt=0
        sql = """select id,barcode,categoryid,characteristic,commission,commissiontype,to_char(ctime,'YYYY-MM-DD HH:MM'),datestart,to_char(utime,'YYYY-MM-DD HH:MM'),
                            logisticsid,minprice,name,numberfav,numbergoodreputation,numberorders,originalprice,paixu,pic,
                            recommendstatus,recommendstatusstr,shopid,status,statusstr,stores,usr_id,videoid,views,weight,pt,ptprice
                            from goods_info where usr_id=%s and COALESCE(del_flag,0)=0 """ % (self.subusr_id)
        if shopid != '' and shopid!='0':
            sql += " and shopid = %s " % shopid
        if lb_id != '':
            sql += " and categoryid = %s"% lb_id
        if recommendStatus != '':
            sql += " and recommendstatus = %s" % recommendStatus
        if nameLike != '':
            sql += " and name like  '%%%s%%'" % nameLike
        if barCode != '':
            sql += " and barcode = '%s'" % barCode
        if pingtuan != '':
            sql += "and pt = %s" % pt
        # if orderBy=='priceUp':
        #     sql += "order by  = %s" % lb_id

        l, t = self.db.select(sql)
        if t > 0:
            L = []
            for i in l:
                L.append({'barCode': i[1], 'categoryId': i[2], 'characteristic': i[3], 'commission': i[4],
                          'commissionType': i[5], 'dateAdd': i[6], 'dateStart': i[7], 'dateUpdate': i[8],
                          'id': i[0], 'logisticsId': i[9], 'minPrice': i[10], 'name': i[11], 'numberFav': i[12],
                          'numberGoodReputation': i[13], 'numberOrders': i[14], 'originalPrice': i[15],
                          'paixu': i[16], 'pic': i[17], 'recommendStatus': i[18], 'recommendStatusStr': i[19],
                          'shopId': i[20], 'status': i[21], 'statusStr': i[22], 'stores': i[23], 'userId': i[24],
                          'videoId': i[25], 'views': i[26], 'weight': i[27],'pingtuan':i[28],'ptprice':i[29]})

            return self.jsons({'code': 0, 'data': L,'msg':self.error_code['ok']})
        else:
            L = [{'name': '未添加商品信息', 'pic': '请添加商品信息', 'minPrice': 0, 'originalPrice': 0}]
            return self.jsons({'code': 404, 'data': L,'msg':self.error_code[404]})

    def goPartgoods_detail(self):#获取商品详情接口 ok

        id=self.RQ('id', '')
        if id=='' or id=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})
        sql="""select id,barcode,categoryid,characteristic,commission,commissiontype,to_char(ctime,'YYYY-MM-DD HH:MM'),datestart,to_char(utime,'YYYY-MM-DD HH:MM'),
                    logisticsid,minprice,name,numberfav,numbergoodreputation,numberorders,originalprice,paixu,pic,
                    recommendstatus,recommendstatusstr,shopid,status,statusstr,stores,usr_id,videoid,views,weight,
                    content,propertyids,hyprice,pt,ptprice
                    from goods_info where usr_id=%s and id=%s and COALESCE(del_flag,0)=0"""%(self.subusr_id,id)

        l,t=self.db.select(sql)
        if t>0:
            sqlids = "select property_child_ids from wechat_mall_goods_property_child_price where goods_id=%s" %id
            ids,ds=self.db.select(sqlids)
            L_ids=[]
            if ds>0:
                for sd in ids:
                    for dds in sd:
                        DD=dds.split(',')
                        for ss in DD:
                            L_ids.append(ss)
            if len(L_ids)>0:
                for ien in L_ids:
                    if L_ids.count(ien)>1:
                        L_ids.remove(ien)
                    if ien=='':
                        L_ids.remove(ien)
            pics=[]
            sqls = """
                   select pic from goods_pics where goods_id=%s order by id 
                    """ %id
            m, n = self.db.select(sqls)
            if n > 0:
                for e in m:
                    #pics.append('https://wxapp.janedao.cn/static/data/%s'%e[0])
                    pics.append(e[0])
            L={}

            properties = []
            for i in l:
                wlsql = "select isfree,feetype from wechat_mall_logistics where id=%s" %i[9]
                wlms="""select kuaidi,kfirstnumber,kfirstamount,kaddnumber,kaddamount,
                                ems,efirstnumber,efirstamount,eaddnumber,eaddamount 
                            from wechat_mall_transportation where logistics_id=%s
                        """%i[9]
                wl=self.db.fetch(wlsql)
                ms=self.db.fetch(wlms)
                M=[]
                if str(ms.get('kuaidi'))=='1':
                    M.append({"addAmount": ms.get('kaddamount'), "addNumber": ms.get('kaddnumber'), "firstAmount": ms.get('kfirstamount'), "firstNumber": ms.get('kfirstnumber'), "type": 0})
                if str(ms.get('ems'))=='1':
                    M.append({"addAmount": ms.get('eaddamount'), "addNumber": ms.get('eaddnumber'), "firstAmount": ms.get('efirstamount'), "firstNumber": ms.get('efirstnumber'), "type": 0})
                logistics={"isFree": wl.get('isfree'), "feeType": wl.get('feetype'), "feeTypeStr":wl.get('name'), "details": M}
                L={'barCode':i[1],'categoryId':i[2],'characteristic':i[3],'commission':i[4],
                          'commissionType':i[5],'dateAdd':i[6],'dateStart':i[7],'dateUpdate':i[8],
                          'id':i[0],'logisticsId':i[9],'minPrice':i[10],'name':i[11],'numberFav':i[12],
                         'numberGoodReputation':i[13],'numberOrders':i[14],'originalPrice':i[15],
                          'paixu':i[16],'pic':i[17],'recommendStatus':i[18],'recommendStatusStr':i[19],
                          'shopId':i[20],'status':i[21],'statusStr':i[22],'stores':i[23],'userId':i[24],
                          'videoId':i[25],'views':i[26],'weight':i[27],'propertyids':i[29],'hyprice':i[30],'pingtuan':i[31],'ptprice':i[32]}
                content=i[28]

                if i[29]!='':
                    propertyids=i[29].split(',')
                    for u in propertyids:
                        if u!='':
                            sqlp="select id,usr_id,name,paixu,to_char(ctime,'YYYY-MM-DD HH:MM') from wechat_mall_goods_property where id =%s "%u
                            s,q=self.db.select(sqlp)

                            if q>0:
                                for b in s:
                                    childsCurGoods = []
                                    bsql="select id,cname,property_id,cpaixu,remark,to_char(ctime,'YYYY-MM-DD HH:MM'),usr_id from wechat_mall_goods_property_child where property_id =%s"%b[0]
                                    ch,ds=self.db.select(bsql)

                                    if ds>0:
                                        for ur in ch:
                                            for jj in L_ids:
                                                if str(jj[0]) == str(b[0]) and str(ur[0])==str(jj[-1]):
                                                    childsCurGoods.append({'dateAdd':ur[5],'id':ur[0],'name':ur[1],'paixu':ur[3],'propertyId':ur[2],'remark':ur[4],'userId':ur[6]})
                                    properties.append( {'childsCurGoods':childsCurGoods,'dateAdd':b[4],'id':b[0],'name':b[2],'paixu':b[3],'userId':b[1]})

            sqlc="select id,usr_id,name,type,pid,key,icon,isuse,paixu,to_char(ctime,'YYYY-MM-DD HH:MM') from goods_category where usr_id=%s and  id=%s and COALESCE(del_flag,0)=0"%(self.subusr_id,i[2])
            p,o=self.db.select(sqlc)
            try:
                v=p[0]
            except:
                v=['','','','','','','','','','']
            category={'dateAdd':v[9],'icon':v[6],'id':[0],'isUse':v[7],'key':v[5],'name':v[2],
                      'paixu':v[8],'pid':v[4],'type':v[3],'userId':v[1]}
            datas={'basicInfo':L,"logistics": logistics,'pics':pics,'content':content,'category':category}
            if len(properties)>0:
                datas['properties']=properties
            return self.jsons({'code':0,'data':datas,'msg':self.error_code['ok']})
        else:
            L=[{'name':'未添加商品信息','pic':'请添加商品信息','minPrice':0,'originalPrice':0}]
            return self.jsons({'code':404, 'data':L,'msg':self.error_code[404]})

    def goPartgoods_price(self):#选择规格和尺寸获取商品价格
        goodsId = self.RQ('goodsId', '')
        propertyChildIds = self.RQ('propertyChildIds', '')
        if goodsId=='' or goodsId=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsId')})
        if propertyChildIds=='' or propertyChildIds=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('propertyChildIds')})

        sql="""select id,ggname,property_child_ids,originalpriceext,minpriceext,ptpriceext,scoreext,storesext,hypriceext 
            from wechat_mall_goods_property_child_price where goods_id =%s and property_child_ids like '%%%s%%' and usr_id=%s
            """%(goodsId,propertyChildIds,self.subusr_id)
        #print(sql)
        l,t=self.db.select(sql)

        if t==0:
            return self.jsons({'code': 404,'msg': self.error_code[404]})
        for i in l:
            L={'goodsId':goodsId,'id':i[0],'originalPrice':i[3],'pingtuanPrice':i[5],'price':i[4],
            'propertyChildIds':i[2],'score':i[6],'stores':i[7],'userId':self.subusr_id,'hypriceext':i[8]
           }
        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})



    def goPartnotice_list(self):#获取公告列表数据 ok
        type = self.RQ('type', '')
        pageSize=self.RQ('pageSize', '')
        sql="select id,usr_id,title,content,isshow,to_char(ctime,'YYYY-MM-DD HH:MM'),type from notice where COALESCE(isshow,0)=0 and  usr_id=%s and COALESCE(del_flag,0)=0"%(self.subusr_id)

        if type!='':
            sql+="and type='%s'"%type
        if pageSize!='':
            try:
                sql+="limit %s"%int(pageSize)
            except:
                pass

        l,t=self.db.select(sql)
        if t>0:
            r=t
            if pageSize != '':
                S=t//int(pageSize)
                s=t%int(pageSize)
                if s:
                    S+=1
            else:
                S=t
            L=[]
            for i in l:
                L.append({'dateAdd': i[5], 'id': i[0], 'isShow': i[4], 'title': i[2], 'userId': i[1],'type':i[6]})
            return self.jsons({'code':0,'data':{'totalRow': r, 'totalPage': S, 'dataList': L},'msg':self.error_code['ok']})
        else:
            return self.jsons({'code':404,'msg':self.error_code[404]})

    def goPartnotice_lastone(self):#获取最新的一条公告数据 OK
        type = self.RQ('type', '')

        sql="select id,usr_id,title,content,isshow,to_char(ctime,'YYYY-MM-DD HH:MM'),type from notice where COALESCE(isshow,0)=0 and  usr_id=%s and COALESCE(del_flag,0)=0"%(self.subusr_id)

        if type!='':
            sql+="and type='%s'"%type
        sql+="order by ctime desc "
        l,t=self.db.select(sql)
        if t>0:
            L=[]
            for i in l:
                L.append({'dateAdd': i[5], 'id': i[0], 'isShow': i[4], 'title': i[2], 'userId': i[1],'type':i[6]})
            return self.jsons({'code':0,'data':L,'msg':self.error_code['ok']})
        else:
            return self.jsons({'code':404,'msg':self.error_code[404]})

    def goPartnotice_detail(self):#通过id获取公告数据

        id=self.RQ('id', '')

        if id == '' or id == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})
        sql="select id,usr_id,title,content,isshow,to_char(ctime,'YYYY-MM-DD HH:MM'),type from notice where   usr_id=%s and id= %s and COALESCE(del_flag,0)=0"%(self.subusr_id,id)

        l,t=self.db.select(sql)
        if t>0:
            L={}
            for i in l:
                L={'dateAdd': i[5], 'id': i[0], 'isShow': i[4], 'title': i[2], 'userId': i[1],'content':i[3],'type':i[6]}
            return self.jsons({'code':0,'data':L,'msg':self.error_code['ok']})
        else:
            return self.jsons({'code':404,'msg':self.error_code[404]})

    def goPartorder_create(self):

        token = self.REQUEST.get('token','')
        goodsJsonStr=self.REQUEST.get('goodsJsonStr','')
        remark=self.RQ('remark','')
        provinceid=self.REQUEST.get('provinceId','')
        cityid=self.REQUEST.get('cityId','')
        districtid=self.REQUEST.get('districtId','')
        address=self.REQUEST.get('address','')
        linkman=self.REQUEST.get('linkMan','')
        mobile=self.REQUEST.get('mobile','')
        code=self.REQUEST.get('code','')
        couponid=self.REQUEST.get('couponId','')
        calculate=self.REQUEST.get('calculate','')

        if token=='' or token=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        if goodsJsonStr=='' or goodsJsonStr=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsJsonStr')})

        if provinceid=='' or provinceid=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('provinceid')})

        if cityid=='' or cityid=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('cityid')})

        if districtid == '' or districtid == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('districtid')})

        if address == '' or address == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('address')})

        if linkman == '' or linkman == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('linkman')})

        if mobile=='' or mobile=='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('mobile')})

        if code == '' or code == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('code')})

        if couponid == '' or couponid == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('couponid')})

        # if calculate == '' or calculate == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('calculate')})
        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql=" select open_id,usr_id from wechat_mall_access_token where token='%s' and usr_id =%s"%(token,self.subusr_id)
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code':10000,'msg': "token 无效，请重新登录"})


        openid=l[0][0]
        sql = " select id from wechat_mall_user where open_id='%s' and usr_id =%s" % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t==0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        mall_user_id=l[0][0]

        # 处理商品json数据
        goods_json = json.loads(goodsJsonStr)
        # province_id = int(provinceid)
        # city_id = int(cityid)
        # district_id = int(districtid)
        province_id = provinceid
        city_id = cityid
        district_id = districtid

        coupon_price,goods_price, logistics_price, total, goods_list,dR = self._handle_goods_json(goods_json, province_id, city_id, district_id,couponid)


        #dR,MSG
        # 1,self.jsons({'code': 404, 'msg': self.error_code[404]})
        # 2,self.jsons({'code': 700, 'msg': '订单中存在已下架的商品，请重新下单。'})
        # 3,库存不足请重新下单！
        #4,运费模板

        if dR==1:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        elif dR==2:
            return self.jsons({'code': 700, 'msg': '订单中存在已下架的商品，请重新下单。'})
        elif dR==3:
            return self.jsons({'code': 700, 'msg': '订单中存在库存不足商品，请重新下单！'})
        elif dR==4:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('后台没有设置运费模板')})

        timeStamp = time.time()
        timeArray = time.localtime(timeStamp)
        danhao = time.strftime("%Y%m%d%H%M%S", timeArray)
        romcode=str(time.time()).split('.')[-1]#[3:]
        order_num='B'+danhao[2:]+romcode
        number_goods=sum(map(lambda r: r['amount'], goods_list))
        goods_ids=list(set(map(lambda r: r['goods_id'], goods_list)))

        order_dict = {
            'wechat_user_id': mall_user_id,
            'linkman':linkman,
            'phone':mobile,
            'address':address,
            'postcode':code,
            'remark':remark,
            'number_goods': number_goods,
            'goods_price': goods_price,
            'logistics_price': logistics_price,
            'total': total,
            'province_id': province_id,
            'city_id': city_id,
            'district_id': district_id,
            'cid':mall_user_id,
            'ctime':self.getToday(9),
            'order_num ':order_num,
            'status':'0',
            'usr_id':self.subusr_id

        }
        if couponid!='null':
            order_dict['couponid']= couponid
            order_dict['coupon_price']= coupon_price


        if not calculate:

            self.db.insert('wechat_mall_order',order_dict)
            #order_id=self.db.insertid('wechat_mall_order_id')
            order_id=self.db.fetchcolumn("select id from wechat_mall_order where order_num='%s'"% order_num)
            for good in goods_list:
                good_dict = {
                    'order_id':order_id,
                    'order_num ': order_num,
                    'goods_id':good['goods_id'],
                    'name':good['name'],
                    'price':good['price'],
                    'pic':good['pic'],
                    'amount':good['amount'],
                    'property_str':good['property_str'],
                    'total':good['total'],
                    'cid':mall_user_id,
                    'ctime':self.getToday(9)
                    ,'usr_id':self.subusr_id
                }
                self.db.insert('wechat_mall_order_goods', good_dict)

            return self.jsons({'code': 0,
                                   'data': {'amountLogistics': logistics_price, 'score': 0, 'goodsNumber': number_goods,
                                            'isNeedLogistics': 1, 'amountTotle': total}, 'msg': 'success'})
        # amountLogistics ： 运费
        # goodsNumber ： 商品数量
        # amountTotle：商品总价（不包含运费的价格）
        # isNeedLogistics：是否需要物流信息
        return self.jsons({'code': 0,'data':{'amountLogistics': logistics_price, 'score': 0, 'goodsNumber': number_goods, 'isNeedLogistics': 1, 'amountTotle': total}, 'msg':'success'})


    def _handle_goods_json(self, goods_json, province_id, city_id, district_id,couponid):
        """
        处理订单创建请求的商品json数据，将其转换为可以直接生成'wechat_mall.order.goods'模型数据的字典，并返回商品总价和物流费用
        :param goods_json: dict
        :param province_id: 省
        :param city_id: 市
        :param district_id: 区
        :return:goods_price, logistics_price, total, goods_list,dR (dR是返回标识)
        """

        goods_price, logistics_price,dR = 0.0, 0.0,0
        goods_list = []


        for each_goods in goods_json:

            good_id=each_goods['goodsId']#商品id
            sql="select status from goods_info where id=%s"%good_id
            l,t=self.db.select(sql)
            if t ==0:
                dR=1
                return 0, 0, 0, 0, dR
            if str(l[0][0])=='1':
                dR = 2
                return 0, 0, 0, 0, dR
            good_dict=self.db.fetch("select * from goods_info where id=%s"%good_id)
            property_child_ids = each_goods['propertyChildIds']#商品规格
            amount = each_goods['number']#商品数据
            transport_type = each_goods['logisticsType']#
            inviter_id=each_goods['inviter_id']

            # each_goods_price, each_goods_total, property_str = self._count_goods_price(
            #     goods_dict[each_goods['goods_id']], amount, property_child_ids
            # )
            # each_logistics_price = self._count_logistics_price(
            #     goods_dict[each_goods['goods_id']], amount, transport_type, province_id, city_id, district_id
            # )
            each_goods_price, each_goods_total, property_str,dr = self._count_goods_price(
                good_dict, amount, property_child_ids
            )
            if dr==3:
                return 0, 0, 0, 0,dr
            each_logistics_price,rd = self._count_logistics_price(
                good_dict, amount, transport_type, province_id, city_id, district_id
            )
            if rd==4:
                return 0, 0, 0, 0,rd


            goods_list.append({
                'goods_id': good_id,
                'name': good_dict['name'],
                'pic': good_dict['pic'],
                'property_str': property_str,
                'price': each_goods_price,
                'amount': amount,
                'total': each_goods_total
            })
            goods_price += each_goods_total
            logistics_price += each_logistics_price
        coupon_price = 0
        if couponid != 'null':
            sqlc="select use_money,money,to_char(datestart,'YYYY-MM-DD'),to_char(dateend,'YYYY-MM-DD') from get_coupon where id=%s"
            l,t=self.db.select(sqlc,couponid)
            if t>0:
                if goods_price>l[0][0]:
                    if self.getToday(6)>=l[0][2] and self.getToday(6)<= l[0][3]:
                        coupon_price+=l[0][1]
        total=goods_price + logistics_price - coupon_price
        return coupon_price,goods_price, logistics_price, total, goods_list,dR

    def _count_goods_price(self, goods, amount, property_child_ids=None):
        """
        计算商品价格
        :param goods: model('wechat_mall.goods')
        :param amount: int
        :param property_child_ids: string
        :return: price, total, property_str, dR(返回标识)
        """
        property_str,dR = '',0

        if property_child_ids:
            print('_count_goods_price','property_child_ids')
            pass
            # property_child = goods.price_ids.filtered(lambda r: r.property_child_ids == property_child_ids)
            # price = property_child.price
            # property_str = property_child.name
            # total = price * amount
            # stores = property_child.stores - amount
            # if stores < 0:
            #     raise exceptions.ValidationError('库存不足请重新下单！')
            #
            # if stores == 0:
            #     # todo 发送库存空邮件
            #     pass
            #
            # property_child.sudo().write({'stores': stores})
        else:

            # if goods['minprice']>0:
            #
            #     price=goods['minprice']
            # else:
            #
            #     price = goods['originalprice']
            price = goods['minprice']
            total = price * amount

            stores = goods['stores'] - amount
            if stores < 0:
                dR=3
                return price, total, property_str,dR

            if stores == 0:
                # todo 发送库存空邮件
                pass

            #goods.sudo().write({'stores': stores})

        return price, total, property_str,dR

    def _count_logistics_price(self, goods, amount, transport_type, province_id, city_id, district_id):
        """
        计算物流费用
        :param goods: model('wechat_mall.goods')
        :param amount: int
        :param transport_type: string
        :return: price,dR(返回标识)
        """
        dR=0
        logistics_id=goods['logisticsid']
        sql="select isfree from wechat_mall_logistics where id=%s"%logistics_id
        l,t=self.db.select(sql)
        if t==0:
            return 0, 4
        if str(l[0][0])=='1':
            return 0,dR
        else:
            if str(transport_type)=='0':
                sqlt="select * from wechat_mall_transportation where  logistics_id =%s "%logistics_id
                #l,t=self.db.select(sqlt)
                return 0, dR
            else:
                return 0, dR
        # sql=""
        # # 保证运输费是最精确的地址匹配
        # transport = goods.logistics_id.district_transportation_ids.filtered(
        #     lambda r: r.default_transportation_id.transport_type == defs.TransportRequestType.attrs[transport_type]
        #               and r.province_id.id == province_id
        #               and r.city_id.id == city_id
        #               and r.district_id.id in [district_id, False]
        # ).sorted(lambda r: not r.district_id)
        #
        # if not transport:
        #     transport = goods.logistics_id.transportation_ids.filtered(
        #         lambda r: r.transport_type == defs.TransportRequestType.attrs[transport_type]
        #     )
        #
        # if not transport:
        #     return 0
        #
        # transport = transport[0]
        #
        # # 按重量计数
        # if defs.LogisticsValuationRequestType.attrs[transport_type] == defs.LogisticsValuationType.by_weight:
        #     amount = amount * goods.weight
        #
        # if amount <= transport.less_amount:
        #     return transport.less_price
        # else:
        #     if transport.increase_amount:
        #         increase_price = \
        #             int(((amount - transport.less_amount) / transport.increase_amount)) * transport.increase_price
        #     else:
        #         increase_price = 0
        #     return transport.less_price + increase_price


    def goPartorder_statistics(self):
        token = self.REQUEST.get('token', '')
        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        access_token = self.db.fetch(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if not access_token:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})

        open_id = access_token.get('open_id')
        sql = "select id from wechat_mall_user where usr_id=%s and open_id='%s'" % (self.subusr_id, open_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        mall_user_id = l[0][0]
        sql = "select count(status)status from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='0' and COALESCE(del_flag,0)=0" % (self.subusr_id, mall_user_id)
        p = self.db.fetch(sql)
        pay=p.get('status',0)

        sql = "select count(status)status from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='1' and COALESCE(del_flag,0)=0" % (
        self.subusr_id, mall_user_id)
        t = self.db.fetch(sql)
        tra = t.get('status',0)

        sql = "select count(status)status from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='2' and COALESCE(del_flag,0)=0" % (
        self.subusr_id, mall_user_id)
        c = self.db.fetch(sql)
        con = c.get('status',0)

        sql = "select count(status)status from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='3' and COALESCE(del_flag,0)=0" % (
        self.subusr_id, mall_user_id)
        s = self.db.fetch(sql)
        su = s.get('status',0)

        sql = "select count(status)status from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='4' and COALESCE(del_flag,0)=0" % (
            self.subusr_id, mall_user_id)
        r = self.db.fetch(sql)
        rep = r.get('status',0)

        sql = "select count(status)status from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='5' and COALESCE(del_flag,0)=0" % (
            self.subusr_id, mall_user_id)
        cl = self.db.fetch(sql)
        clo = cl.get('status',0)

        # 参数名          数据类型     备注
        # count_id_no_pay  int       未支付订单数0
        # count_id_no_transfer  int  待发货订单数1
        # count_id_no_confirm   int  待确认收货订单数2
        # count_id_success     int   交易完成订单数3
        # count_id_close     int     关闭的订单数5
        # count_id_no_reputation  int   待评价订单数4
        return self.jsons({'code': 0,
                           'data':{'count_id_no_pay':pay,
                                   'count_id_no_transfer':tra,
                                   'count_id_no_confirm':con,
                                   'count_id_success':su,
                                   'count_id_close':clo,
                                   'count_id_no_reputation':rep},
                           'msg': self.error_code['ok']})


    def goPartorder_list(self):

        token = self.REQUEST.get('token', '')
        status=self.RQ('status','')
        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if status == '' or status == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('orderId')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        access_token=self.db.fetch("select open_id from wechat_mall_access_token where usr_id=%s and token='%s'"%(self.subusr_id,token))
        if not access_token:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})

        open_id=access_token.get('open_id')
        sql="select id from wechat_mall_user where usr_id=%s and open_id='%s'"%(self.subusr_id,open_id)
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        mall_user_id=l[0][0]
        sql="select id,goods_price,status,logistics_price,to_char(ctime,'YYYY-MM-DD HH:MM'),to_char(utime,'YYYY-MM-DD HH:MM'),order_num,remark,usr_id,wechat_user_id,total,number_goods  from wechat_mall_order where usr_id=%s and wechat_user_id=%s and status='%s' and COALESCE(del_flag,0)=0"%(self.subusr_id,mall_user_id,status)
        L,i =self.db.select(sql)

        orderList=[]
        goodsMap={}
        if i>0:
            for o in L:
                odict = {}
                if o[2]=='0':
                    odict['statusStr']='待支付'
                elif o[2] == '1':
                    odict['statusStr'] = '已支付待发货'
                elif o[2] == '2':
                    odict['statusStr'] = '已发货待确认'
                elif o[2] == '3':
                    odict['statusStr'] = '已收货待评价'
                elif o[2] == '4':
                    odict['statusStr'] = '交易成功'

                odict['id'] = o[0]
                odict['amount']=o[1]
                odict['amountLogistics'] = o[3]
                odict['amountReal'] = o[10]
                odict['dateAdd'] = o[4]
                odict['goodsNumber'] = o[11]
                odict['orderNumber'] = o[6]
                odict['remark'] = o[7]
                odict['status'] = int(o[2])
                odict['type'] = '未知type'
                odict['uid'] = o[9]
                odict['userId'] = o[8]
                #odict['goodReputation'] = 2
                #odict['goodReputationRemark'] = '淡饭黄齑桑德环境'
                #odict['goodReputationStr'] = '好评'
                # Map={'amount':199,'goodsId':36679,'goodsName':"清欢严选商城模版",'id':85070,
                #      'number':1, 'orderId':76252,
                #      'pic':"https://cdn.it120.cc/apifactory/2018/04/02/31ea79549e46a62d179610ccb1c60f4e.png",
                #     'score': 0,'uid':312818,'userId':5078}
                A,n=self.db.select("select id,goods_id,name,amount,order_id,pic from wechat_mall_order_goods where order_num='%s' and order_id =%s"%(o[6],o[0]))
                Map={}
                if n>0:
                    for m in A:
                        Map['amount']=m[3]
                        Map['goodsId'] = m[1]
                        Map['goodsName'] = m[2]
                        Map['id'] = m[0]
                        Map['number'] = m[3]
                        Map['orderId'] = m[4]
                        Map['pic'] = m[5]
                        Map['score'] = '未知score'
                        Map['uid'] = mall_user_id
                        Map['userId'] = self.subusr_id

                goodsMap[o[0]]=[Map]
                orderList.append(odict)

        # 参数名    数据类型           备注
        # orderList   Array[Object]   订单列表数据
        # goodsMap    Map < String, Array[Object] > 每个订单对应的商品列表信息
        # logisticsMap  Map < String, Array[Object] > 每个订单对应的物流信息
        return self.jsons({'code': 0,'data':{'orderList':orderList,'goodsMap':goodsMap,'logisticsMap':''}, 'msg': self.error_code['ok']})


    def goPartorder_close(self):# 订单关闭接口
        #https://www.it120.cc/apis/44
        token = self.REQUEST.get('token', '')
        orderId = self.RQ('orderId', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if orderId == '' or orderId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})

        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sqlo="select id from wechat_mall_order where COALESCE(status,'0')='0' and id=%s and usr_id=%s and wechat_user_id=%s and and COALESCE(del_flag,0)=0"%(orderId,self.subusr_id,mall_user_id)
        sq,lo=self.db.select(sqlo)
        if lo==0:
            return self.jsons({'code': 110, 'msg': '订单状态不正常'})
        sqlu="update wechat_mall_order set status='5' where  id=%s and usr_id=%s and wechat_user_id=%s"%(orderId,self.subusr_id,mall_user_id)
        self.db.query(sqlu)
        sqld = "select id from wechat_mall_order where COALESCE(status,'0')='5' and id=%s and usr_id=%s and wechat_user_id=%s and and COALESCE(del_flag,0)=0" % (orderId, self.subusr_id, mall_user_id)
        sd, ld = self.db.select(sqld)
        if ld==0:
            return self.jsons({'code': 110, 'msg': '取消订单失败'})
        return self.jsons({'code': 0,'msg': self.error_code['ok']})


    def goPartuser_amount(self):#查询用户钱包余额
        #https://www.it120.cc/apis/87
        token = self.REQUEST.get('token', '')
        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        access_token = self.db.fetch(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if not access_token:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})

        open_id = access_token.get('open_id')
        sql = "select id,COALESCE(balance,0),COALESCE(djje,0) from wechat_mall_user where usr_id=%s and open_id='%s'" % (self.subusr_id, open_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        mall_user_id = l[0][0]
        balance=l[0][1]
        freeze=l[0][2]
        sqls="select now_amount from integral_log where usr_id=%s and wechat_user_id=%s order by id desc limit 1"%(self.subusr_id,mall_user_id)
        ll,tt=self.db.select(sqls)
        score = 0
        if tt>0:
            score=ll[0][0]

        # 参数名   数据类型   备注
        # balance   double    可用余额
        # freeze    double    冻结余额
        # score      int      积分数量
        return self.jsons({'code': 0, 'data': {'balance': balance, 'freeze': freeze, 'score': score},'msg': self.error_code['ok']})
        #return self.jsons({'code': 110, 'data': 'L', 'msg': '未处理'})


    def goPartget_pay_data(self):
        token = self.REQUEST.get('token', '')
        money=self.REQUEST.get('money','')
        remark=self.REQUEST.get('remark','')
        payName=self.REQUEST.get('payName','')#: "在线支付",
        nextAction=self.REQUEST.get('nextAction','')
        nextaction=json.loads(nextAction)


        if token=='' or token =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if money=='' or money =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('money')})
        if remark=='' or remark =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('remark')})
        if payName=='' or payName =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('payName')})
        if nextAction=='' or nextAction =='None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('nextAction')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        access_token = self.db.fetch(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if not access_token:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})


        L,T=self.db.select("select appid,secret,mchid,mchkey from mall where usr_id=%s"%self.subusr_id)
        if T==0:
            return self.jsons({'code': 10000, 'msg': '请到后台微信设置里进行设置微信APPID和secret'})
        try:
            app_id = L[0][0]
            wechat_pay_id = L[0][2]
            wechat_pay_secret = L[0][3]
        except:
            return self.jsons({'code': 10000, 'msg': '请到后台微信设置里进行设置微信APPID和secret'})


        open_id = access_token.get('open_id')
        sql = "select id from wechat_mall_user where usr_id=%s and open_id='%s'" % (self.subusr_id, open_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        try:
            mall_user_id = l[0][0]
        except:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})

        k, r = self.db.select("select order_num  from wechat_mall_order where id=%s" % nextaction['id'])
        if r == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})
        try:
            order_num = k[0][0]
        except:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})
        payment={
            'order_id': int(nextaction['id']),
            'wechat_user_id': mall_user_id,
            'price': float(money),
            'usr_id':self.subusr_id,
            'cid':mall_user_id,
            'ctime':self.getToday(9),
            'payment_number':order_num
        }
        A,a=self.db.select("select id from  wechat_mall_payment where order_id=%s and payment_number='%s'"%(int(nextaction['id']),order_num))
        if a>0:
            self.db.update('wechat_mall_payment', payment,'order_id=%s'%int(nextaction['id']))
        else:
            self.db.insert('wechat_mall_payment',payment)

        mname=self.db.fetch("select content from config_set  where key='mallName'")
        if not mname:
            mall_name='微信小程序商城'
        else:
            mall_name=mname.get('content')

        base_url='https://wxapp.janedao.cn'
        notify_url = 'https://wxapp.janedao.cn/pay/%s/notify'%self.subusr_id

        data = {
            'appid': app_id,
            'mch_id': wechat_pay_id,
            'nonce_str': get_nonce_str(),
            'body': mall_name,  # 商品描述
            'out_trade_no':order_num,  # 商户订单号
            'total_fee':int(float(money) * 100),
            #'spbill_create_ip': spbill_create_ip,
            'notify_url': notify_url,
            #'attach': '{"msg": "自定义数据"}',
            'trade_type': 'JSAPI',
            'openid': open_id,
            'timeStamp': str(int(time.time())),

        }

        wxpay = WxPay(wechat_pay_secret, **data)
        pay_info,dR,prepay_id = wxpay.get_pay_info()
        if dR==0:
            self.db.query("update wechat_mall_payment set prepay_id='%s' where payment_number='%s'"%(prepay_id,order_num))
            sql="update wechat_mall_payment set timestamp='%s',noncestr='%s',package='%s',paysign='%s',total_fee=%s where payment_number='%s'"%(pay_info['timeStamp'],pay_info['nonceStr'],pay_info['package'],pay_info['paySign'],int(float(money) * 100),order_num)
            self.db.query(sql)
            return self.jsons({'code':0,'data':pay_info})
        elif dR==2:
            sql="select id from mall where appid='%s' and mchid='%s' and usr_id = %s"%(pay_info['appid'],pay_info['mch_id'],self.subusr_id)
            l,t=self.db.select(sql)
            m,n=self.db.select("select id from wechat_mall_order where order_num='%s' and wechat_user_id=%s and usr_id=%s"%(order_num,mall_user_id,self.subusr_id))
            mn = "select id from wechat_mall_order where  order_num='%s' and usr_id=%s and wechat_user_id=%s" % (order_num, self.subusr_id,mall_user_id)
            k, v = self.db.select(mn)

            if pay_info.get('err_code')=='ORDERPAID':#订单已支付
                if t>0 and n>0 and v>0:
                    try:
                        self.db.query("update wechat_mall_order set status='1',uid=0,utime='%s' where order_num='%s'" % (self.getToday(9), order_num))
                        self.db.query("update wechat_mall_payment set status='1',uid=0,utime='%s' where payment_number='%s'" % (self.getToday(9), order_num))
                        return self.jsons({'code': 110, 'msg': pay_info.get('err_code_des')})
                    except:
                        pass
            return self.jsons({'code': 10, 'msg': pay_info.get('err_code_des')})
        return self.jsons({'code': -1, 'msg': '请求支付失败'})


    def goPartdiscounts_coupons(self):  #检索可领取优惠券
        type=self.RQ('type','')

        L=[]
        sql="""
            select id,type,pwd,needscore,refid,name,
                numbertotle,money,use_money,numberpersonmax,datestart,dateend,to_char(ctime,'YYYY-MM-DD HH:MM'),status         
            from coupon where usr_id=%s and status=0 and datestart<=current_date and current_date<=dateend and COALESCE(del_flag,0)=0
        """%self.subusr_id
        if type!='':
            sql+=" and type='%s'"%type
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 300, 'msg': self.error_code[300]})
        for e in l:
            if str(e[13])=='0':
                statusStr='正常'
            elif str(e[13]) == '1':
                statusStr='失效'
            elif str(e[13]) == '2':
                statusStr ='已过期 / 结束'
            L.append({ "id": e[0],"dateAdd": e[12],"name":e[5], "numberPersonMax": e[9],"type": e[1],
                       "numberTotle": e[6],"status": e[13],"statusStr": statusStr,'dateStart':e[10],
                       'dateEnd':e[11], "moneyHreshold": e[8], "money": e[7]
                    })

        return self.jsons({'code': 0, 'data':L,'msg': self.error_code['ok']})

    def goPartdiscounts_fetch(self): #领取优惠券接口
        token = self.REQUEST.get('token', '')
        id = self.REQUEST.get('id','')
        pwd = self.REQUEST.get('pwd','')
        detect = self.REQUEST.get('detect', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if id == '' or id == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})
        try:
            if id:
                id = int(id)
        except:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        if pwd:
            sqli="""
            select id,type,pwd,needscore,refid,name,
                numbertotle,money,use_money,numberpersonmax,datestart,dateend,to_char(ctime,'YYYY-MM-DD HH:MM'),status         
            from coupon 
            where usr_id=%s and id=%s and pwd='%s' and and COALESCE(del_flag,0)=0
        """%(self.subusr_id,id,pwd)
        else:
            sqli = """
            select id,type,pwd,needscore,refid,name,
                    numbertotle,money,use_money,numberpersonmax,datestart,dateend,to_char(ctime,'YYYY-MM-DD HH:MM'),status         
                from coupon 
                where usr_id=%s and id=%s and COALESCE(pwd,'')='' and and COALESCE(del_flag,0)=0
            """ % (self.subusr_id, id)

        s, q = self.db.select(sqli)
        if q == 0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        if str(s[0][13])!='0':
            return self.jsons({'code': 20004, 'msg': self.error_code[404]})
        so="select now_amount  from integral_log where wechat_user_id =%s and usr_id=%s order by id desc  limit 1"%(mall_user_id,self.subusr_id)
        now_amount=self.db.fetchcolumn(so)
        a=0
        if s[0][3]!='':
            a=int(s[0][3])
        if a>int(now_amount):
            return self.jsons({'code': 30001, 'msg': '您的积分不足'})

        sqlc = "select sum(amount) from get_coupon where coupon_id =%s and  usr_id=%s and and COALESCE(del_flag,0)=0" % (id, self.subusr_id)

        nsum = self.db.fetchcolumn(sqlc)
        if nsum:
            if int(s[0][6]) == int(nsum):
                return self.jsons({'code': 20001, 'msg': '来晚了'})

        L=[]
        if pwd:
            sql="""
            select id,type,pwd,needscore,refid,name,
                numbertotle,money,use_money,numberpersonmax,to_char(datestart,'YYYY-MM-DD'),to_char(dateend,'YYYY-MM-DD'),ctime,status         
            from coupon 
            where usr_id=%s and id=%s and pwd='%s'and status=0 and and COALESCE(del_flag,0)=0 --and datestart<=current_date and current_date<=dateend
        """%(self.subusr_id,id,pwd)
        else:
            sql = """
            select id,type,pwd,needscore,refid,name,
                    numbertotle,money,use_money,numberpersonmax,
                    to_char(datestart,'YYYY-MM-DD'),to_char(dateend,'YYYY-MM-DD'),ctime,status         
                from coupon 
                where usr_id=%s and id=%s and COALESCE(pwd,'0')='0' and status=0 and and COALESCE(del_flag,0)=0 --and datestart<=current_date and current_date<=dateend
            """ % (self.subusr_id, id)

        o,p=self.db.select(sql)
        if p==0:
            return self.jsons({'code': 20004, 'msg': '已过期~'})
        if o[0][11]!='':
            if o[0][11]<self.getToday(6):
                return self.jsons({'code': 20004, 'msg': '已过期~'})
        for e in o:

            if str(e[13])=='0':
                statusStr='正常'
            elif str(e[13]) == '1':
                statusStr='失效'
            elif str(e[13]) == '2':
                statusStr ='已过期 / 结束'
            L.append({ "id": e[0],"dateAdd": e[12],"name":e[5], "numberPersonMax": e[9],"type": e[1],
                       "numberTotle": e[6],"status": e[13],"statusStr": statusStr,'dateStart':e[10],
                       'dateEnd':e[11], "moneyHreshold": e[8], "money": e[7]
                    })
        numberPersonMax = o[0][9]
        cq="select sum(amount) from get_coupon where coupon_id =%s and wechat_user_id =%s and usr_id=%s "%(id,mall_user_id,self.subusr_id)

        d,h=self.db.select(cq)

        if h>0 :
            if d[0][0]=='':
                if detect=='true':
                    return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
                self.db.query(
                    "insert into get_coupon(usr_id,wechat_user_id,coupon_id,amount,status,cid,ctime)values(%s,%s,%s,%s,%s,%s,now())" % (
                    self.subusr_id, mall_user_id, id, 1, 0, mall_user_id))
                return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
            if d[0][0]!='':
                if d[0][0]<numberPersonMax:
                    if detect == 'true':
                        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
                    self.db.query("insert into get_coupon(usr_id,wechat_user_id,coupon_id,amount,status,cid,ctime)values(%s,%s,%s,%s,%s,%s,now())"%(self.subusr_id,mall_user_id,id,1,0,mall_user_id))
                    return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
        return self.jsons({'code': 20003, 'data': L, 'msg': '你领过了，别贪心哦~'})

    def goPartdiscounts_my(self):# 我的优惠券
        #https://www.it120.cc/apis/72
        token = self.REQUEST.get('token', '')
        status = self.RQ('status','')
        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        try:
            if status:
                status = int(status)
        except:
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('status')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sqlco="select coupon_id from get_coupon where wechat_user_id=%s and usr_id=%s "%(mall_user_id,self.subusr_id)
        if status!='':
            sqlco+=" and status=%s"%status
        ll,tt=self.db.select(sqlco)
        if tt==0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})


        sql = """
            select gc.id,gc.amount,gc.status as gcstatus ,c.name,
                    c.numbertotle,c.money,c.use_money,c.numberpersonmax,
                    to_char(c.datestart,'YYYY-MM-DD HH:MM:SS' ),
                    to_char(c.dateend,'YYYY-MM-DD HH:MM:SS' ) ,
                    c.status,to_char(c.ctime,'YYYY-MM-DD HH:MM'),
                    gc.coupon_id 
                from get_coupon gc 
                left join coupon c on c.id=gc.coupon_id
                where COALESCE(c.status,0)=0 and COALESCE(c.del_flag,0)=0  
               and  gc.usr_id=%s and gc.wechat_user_id=%s
            """ % (self.subusr_id, mall_user_id)
        if status:
            sql += "and  COALESCE(gc.status,0)=%s" % status
        o, p = self.db.select(sql)
        if p == 0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        L = []

        for e in o:

            if str(e[10]) == '0':
                statusStr = '正常'
            elif str(e[10]) == '1':
                statusStr = '失效'
            elif str(e[10]) == '2':
                statusStr = '已过期 / 结束'
            if str(e[2]) == '0':
                gcstatusStr = '未使用'
            elif str(e[2]) == '1':
                gcstatusStr = '已使用'
            elif str(e[2]) == '2':
                gcstatusStr = '已过期'

            L.append({"id": e[0], "dateAdd": e[11], "name": e[3], "numberPersonMax": e[7],
                      "numberTotle": e[4], "status": e[10], "statusStr": statusStr, 'dateStart': e[8],
                      'dateEnd': e[9], "moneyHreshold": e[6], "money": e[5], 'gcstatus': e[2],
                      'gcstatusStr': gcstatusStr,'coupon_id':e[12]
                      })

        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})



    def goParttoday_signed(self):  #今日是否签到
        #https://www.it120.cc/apis/88
        token = self.REQUEST.get('token', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sql="select id,wechat_user_id,to_char(ctime,'YYYY-MM-DD HH:MM'),counts from signin_log where wechat_user_id =%s and ctime='%s' and usr_id=%s"%(mall_user_id,self.getToday(6),self.subusr_id)
        ll,tt=self.db.select(sql)
        if tt>0:
            return self.jsons({'code': 0, 'data': {"continuous":ll[0][3],
                                                    "dateAdd": ll[0][2],
                                                   "id": ll[0][0],
                                                   "uid": ll[0][1]}, 'msg': self.error_code['ok']})

        return self.jsons({'code': 700, 'data': {"continuous": 0}, 'msg': self.error_code[700]})

    def goPartscore_sign(self): #签到
        token = self.REQUEST.get('token', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sql = "select id,wechat_user_id,to_char(ctime,'YYYY-MM-DD HH:MM'),counts from signin_log where wechat_user_id =%s and ctime='%s' and usr_id=%s" % (mall_user_id, self.getToday(6),self.subusr_id)
        ll, tt = self.db.select(sql)
        if tt == 0:
            today = datetime.date.today()
            yd = today + datetime.timedelta(days=-1)
            sqlc="select id,wechat_user_id,to_char(ctime,'YYYY-MM-DD HH:MM'),counts from signin_log where wechat_user_id =%s and ctime='%s' and usr_id=%s" % (mall_user_id, yd,self.subusr_id)
            mm,nn =self.db.select(sqlc)
            counts=0
            if nn>0:
                counts=mm[0][3]+1

            sqls="insert into signin_log(usr_id,wechat_user_id,cid,ctime,counts)values(%s,%s,%s,'%s',%s)"%(self.subusr_id,mall_user_id, mall_user_id, self.getToday(6),counts)
            self.db.query(sqls)
        ll, tt = self.db.select(sql)
        if tt>0:
            return self.jsons({'code': 0, 'data': {"continuous": ll[0][3],
                                                   "dateAdd": ll[0][2],
                                                   "id": ll[0][0],
                                                   "uid": ll[0][1]}, 'msg': self.error_code['ok']})
        return self.jsons({'code': 700, 'msg': '签到失败'})

    def goPartsign_logs(self):  #查询签到记录
        token = self.REQUEST.get('token', '')
        dateaddbegin =self.RQ('dateaddbegin','')
        dateaddend =self.RQ('dateaddend','')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if dateaddbegin == '' or dateaddbegin == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('dateaddbegin')})
        if dateaddend == '' or dateaddend == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('dateaddend')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sql = "select id,wechat_user_id,to_char(ctime,'YYYY-MM-DD HH:MM'),counts from signin_log where wechat_user_id =%s and ctime>='%s' and ctime<='%s' and usr_id=%s limit 50" % (
        mall_user_id, dateaddbegin,dateaddend,self.subusr_id)
        ll, tt = self.db.select(sql)
        L=[]
        if tt==0:
            return self.jsons({'code': 404, 'msg': self.error_code[404]})
        for i in ll:
            L.append({"continuous": i[3],"dateAdd":i[2],"id": i[0],"uid": i[1]})
        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})


        #return self.jsons({'code': 700, 'data': 'L', 'msg': self.error_code[700]})


    def goPartscore_logs(self):  #积分明细记录
        #https://www.it120.cc/apis/103
        token = self.REQUEST.get('token', '')
        type = self.RQ('type','')
        behavior = self.RQ('behavior','')
        remark = self.RQ('remark','')
        dateaddbegin = self.RQ('dateAddBegin','')
        dateaddend = self.RQ('dateAddEnd','')
        pageSize = self.RQ('pageSize','')
        # token  String  登录接口返回的登录凭证  Y
        # type   int类型 0注册 1邀请好友 2每日签到 3兑换优惠券 4管理员调整 5充值送 6消费返 X
        # behavior  int  收支方式 0收入 1支出  X
        # remark  String  备注关键词搜索   X
        # dateAddBegin  String  起始时间筛选，2017 - 11 - 22  X
        # dateAddEnd  String    截止时间筛选，2017 - 11 - 22  X
        # page  int  获取第几页数据，不传默认为1  X
        # pageSize  int   每页显示多少条数据，不传默认为50

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        # if type == '' or type == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('type')})
        # if behavior == '' or behavior == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('behavior')})
        # if remark == '' or remark == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('remark')})
        # if dateaddbegin == '' or dateaddbegin == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('dateaddbegin')})
        # if dateaddend == '' or dateaddend == 'None':
        #     return self.jsons({'code': 300, 'msg': self.error_code[300].format('dateaddend')})
        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sqlg="select type,typestr,in_out,inoutstr,to_char(ctime,'YYYY-MM-DD HH:MM'),memo,amount,now_amount from integral_log where usr_id=%s and wechat_user_id =%s "%(self.subusr_id,mall_user_id)
        if type!='':
            sqlg+="and type =%s"%type
        if behavior!='':
            sqlg+="and in_out =%s"%behavior
        if remark!='':
            sqlg+="and memo like '%%%s%%'"%remark
        if dateaddbegin!='':
            sql+=" and ctime>'%s'"%dateaddbegin
        if dateaddend!='':
            sql+=" and ctime < '%s'"%dateaddend
        ll,tt=self.db.select(sqlg)
        if tt==0:
            return self.jsons({'code': 400, 'msg': self.error_code[404]})
        result=[]
        for li in ll:
            result.append({"behavior": li[2],"behaviorStr": li[3],"dateAdd": li[4],"remark": li[5]
                    ,"score": li[6],"scoreLeft": li[7],"type": li[0],"typeStr": li[1]})

        return self.jsons({'code': 0, 'data':{'result':result,'totalRow':tt,'totalPage':0}, 'msg': self.error_code['ok']})
        #return self.jsons({'code': 110, 'data': 'L', 'msg': '未处理'})


    def goPartsend_rule(self):  #获取积分赠送规则
        #https://www.it120.cc/apis/112
        #token = self.REQUEST.get('token', '')
        code = self.RQ('code', '')

        sql="select s.code,s.confine,s.score,m.txt1 from score_send s left join mtc_t m on m.id=s.code and m.type='ZFZSGZ' where s.usr_id=%s and COALESCE(s.del_flag,0)=0"%self.subusr_id
        if code!='':
            sql+=" and code ='%s'"%code
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 0, 'msg': '未找到积分赠送规则'})
        L = []
        for i in l:
            L.append( {"code": i[0],"codeStr":i[3],"confine": i[1],"score": i[2]})

        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})


    def goPartorder_detail(self):#商城订单详情接口
        #https://www.it120.cc/apis/42
        # 参数名   数据类型   备注
        # orderInfo  Object  订单详细信息
        # goods  Array[Object]  该订单的所有商品列表
        # logs  Array[Object]   该订单的日志记录信息
        # logistics   Object  该订单的物流信息
        #wechat_mall_order 订单表 wechat_mall_order_goods订单商品明细  wechat_mall_payment支付记录
        token = self.REQUEST.get('token', '')
        id = self.RQ('id', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if id == '' or id == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sqlo="select id,order_num,number_goods,goods_price,logistics_price,total,remark,to_char(ctime,'YYYY-MM-DD HH:MM'),to_char(utime,'YYYY-MM-DD HH:MM'),status from wechat_mall_order where id=%s and usr_id=%s and wechat_user_id=%s and and COALESCE(del_flag,0)=0"%(id,self.subusr_id,mall_user_id)
        sq,lo=self.db.select(sqlo)
        orderInfo={}
        if lo==0:
            return self.jsons({'code': 110, 'data': {}, 'msg': '订单不存在/订单id有误'})
        for qs in sq:
            orderInfo = {"amount": qs[3], "amountLogistics": qs[4], "amountReal": qs[5], "dateAdd": qs[7],
                         "dateUpdate": qs[8], "goodsNumber": qs[2], "id":qs[0], "orderNumber": qs[1],
                         "remark": qs[6], "status": qs[9], "uid": mall_user_id,"userId": self.subusr_id}
                # orderInfo={"amount":qs[2],"amountLogistics": qs[3],"amountReal": qs[1],"dateAdd": qs[6],
                #     "dateUpdate": qs[7],"goodReputation": 2,"goodReputationRemark": "淡饭黄齑桑德环境",
                #     "goodReputationStr": "好评","goodsNumber": qs[4],"id": 13,"orderNumber": qs[0],
                #     "remark": qs[5],"status": qs[8],"statusStr": "交易成功","type": 0,"uid": mall_user_id,"userId": self.subusr_id}

        sqlg="select id,order_id,goods_id,name,price,amount,property_str,total from wechat_mall_order_goods where usr_id=%s and order_id=%s"%(self.subusr_id,id)
        sg,ig=self.db.select(sqlg)
        goods=[]
        if ig >0:
            for gi in sg:
                goods.append({"amount": gi[4], "goodsId": gi[2], "goodsName": gi[3], "id": gi[0], "number": gi[5], "orderId": gi[1], "property":gi[7]})

        # goods=[
        #     {"amount": 1998,"goodsId": 11,"goodsName": "无物流无规格商品测试","id": 17,"number": 2,"orderId": 13},
        #     {"amount": 750,"goodsId": 8,"goodsName": "Mac 2016新款","id": 18,"number": 3,"orderId": 13, "property": "内存容量:256G"}
        #     ]

        sqll="select id,usr_id,orderid,status,status_str,del_flag,remark,cid,to_char(ctime,'YYYY-MM-DD HH:MM') from order_los where usr_id=%s and orderid=%s"%(self.subusr_id,id)
        ll,tt=self.db.select(sqll)
        logs=[]
        if tt>0:
            for il in ll:
                logs.append({"dateAdd": il[8], "id": il[0], "orderId": il[2], "type": il[3], "typeStr": il[4]}),

        # logs=[{"dateAdd": "2017-03-29 09:16:11","id": 17,"orderId": 13,"type": 0,"typeStr": "下单"},
        #         {"dateAdd": "2017-03-29 09:38:26","id": 18,"orderId": 13,"type": 5,"typeStr": "卖家修改价格"}
        #       ]
        #

        logistics={"address": "详细地址","cityId": 330100,"code": "310009","dateUpdate": "2017-03-29 16:55:02",
                    "districtId": 330108,"id": 13,"linkMan": "张飞","mobile": "13500000001","provinceId": 330000,
                    "shipperCode": "SF","shipperName": "顺丰快递","status": 3,
                    "traces": [{"AcceptStation":"顺丰速运 已收取快件","AcceptTime":"2017-03-23 16:57:44","Remark":""},
                    {"AcceptStation":"快件在【阜阳颍泉区汽车北站营业点】已装车，准备发往 【阜阳开发区集散中心】","AcceptTime":"2017-03-23 17:21:05","Remark":""}
                               ]
                      ,"trackingNumber": "974259022676"}

        L={'orderInfo':orderInfo,'goods':goods,'logs':logs,'logistics':''}
        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
        #return self.jsons({'code': 110, 'data': '未处理', 'msg': '未处理'})




    def goPartorder_delivery(self):#确认收货接口
        #https://www.it120.cc/apis/45
        token = self.REQUEST.get('token', '')
        orderId = self.RQ('orderId', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if orderId == '' or orderId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('id')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})


        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]
        sqls="selecct id from wechat_mall_order where wechat_user_id=%s and usr_id=%s and id=%s and status=2 and and COALESCE(del_flag,0)=0"%(mall_user_id,self.subusr_id,orderId)
        ll,tt=self.db.select(sqls)
        if tt==0:
            return self.jsons({'code': 404, 'msg': '订单状态异常'})
        self.db.query("update wechat_mall_order set status=3 where wechat_user_id=%s and usr_id=%s and id=%s"%(mall_user_id,self.subusr_id,orderId))
        sqlu = "selecct id from wechat_mall_order where wechat_user_id=%s and usr_id=%s and id=%s and status=3"%(mall_user_id, self.subusr_id, orderId)
        su,st=self.db.select(sqlu)
        if st==0:
            return self.jsons({'code': 110, 'msg': '确认收货失败，请重试'})
        return self.jsons({'code': 0,'msg': self.error_code['ok']})



    def goPartorder_reputation(self):# 商品评价接口
        #https://www.it120.cc/apis/46

        postJsonString = self.REQUEST.get('postJsonString', '')
        # 处理商品json数据
        postjson = json.loads(postJsonString)
        token = postjson.get('token','')
        orderId = postjson.get('orderId','')
        reputations = postjson.get('reputations','')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if orderId == '' or orderId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('orderId')})
        if reputations == '' or reputations == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('reputations')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})

        mall_user_id = m[0][0]

        for pjdict in reputations:
            goodid=pjdict['id']
            pj=pjdict['reputation']
            remark=pjdict['remark']
            sql = "select id from pingjia_list where usr_id=%s and cid=%s and orderid=%s and goodid=%s"%(self.subusr_id,mall_user_id,orderId,goodid)
            ll,tt=self.db.select(sql)
            if tt==0:
                self.db.query("insert into pingjia_list(usr_id,orderid,goodid,pj,remark,cid,ctime)values(%s,%s,%s,%s,'%s',%s,now())"%(self.subusr_id,orderId,goodid,pj,remark,mall_user_id))
            else:
                self.db.query("update pingjia_list set pj=%s,remark='%s',uid=%s,utime=now() where id=%s"%(pj,remark,mall_user_id,ll[0][0]))

        return self.jsons({'code': 0,'msg': self.error_code['ok']})
        # reputations: [
        #     {
        #         id: "订单归属的商品列表数据的id字段",
        #         reputation: "0 差评 1 中评 2 好评",
        #         remark: "评价备注，限200字符"
        #     },
        #     {
        #         id: "订单归属的商品列表数据的id字段",
        #         reputation: "0 差评 1 中评 2 好评",
        #         remark: "评价备注，限200字符"
        #     }
        # ]
        #return self.jsons({'code': 110, 'data': '未处理', 'msg': '未处理'})


    def goPartgoods_reputation(self):#获取商品评价数据
        #https://www.it120.cc/apis/78
        # goodsId  int  商品编号数字id  Y
        # page  int  获取第几页数据，不传默认为1  X
        # pageSize  int  每页显示多少条数据，不传默认50  X

        goodsId = self.RQ('goodsId', '')
        pageSize = self.RQ('pageSize', '')
        if goodsId == '' or goodsId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('goodsId')})

        #返回参数说明:
        #参数名     数据类型    备注
        #goodsName   String    商品名称
        #number       int      购买数量
        #orderId      int      订单的数字id，便于做订单详情的跳转
        #pic         String    商品主图图片
        #avatarUrl    String    用户头像
        #goodReputation  int   0差评1中评2好评
        #goodReputationRemark   String   用户评价备注
        #dateReputation   Datetime  评价时间
        #return self.jsons({'code': 0, 'data': L})
        #return self.jsons({'code': 1, 'msg': '没有数据'})
        sql="""
            select gi.name,gi.amount,pl.orderid,gi.pic,pl.pj,pl.remark,to_char(pl.ctime,'YYYY-MM-DD HH:MM'),w.avatar_url 
            from pingjia_list pl 
            left join wechat_mall_order_goods gi on gi.goods_id =pl.goodid and pl.usr_id=gi.usr_id 
            left join wechat_mall_user w on w.id=pl.cid and w.usr_id=pl.usr_id
            where pl.usr_id=%s and pl.goodid=%s
        """%(self.subusr_id,goodsId)
        l,t=self.db.select(sql)
        L=[]
        if t==0:
            return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
        for i in l:
            L.append({"goodsName": i[0], "number": i[1],"orderId": i[2],'pic':i[3],
                      "avatarUrl": i[7],
                      'goodReputation':i[4],'goodReputationRemark':i[5],'dateReputation':i[6]
                      })

        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})

    def goPartsign_rules(self):  #获取签到赠送积分规则
        #https://www.it120.cc/apis/120
        sql="select continuous,score from score_set where COALESCE(del_flag,0)=0 and usr_id =%s"%self.subusr_id
        l,t=self.db.select(sql)
        if t==0:
            return self.jsons({'code': 0, 'msg': '未找到签到赠送积分规则'})
        L=[]
        for i in l:
            L.append({"continuous": i[0],"score": i[1]})
        return self.jsons({'code': 0, 'data': L, 'msg': self.error_code['ok']})
        #return self.jsons({'code': 110, 'data': 'L', 'msg': '未处理'})


    def goPartorder_pay(self):  # 用户钱包支付订单
        # https://www.it120.cc/apis/81
        token = self.REQUEST.get('token', '')
        orderId = self.REQUEST.get('orderId','')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if orderId == '' or orderId == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('orderId')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        access_token = self.db.fetch(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if not access_token:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        open_id = access_token.get('open_id')
        sql = "select id,balance from wechat_mall_user where usr_id=%s and open_id='%s'" % (self.subusr_id, open_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        mall_user_id = l[0][0]
        balance = l[0][1]

        # return self.jsons({'code': 0,'msg': self.error_code['ok']})
        return self.jsons({'code': 110, 'msg': '暂时不支持钱包付款！'})

    def goPartprice_freight(self):#获取物流费用接口
        #https://www.it120.cc/apis/40
        #templateId  int  运费模板编号，可通过商品列表、商品详情接口获取  Y
        #type int  快递方式：0 快递 1 EMS  2  平邮 Y
        #provinceId int 用户省份编号  X
        #cityId  int  用户城市编号  X
        #districtId  int  用户区县编号  X
        return self.jsons({'code': 110, 'data': 'L', 'msg': '未处理'})

    def goPartvideo_detail(self):  # 获取视频详情
        # https://www.it120.cc/apis/101

        videoId = self.RQ('videoId', '')

        #返回参数说明:
        #参数名    数据类型    备注
        #coverUrl   String    视频截图封面
        #title      String    视频名称
        #size       int       视频容量
        #fdMp4      String    流畅Mp4
        #fdM3u8     String    流畅M3u8
        #ldMp4      String    标清Mp4
        #ldM3u8     String    标清M3u8
        return self.jsons({'code': 110, 'data': '未处理', 'msg': '未处理'})


    def goPartorder_hybuy(self):#创建会员订单
        token = self.REQUEST.get('token', '')
        money = self.RQ('money','')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})

        if money == '' or money == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('money')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})

        sql = " select open_id,usr_id from wechat_mall_access_token where token='%s' and usr_id =%s" % (
        token, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 10000, 'msg': "token 无效，请重新登录"})
        openid = l[0][0]
        sql = " select id from wechat_mall_user where open_id='%s' and usr_id =%s" % (openid, self.subusr_id)
        l, t = self.db.select(sql)
        if t == 0:
            return self.jsons({'code': 10000, 'msg': self.error_code[10000]})
        mall_user_id = l[0][0]

        timeStamp = time.time()
        timeArray = time.localtime(timeStamp)
        danhao = time.strftime("%Y%m%d%H%M%S", timeArray)
        romcode = str(time.time()).split('.')[-1]  # [3:]
        order_num = 'HY' + danhao[2:] + romcode[3:]


        order_dict = {
            'wechat_user_id': mall_user_id,
            'remark': '开通会员',
            'number_goods': 1,
            'goods_price': money,
            'logistics_price': 0,
            'total': money,
            'type':3,
            'province_id': 0,
            'city_id': 0,
            'district_id': 0,
            'cid': mall_user_id,
            'ctime': self.getToday(9),
            'order_num ': order_num,
            'status': '0',
            'usr_id': self.subusr_id
        }

        try:
            self.db.insert('wechat_mall_order', order_dict)
        except:
            pass

        ll,tt = self.db.select("select id,total from wechat_mall_order where order_num='%s'" % order_num)
        if tt==0:
            return self.jsons({'code': 110, 'msg': '开通会员失败'})

        return self.jsons({'code': 0,
                           'data': {'money': ll[0][1], 'orderId': ll[0][0], 'uid': mall_user_id},
                           'msg': 'success'})



    def goPartuser_feedback(self):# 用户反馈
        token = self.REQUEST.get('token', '')
        title = self.RQ('title', '')
        question = self.RQ('question', '')
        e_mail = self.RQ('e_mail', '')
        mobil = self.RQ('mobil', '')

        if token == '' or token == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('token')})
        if title == '' or title == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('title')})
        if question == '' or question == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('question')})
        if e_mail == '' or e_mail == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('e_mail')})
        if mobil == '' or question == 'None':
            return self.jsons({'code': 300, 'msg': self.error_code[300].format('mobil')})

        dR = self.check_token(token)
        if dR['code'] != 0:
            return self.jsons({'code': 901, 'msg': dR['MSG']})


        l, t = self.db.select(
            "select open_id from wechat_mall_access_token where usr_id=%s and token='%s'" % (self.subusr_id, token))
        if t == 0:
            return self.jsons({'code': 901, 'msg': self.error_code[901]})
        openid = l[0][0]
        sql = "select id from wechat_mall_user where open_id='%s' and usr_id=%s " % (openid, self.subusr_id)
        m, n = self.db.select(sql)
        if n == 0:
            return self.jsons({'code': 700, 'msg': self.error_code[700]})
        mall_user_id = m[0][0]


    # def goPartorder_close(self):# 未知接口
    #
    #     pass
    #
    # def goPartorder_close(self):# 未知接口
    #
    #     pass




