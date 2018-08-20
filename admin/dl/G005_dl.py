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

class cG005_dl(cBASE_DL):
    def init_data(self):

        #以字典形式创建列表上要显示的字段 
        #以下字典为列表逻辑所用 , 所有数组元素的位置必须对应好
        #[列表名,查询用别名,表格宽度,对齐]
        self.FDT=[
            ['',      "u.usr_id",             '',''],#0
            ['分类',      "u.usr_name",           '',''],#1
            ['标题', "u.usr_name", '', ''],  # 2
            ['排序',      "u.login_id",      '',''],#3
            ['创建时间',      "r.role_name",'',''],#4
            ['更新时间',        "d.cname",     '',''],#5
            #['添加时间',      "u1.usr_name",'',''],#6
            #['更新时间',    "u.ctime",               '',''],#7
            #['添加时间',  "u2.usr_name",'',''],#8
            #['修改时间',"u.utime",               '',''],#9
            #['进货时间',      "u.last_login",'',''],#10
            #['备注',    "u.last_ip",               '','']#11
            
        ]
        #self.GNL=[] #列表上出现的
        #self.SNL=[]     #排序
        #self.QNL=''  #where查询
        self.GNL = self.parse_GNL([0,1,2,3,4,5])
        self.SNL = self.parse_SNL([0])
        self.QNL = self.parse_QNL([1])

    #在子类中重新定义         
    def myInit(self):
        self.src = 'G005'
        pass

    def mRight(self):
            
        sql = u"""
            select h.id
                ,m.txt1
                ,h.title
                ,h.sort
                ,h.ctime
                ,h.utime
            from help_doc h
            left join mtc_t m on m.id=h.type and m.type='HELPDOC'
            where 1=1
        """
        self.qqid = self.GP('qqid','')
        self.type = self.GP('type','')
        # self.orderbydir = self.GP('orderbydir','')
        # self.pageNo=self.GP('pageNo','')
        # if self.pageNo=='':self.pageNo='1'
        if self.qqid!='' and len(self.QNL) > 0:
            sql+= "and h.title LIKE '%%%s%%' "%(self.qqid)
        if self.type!='':
            sql+=" and  h.type=%s"%self.type
        # #ORDER BY
        # if self.orderby!='':
        #     sql+=' ORDER BY %s %s' % (self.orderby,self.orderbydir)
        # else:
        sql+=" ORDER BY h.sort "
        
        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
            select id
                ,type
                ,title
               ,sort
                ,content
            from help_doc  
            where  id=%s
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
        save_flag = self.REQUEST.get("save_flag").strip()
        save_flag2 = self.cookie.getcookie("__flag")
        
        
        #获取表单参数
        type=self.GP('type')#分类
        title=self.GP('title')#标题

        sort=self.GP('sort')#排序
        container = self.GP('container')  # 内容



        # if not (save_flag == save_flag2):
        #     #为FALSE时,当前请求为重刷新
        #     return dR
        
        # if danhao == '':
        #     dR['R'] = '1'
        #     dR['MSG'] = '请输入角色名字'
        
        data = {
                'type':type
                ,'title':title
                ,'content':container
                ,'sort':sort
                ,'cid': self.usr_id
                ,'ctime': self.getToday(9)
                ,'uid': self.usr_id
                ,'utime': self.getToday(9)


        }

        # from werkzeug import secure_filename
        # try:
        #     file = self.objHandle.files['pic']
        #     if file:
        #         filename = secure_filename(file.filename)
        #         data['pic'] = filename  ##封面展示图片
        #         file.save(os.path.join(public.ATTACH_ROOT, filename))
        # except:
        #     pass

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('help_doc' , data , " id = %s " % pk)

        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')

            self.db.insert('help_doc' , data)
            pk = self.db.insertid('help_doc_id')#这个的格式是表名_自增字段
            #dR['isadd'] = 1
        #self.listdata_save(pk,danhao)
        dR['pk'] = pk
        
        return dR

    def getfllist(self):
        L=[]
        sql="select id,name from cms_fl"
        l,t=self.db.select(sql)
        if t>0:
            L=l

        return L
