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

if DEBUG == '1':    
    import admin.dl.BASE_DL
    reload(admin.dl.BASE_DL)
from admin.dl.BASE_DL  import cBASE_DL


import hashlib , os , time , random

class cA001_dl(cBASE_DL):
    def init_data(self):
        self.GNL=['','店铺名称','店铺简介','店铺logo','店铺地址','添加时间','修改时间'] #列表表头


    #在子类中重新定义         
    def myInit(self):
        self.src = 'A001'
        pass

    def mRight(self):
            
        sql = u"""
            select 
              id
              --,type
              --,provinceid  
              ,name 
              ,introduce
               ,pic 
              ,address 
              --,linkphone
             
              --,numberorder 
              --,numberoodreputation  
             -- ,status 
             
              ,ctime
             
              ,utime
              
            from shopname 
            where  COALESCE(del_flag,0)!=1 and usr_id=%s
        """%self.usr_id

        
        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
            select 
              id
              ,type
              ,number
              ,expresstype
              ,provinceid
              ,cityid
              ,districtid
              ,name
              ,address
              ,linkphone
              ,introduce
              ,characteristic
              ,mapaddresssearch
              ,paixu
              ,status
              ,activity
              ,latitude
              ,longitude
              ,numberorder
              ,numberoodreputation
              ,pic
              ,cid
              ,ctime
              ,uid
              ,utime
              
            from shopname
            where id=%s
           
        """ % pk
        if pk != '':
            L = self.db.fetch( sql )
        # else:
        #     timeStamp = time.time()
        #     timeArray = time.localtime(timeStamp)
        #     danhao = time.strftime("%Y%m%d%H%M%S", timeArray)
        #
        #     #L['danhao']='cgdd'+danhao
        #     L['danhao'] = ''
        return L
    
    def local_add_save(self):
        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        """
        
        #这些是操作权限
        dR={'R':'','MSG':'申请单 保存成功','B':'1','isadd':'','furl':''}  
        pk = self.pk
        #dR={'R':'','MSG':'','isadd':''}
        dR={'R':'','MSG':''}

        
        
        #获取表单参数
        # type=self.GP('type')#店铺类型
        # number=self.GP('number')#门店编号
        # expresstype=self.GP('expresstype')#生鲜配送
        # provinceid=self.GP('provinceid')#地址省
        # cityid=self.GP('cityid')#地址市
        # districtid=self.GP('districtid')#地址区县
        name=self.GP('name','')#店铺名称
        address = self.GP('address','')  # 地址
        #linkphone=self.GP('linkphone','')#联系电话
        introduce=self.GP('introduce','')#店铺介绍
        # characteristic=self.GP('characteristic')#店铺特色
        # mapaddresssearch=self.GP('mapaddresssearch')#地图位置
        # paixu=self.GP('paixu') or 0 #排序
        # status=self.GP('status')#状态
        # activity=self.GP('activity')#打折信息
        # latitude=self.GP('latitude')#后台标注的商家地图纬度坐标
        # longitude=self.GP('longitude')#后台标注的商家地图经度坐标
        # numberorder=self.GP('numberorder')#成交数量
        # numberoodreputation=self.GP('numberoodreputation')#好评数


        # from werkzeug import secure_filename
        # try:
        #     file = self.objHandle.files['pic']
        #     if file:
        #         #filename = secure_filename(file.filename)
        #         ext = secure_filename(file.filename).split('.')[-1]
        #         timeStamp = time.time()
        #         md5name = hashlib.md5()
        #         md5name.update(str(timeStamp).encode('utf-8'))
        #         filename = md5name.hexdigest() + '.' + ext
        #         pic = filename
        #         file.save(os.path.join(public.ATTACH_ROOT, filename))
        # except:
        pic = self.GP('picUrl','')  # 图标

        
        data = {
                # 'type':type
                # ,'number':number
                # ,'expresstype':expresstype
                # ,'provinceid':provinceid
                # ,'cityid':cityid
                # ,'districtid':districtid,
                'name':name
                ,'address':address
                #,'linkphone':linkphone
                ,'introduce':introduce
                # ,'characteristic':characteristic
                # ,'mapaddresssearch':mapaddresssearch
                # ,'paixu':paixu
                # ,'status':status
                # ,'activity':activity
                # ,'latitude':latitude
                # ,'longitude':longitude
                # ,'numberorder':numberorder
                # ,'numberoodreputation':numberoodreputation
                ,'pic':pic
                ,'cid': self.usr_id
                ,'ctime': self.getToday(6)
                ,'uid': self.usr_id
                ,'utime': self.getToday(6)
                ,'usr_id':self.usr_id
        }

        # for k in list(data):
        #     if data[k] == '':
        #         data.pop(k)
        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('shopname' , data , " id = %s " % pk)
            
        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')
            
            self.db.insert('shopname' , data)
            #pk = self.db.insertid('shopname_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        dR['pk'] = pk
        
        return dR

    def getmtcdata(self,type,df='',title='请选择'):
        if title!='':L=[['',title,'']]
        else:L=[]
        if type!='':
            sql="select id,txt1 from mtc_t where type='%s' order by sort"%type
            lT,iN=self.db.select(sql)
            if iN>0:
                for e in list(lT):
                    id,txt=e
                    b = ''
                    if str(df) == str(id):
                        b = ' selected="selected"'
                    L.append([id,txt,b])
        return L

    def get_provinceid_data(self):
        L=[['','--请选择--']]
        sql="select code,cname from province"
        lT,iN=self.db.select(sql)
        if iN>0:
            for r in lT:
                L.append(r)
        return L

    def get_cityid_data(self,pcode=''):
        if pcode=='':
            lT=[['','--请选择--']]
            return lT
        sql="select code,cname from city where parent_code ='%s' " %pcode
        lT,iN=self.db.select(sql)
        return lT

    def get_areaid_data(self,pcode=''):
        if pcode=='' :
            lT=[['','--请选择--']]
            return lT
        sql="select code,cname from area where  parent_code='%s' " %pcode
        lT,iN=self.db.select(sql)
        return lT

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update shopname set del_flag=1 where id= %s" % pk)
        return dR