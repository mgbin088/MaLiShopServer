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

class cF002_dl(cBASE_DL):
    def init_data(self):

        self.GNL = ['ID','标题','类型','是否展示','发布时间']


    #在子类中重新定义         
    def myInit(self):
        self.src = 'F002'
        pass

    def mRight(self):
            
        sql = u"""
            select cd.id
                ,cd.title
                ,cf.name
                ,case when cd.isshow=0 then '是' else '否' end 
                ,cd.ctime
                --,cd.content
               --,cd.tags
                --,cd.keywords
                --,cd.descript
               -- ,cd.income
               -- ,cd.author
                
                
                
            from cms_doc cd
            left join cms_fl cf on cf.id=cd.fenlei and cf.usr_id=cd.usr_id
            where COALESCE(cd.del_flag,0)!=1 and cd.usr_id=%s
        """%self.usr_id
        # self.qqid = self.GP('qqid','')
        # self.orderby = self.GP('orderby','')
        # self.orderbydir = self.GP('orderbydir','')
        # self.pageNo=self.GP('pageNo','')
        # if self.pageNo=='':self.pageNo='1'
        # self.pageNo=int(self.pageNo)
        # if self.qqid!='' and len(self.QNL) > 0:
        #     sql+= self.QNL + " LIKE '%%%s%%' "%(self.qqid)
        # #ORDER BY
        # if self.orderby!='':
        #     sql+=' ORDER BY %s %s' % (self.orderby,self.orderbydir)
        # else:
        #     sql+=" ORDER BY r.role_id DESC"
        
        L,iTotal_length,iTotal_Page,pageNo,select_size=self.db.select_for_grid(sql,self.pageNo)
        PL=[pageNo,iTotal_Page,iTotal_length,select_size]
        return PL,L

    def get_local_data(self , pk):
        """获取 local 表单的数据
        """
        L = {}
        sql = """
            select id
                ,fenlei
                ,title
                ,tags
                ,keywords
                ,descript
                ,income
                ,author
                ,isshow
                ,status
                ,sort
                ,pic
                ,content
            from cms_doc  
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

        
        #获取表单参数
        fenlei=self.GP('fenlei','')#分类
        title=self.GP('title','')#类型
        tags=self.GP('tags','')#是否展示
        keywords=self.GP('keywords','')#内容
        descript = self.GP('descript','')  # 标题
        income = self.GP('income','')  # 类型
        author = self.GP('author','')  # 是否展示
        isshow = self.GP('isshow','')  # 内容
        status = self.GP('status','')  # 内容
        sort=self.GP('sort','')
        #container = self.GP('container')  # 内容
        content = self.GP('text_contents', '')  # 详情介绍
        pic = self.GP('pic', '')#封面图片




        data = {
                'fenlei':fenlei
                ,'title':title
                ,'tags':tags
                ,'keywords':keywords
                ,'descript': descript
                , 'income': income
                , 'author': author
                , 'isshow': isshow
                ,'status':status
                ,'content':content
                ,'sort':sort
                ,'cid': self.usr_id
                ,'ctime': self.getToday(9)
                ,'uid': self.usr_id
                ,'utime': self.getToday(9)
                ,'usr_id':self.usr_id

        }
        # for k in list(data):
        #     if data[k] == '':
        #         data.pop(k)
        data['pic'] = pic
        #from werkzeug import secure_filename
        # try:
        #     file = self.objHandle.files['pic']
        #     if file:
        #         #filename = secure_filename(file.filename)
        #         ext = secure_filename(file.filename).split('.')[-1]
        #         timeStamp = time.time()
        #         md5name = hashlib.md5()
        #         md5name.update(str(timeStamp).encode('utf-8'))
        #         filename = md5name.hexdigest() + '.' + ext
        #         data['pic'] = filename  ##封面展示图片
        #         file.save(os.path.join(public.ATTACH_ROOT, filename))
        # except:
        #     pass

        if pk != '':  #update
            #如果是更新，就去掉cid，ctime 的处理.
            data.pop('cid')
            data.pop('ctime')
            #data.pop('random')

            self.db.update('cms_doc' , data , " id = %s " % pk)

        else:  #insert
            #如果是插入 就去掉 uid，utime 的处理
            data.pop('uid')
            data.pop('utime')

            self.db.insert('cms_doc' , data)

        dR['pk'] = pk
        
        return dR

    def getfllist(self):
        L=[]
        sql="select id,name from cms_fl where COALESCE(del_flag,0)!=1"
        l,t=self.db.select(sql)
        if t>0:
            L=l

        return L

    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update cms_doc set del_flag=1 where id= %s" % pk)
        return dR
