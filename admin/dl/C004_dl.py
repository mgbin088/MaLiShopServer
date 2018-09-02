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

 
class cC004_dl(cBASE_DL):
    
    def init_data(self):

        self.GNL = ['ID','用户', '订单号','商品数量','状态',
                    '商品总金额','物流费用','实际支付','下单时间','最后更新']

        
        self.src = 'C004'


    def mRight(self):
            
        sql = """
            SELECT
                D.id,
                w.name,
                D.order_num ,
                D.number_goods ,
                m.txt1,
                D.goods_price ,
                D.logistics_price ,
                D.total ,
                
                to_char(D.ctime,'YYYY-MM-DD HH:MM'),
                to_char(D.utime,'YYYY-MM-DD HH:MM')
            FROM wechat_mall_order D
            left join wechat_mall_user w on w.id = D.wechat_user_id 
            left join mtc_t m on m.id=D.status::int and m.type='DDZT'
           where COALESCE(D.del_flag,0)!=1 and  D.usr_id=%s
        """%self.usr_id
        

        if self.orderby != '':
            sql += ' ORDER BY %s %s' % (self.orderby, self.orderbydir)
        else:
            sql += " ORDER BY D.id DESC"
        #print(sql)

        L, iTotal_length, iTotal_Page, pageNo, select_size = self.db.select_for_grid(sql, self.pageNo)
        PL = [pageNo, iTotal_Page, iTotal_length, select_size]
        return PL, L
    
    def get_local_data(self):
        #这里请获取表单所有内容。包括gw_doc表的title

        L = {}
        sql="""
             SELECT
                D.id
                ,D.order_num
                ,m.txt1
                ,D.total
                --to_char(D.ctime,'YYYY-MM-DD HH:MM'),
                --to_char(D.utime,'YYYY-MM-DD HH:MM')
            FROM wechat_mall_order D
            left join mtc_t m on m.id=D.status::int and m.type='DDZT'
           where D.id=%s
        """%self.pk
        if self.pk != '':
            L = self.db.fetch(sql)

        return L

    def local_add_save(self):
        
        """
        <p>这里是local 表单 ，add 模式下的保存处理</p>
        pk 已经传进来  是 gw_doc 的 ID 请勿弄错
        """

        # 这些是表单值
        dR = {'R':'', 'MSG':'提交成功'}
        
        #请先查询自己的表是否有数据。 例如gw_doc有ID为1的数据。 table1的gw_id没有ID为1的数据。需要增加
        #假如字表的名字是 gw_test




        categoryid = self.GP('categoryid','')
        barcode =self.GP('barcode','')
        videoid = self.GP('videoid', '')
        name = self.GP('name', '')
        characteristic = self.GP('characteristic', '')
        paixu = self.GP('paixu', '')
        status = self.GP('status', '')
        content = self.GP('content', '')

        timeStamp = time.time()
        timeArray = time.localtime(timeStamp)
        sname = time.strftime("%Y%m%d%H%M%S", timeArray)
        picurl = self.objHandle.files.get('pic')
        if picurl.name!='':
            ext = picurl.name.split('.')[-1]
            extentions = 'jpg,jpeg,png,gif,bmp'
            pictype = picurl.type.split('/')[-1]
            if pictype not in extentions:
                dR['R'] = 1
                dR['MSG'] = '上传的图片格式有误，请上传jpg,jpeg,png,gif,bmp等类型文件'
                return dR
            save_name = '%s.%s' % (sname,
                                   ext)  # picurl.name#'%s.%s' % (hashlib.md5("%s%s" % (time.ctime(), random.randint(0, 99999))).hexdigest(), ext)
            img_path = os.path.join(public.ATTACH_ROOT, save_name)

            fF = picurl.body
            iF = len(fF)
            if iF > 1024 * 1024:  # 大于1M
                dR['R'] = 1
                dR['MSG'] = '不能保存，图片尺寸大于1M!不适合在网页上显示，请压缩后再上传！'
                return dR
            if self.pk!='':
                sql1 = "SELECT pic FROM goods_info WHERE id=%s" % self.pk
                lT, iN = self.db.select(sql1)
                if iN > 0:
                    ext = lT[0][0].split('/')[-1]
                    if ext != '':
                        oldpic = os.path.join(public.ATTACH_ROOT, '%s' % (ext))
                        try:
                            os.remove(oldpic)
                        except:
                            pass#print('file:%s delete error' % oldpic)

            with open(img_path, 'wb') as f:
                f.write(fF)
                f.flush()
                f.close()
            piclink = 'https://wxapp.yjyzj.cn/data/%s' % save_name
        else:
            piclink =  self.GP('picurl')

        data={

            'categoryid':categoryid,
            'barcode':barcode,
            'videoid': videoid,
            'name': name,
            'characteristic': characteristic,
            'status': status,
            'paixu': paixu,
            'content':content,
            'pic':piclink
        }
        for k in list(data):
            if data[k] == '':
                data.pop(k)

        if self.pk != '':  # update

            data['uid']=self.usr_id
            data['utime'] = self.getToday(9)
            self.db.update('goods_info' , data , " id = %s " % self.pk)

        else:  # insert
            data['usr_id']= self.usr_id
            data['cid'] = self.usr_id
            data['ctime'] = self.getToday(9)
            self.db.insert('goods_info' , data)


            
        return dR
        
    def delete_data(self):
        pk = self.pk
        dR = {'R':'', 'MSG':''}
        self.db.query("update wechat_mall_order set del_flag=1 where id= %s" % pk)
        return dR

    def good_list(self):
        sql="select id,name from goods_category where usr_id =%s"%self.usr_id
        l,t=self.db.select(sql)
        return l

