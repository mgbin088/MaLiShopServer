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

 
class cB001_dl(cBASE_DL):
    
    def init_data(self):


        self.GNL = ['ID','编号', '类型标记', '业务编号','名称',
                    'Banner图片','链接地址','状态','添加时间','修改时间	']
        self.src = 'B001'


    def mRight(self):
            
        sql = """
            SELECT
                D.id,
                D.type,
                D.businessid,
                D.title,
                D.pic,
                D.linkurl,
                case when D.status=0 then '是' else '否' end,
                to_char(D.ctime,'YYYY-MM-DD HH:MM'),
                to_char(D.utime,'YYYY-MM-DD HH:MM')
            FROM banner D
           where COALESCE(D.del_flag,0)!=1 and   D.usr_id=%s
        """%self.usr_id
        
        if self.qqid != '' and len(self.QNL) > 0:
            sql += self.QNL + "AND LIKE '%%%s%%' " % (self.qqid)
        # ORDER BY 
        # if self.orderby != '':
        #     sql += ' ORDER BY %s %s' % (self.orderby, self.orderbydir)
        # else:
        sql += " ORDER BY D.type ,D.paixu"

        L, iTotal_length, iTotal_Page, pageNo, select_size = self.db.select_for_grid(sql, self.pageNo)
        PL = [pageNo, iTotal_Page, iTotal_length, select_size]
        return PL, L
    
    def get_local_data(self):
        #这里请获取表单所有内容。包括gw_doc表的title

        L = {}
        sql="""
             SELECT
                D.id,
                D.type,
                D.businessid,
                D.title,
                D.status,
                D.remark,
                D.linkUrl,
                D.pic,
                D.paixu
            FROM banner D
            where D.id = %s
        """%self.pk
        if self.pk != '':
            L = self.db.fetch(sql)

        return L

    def local_add_save(self):
        
        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        pk 已经传进来  是 gw_doc 的 ID 请勿弄错
        """
        data = {}



        # 这些是表单值
        dR = {'R':'', 'MSG':'提交成功'}

        type = self.GP('type','')#类型标记:
        if type!='':
            data['type']=type
        businessid =self.GP('businessid','')# 业务编号:

        if businessid!='':
            businessid=int(businessid)

            data['businessid']=businessid

        # if businessid=='':
        #     businessid='null'
        # else:
        #     businessid=int(businessid)
        title = self.GP('title', '')#名称
        if title!='':
            data['title']=title

        #Banner图片
        linkurl = self.GP('linkurl', '')#链接地址
        if linkurl!='':
            data['linkurl']= linkurl

        status = self.GP('status', '')#状态
        if status!='':
            data['status']= int(status)

        paixu = self.GP('paixu', '')#排序
        if paixu=='':
            paixu=0
        data['paixu']= int(paixu)
        remark = self.GP('remark', '')#备注
        if remark!='':
            data['remark']= remark
        pic=self.GP('picUrl','')
        #if pic!='':
        data['pic']= pic

        if self.pk != '':  # update

            data['uid']=self.usr_id
            data['utime'] = self.getToday(9)
            self.db.update('banner' , data , " id = %s " % self.pk)
            pk=self.pk

        else:  # insert
            data['usr_id']= self.usr_id
            data['cid'] = self.usr_id
            data['ctime'] = self.getToday(9)
            self.db.insert('banner' , data)
            #pk = self.db.insertid('banner_id')  # 这个的格式是表名_自增字段

        #dR['pk']=pk

            
        return dR
        
    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update banner set del_flag=1 where id= %s" % pk)
        return dR

