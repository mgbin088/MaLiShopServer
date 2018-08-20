# -*- coding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2006 Haiwen.Zhou
#        File:  wsj:Login.py
#      Author:  Haiwen.Zhou
# Start  Date:  2006/01/31
# Last modify:  2006/01/31
#
##############################################################################
import time,platform,hashlib
from imp import reload
import basic
reload(basic)
from basic import public
DEBUG,CLIENT_NAME=public.DEBUG,public.CLIENT_NAME

db,dActiveUser,ROOT,SITE_ROOT=public.db,public.dActiveUser,public.ROOT,public.SITE_ROOT
make_sub_path,extentions=public.make_sub_path,public.extentions
from qiniu import Auth, put_stream, put_data,put_file
from werkzeug import secure_filename
from flask import jsonify

def mShowHtml(request):
    QUERY_STRING = request.environ['QUERY_STRING']

    temp = QUERY_STRING.split("&")
    # print temp
    Param = {}
    for t in temp:
        if t == '': continue
        p = t.split("=")
        Param[p[0]] = p[1]

    # db.insert("ueupload" , {'act':Param['do']})
    do = Param.get("do", '')
    if Param.get("fetch", '') == '1':
        # header( 'Content-Type: text/javascript' );
        #return 'updateSavePath(' + write(['images']) + ');'
        return 'updateSavePath'

    # 当使用uploadify提交时执行这个独立的处理
    if request.values.get('do', '') == 'fileupload' and request.values.get('mdl', '') == 'uploadify':
        return uploadify_save(request)
    # 其他还是以前的那个处理
    elif do == 'ueupload':
        return m_ueupload(request)
    elif do == 'ueAttaUpload':  # 处理附件上传
        return m_ueAttaUpload(request)
    elif do == 'test':
        return test()
    elif do == 'manager':
        return m_manage(request)
    elif do == 'fileupload':
        return m_fileupload(request)
    elif do == 'delfile':
        return m_delfile(request)
    elif do == 'download':
        return m_download(request)
    elif do == 'uphead':
        return '11'
    elif do == 'qiniu':
        return qiniu_save(request)
    return QUERY_STRING


def test():
    return '{"url":"images\/1\/2014\/08\/Czu978m893te545t3Q9O3LUM7U378t.jpg","title":"","original":"","state":"已超过系统默认文件大小"}'


def m_ueupload(REQUEST):

    import base64, os, random
    imgFile = REQUEST.files['upfile']
    filename = imgFile.filename.strip()
    filename = filename.split('\\')[-1]



    if platform.system() == "Windows":
        path = os.path.join(SITE_ROOT, r'static\resource\attachment\images')
    else:
        path = os.path.join(SITE_ROOT, r'static/resource/attachment/images')
    make_sub_path(path)
    Y = time.strftime("%Y", time.localtime(time.time()))
    M = time.strftime("%m", time.localtime(time.time()))
    path = os.path.join(path, Y)
    make_sub_path(path)
    path = os.path.join(path, M)
    make_sub_path(path)
    result = {
        'url': '',
        'title': '',
        'original': '',
        'state': 'SUCCESS'
    }
    if filename != '':
        ext = filename.split('.')[-1]
        cstr = "%s%s" % (time.ctime(), random.randint(0, 99999))
        save_name = '%s.%s' % (base64.b64encode(cstr.encode('utf-8')).decode('ascii')[:-1], filename.split('.')[-1])
        # db.insert("ueupload" , {'t':'ss'})

        file_path = os.path.join(path, save_name)
        fF = imgFile.read()
        size = len(fF)
        if size > 6291456:
            result['state'] = '已超过系统默认文件大小'
            return jsonify(result)
        ext_arr = extentions.split(",")
        if ext not in ext_arr:
            result['state'] = '上传文件格式有错误'
            return jsonify(result)
        # db.insert("ueupload" , {'filename':save_name,'size':size})
        result['url'] = 'images/%s/%s/%s' % (Y, M, save_name)
        #print(file_path)
        f = open(file_path, 'wb')
        f.write(fF)
        f.flush()
        f.close()
        # db.insert("ueupload" , {'act':'ueupload','filename':result['url'],'attachment':filename,'size':size,'t':write(result)})
        # db.insert("ueupload" , {'t':sql})
        return jsonify(result)
    else:
        result['state'] = '上传失败，请重试！'
        return jsonify(result)


# 编辑器的附件上传
def m_ueAttaUpload(REQUEST):
    import base64, os, random
    #imgFile = REQUEST['upfile']
    imgFile = REQUEST.files['upfile']
    #print ('imgFile=%s'%imgFile)

    filename = imgFile.filename.strip()
    filename = filename.split('\\')[-1]
    #path = os.path.join(SITE_ROOT, r'static\resource\attachment\ueFile')
    if platform.system() == "Windows":
        path = os.path.join(SITE_ROOT, r'static\resource\attachment\ueFile')
    else:
        path = os.path.join(SITE_ROOT, r'static/resource/attachment/ueFile')

    make_sub_path(path)
    Y = time.strftime("%Y", time.localtime(time.time()))
    M = time.strftime("%m", time.localtime(time.time()))
    path = os.path.join(path, Y)
    make_sub_path(path)
    path = os.path.join(path, M)
    make_sub_path(path)
    result = {
        'url': '',
        'title': filename,
        'original': filename,
        'state': 'SUCCESS',
        'fileType': ''
    }
    if filename != '':
        ext = filename.split('.')[-1]
        cstr="%s%s" % (time.ctime(), random.randint(0, 99999))
        save_name = '%s.%s' % (base64.b64encode(cstr.encode('utf-8')).decode('ascii')[:-1], filename.split('.')[-1])
        # db.insert("ueupload" , {'t':'ss'})
        file_path = os.path.join(path, save_name)
        fF = imgFile.read()
        size = len(fF)
        if size > 6291456:
            result['state'] = '已超过系统默认文件大小'
            return jsonify(result)

        ext_arr = extentions.split(",")
        if ext not in ext_arr:
            result['state'] = '上传文件格式有错误'
            return jsonify(result)
        result['url'] = 'ueFile/%s/%s/%s' % (Y, M, save_name)
        f = open(file_path, 'wb')
        f.write(fF)
        f.flush()
        f.close()
        result['fileType'] = '.' + ext
        return jsonify(result)
    else:
        result['state'] = '上传失败，请重试！'
        return jsonify(result)


def m_delfile(REQUEST):
    print('333333333333333')
    # import os
    # pk = REQUEST.get('pk', '')
    #
    # file = db.fetch("select fname from file_pic where seq = %s" % pk)
    # # print "select fname from file_pic where seq = %s" % pk
    # if file:
    #     # print file
    #     path = os.path.join(dINI['ROOT'], r'resource\attachment')
    #     path = os.path.join(path, file['fname'])
    #     if os.path.exists(path) and os.path.isfile(path):
    #         try:
    #             os.remove(path)
    #         except:
    #             return 0
    #     db.query("delete from file_pic where seq = %s" % pk)
    #     return 1
    # else:
    #     return 0


def m_fileupload(REQUEST):
    print('4444444444444444444')
    # import md5, os, random, traceback
    # try:
    #     imgFile = REQUEST['upfile']
    #     pk = REQUEST.get('pk', '')
    #     src = REQUEST.get('src', '')
    #     filename = imgFile.filename.strip()
    #     filename = filename.split('\\')[-1]
    #     path = os.path.join(dINI['ROOT'], r'resource\attachment\doc')
    #     make_sub_path(path)
    #     Y = time.strftime("%Y", time.localtime(time.time()))
    #     M = time.strftime("%m", time.localtime(time.time()))
    #     path = os.path.join(path, Y)
    #     make_sub_path(path)
    #     path = os.path.join(path, M)
    #     make_sub_path(path)
    #     result = {
    #         'url': '',
    #         'title': '',
    #         'size': '',
    #         'ispic': '',
    #         'cid': '',
    #         'ctime': '',
    #         'success': 0,
    #         'msg': '',
    #         'has_mid': 0
    #     }
    #     if filename != '':
    #         filename = filename.decode('utf-8').encode('gbk')
    #         ext = filename.split('.')[-1]
    #         save_name = '%s.%s' % (md5.md5("%s%s" % (time.ctime(), random.randint(0, 99999))).hexdigest(), ext)
    #         # db.insert("ueupload" , {'t':'ss'})
    #
    #         file_path = os.path.join(path, save_name)
    #         fF = imgFile.read()
    #         size = len(fF)
    #         if size > int(dINI['limit']):
    #             result['msg'] = '已超过系统默认文件大小'
    #             return write(result)
    #         ext_arr = dINI['unallow'].split(",")
    #         if ext in ext_arr:
    #             result['msg'] = '上传文件格式有错误'
    #             return write(result)
    #         # db.insert("ueupload" , {'filename':save_name,'size':size})
    #         result['url'] = 'doc/%s/%s/%s' % (Y, M, save_name)
    #         pics = dINI['extentions'].split(",")
    #         ispic = 0
    #         if ext in pics:
    #             ispic = 1
    #         f = open(file_path, 'wb')
    #         f.write(fF)
    #         f.flush()
    #         f.close()
    #         ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    #         cookie = myCookie(REQUEST)
    #         session_user = cookie.igetcookie("__session")
    #         uid = int(session_user['value'])
    #         data = {
    #             'title': filename.replace("." + ext, ''),
    #             'file_name': filename,
    #             'file_size': size,
    #             'is_pic': ispic,
    #             'ctime': ctime,
    #             'cid': uid,
    #             'fname': result['url']
    #         }
    #         if pk != '':
    #             data['m_id'] = int(pk)
    #             result['has_mid'] = 1
    #         if src != '':
    #             data['src'] = src
    #         db.insert("file_pic", data)
    #         pk = db.insertid()
    #
    #         result['title'] = filename
    #         result['size'] = size
    #         result['ispic'] = ispic
    #         result['cid'] = uid
    #         result['ctime'] = ctime
    #         result['success'] = 1
    #         result['pk'] = pk
    #
    #         return write(result)
    #     else:
    #         result['msg'] = '上传失败，请重试！'
    #         return write(result)
    # except:
    #     result = '%s\n' % getToday(8)
    #     result += str(traceback.format_exc())
    #     result += '%s============ end \n\n' % getToday(8)
    #     make_sub_path(r'D:/Zope-Instance/data/cfdi/resource/uploadFile_error/')
    #     f = open(r'D:/Zope-Instance/data/cfdi/resource/uploadFile_error/file_log.log', 'w+')
    #     f.write(result)
    #     f.flush()
    #     f.close()


def m_manage(REQUEST):

    import os, time
    Y = time.strftime("%Y", time.localtime(time.time()))
    path = os.path.join(SITE_ROOT, r'static\resource\attachment\images\%s' % Y)
    make_sub_path(path)
    exts = ['gif', 'jpg', 'jpeg', 'png', 'bmp']
    files = []
    for s in os.listdir(path):
        newDir = os.path.join(path, s)
        if os.path.isdir(newDir):
            for f in os.listdir(newDir):
                ext = f.split('.')[-1]
                files.append(r"attachment/images/%s/%s/%s" % (Y, s, f))
    str = ''
    # path=os.path.join(dINI['ROOT'],r'resource')
    for f in files:
        str += f + "ue_separate_ue"
    return str


def m_download(REQUEST):
    print('66666666666666666')
    # import os
    # pk = REQUEST.get('pk', '')
    # sql = "SELECT seq,title,fname FROM file_pic WHERE seq=%s" % pk
    # lT, iN = db.select(sql)
    # L = list(lT[0])
    # id = L[0]
    # title = L[1]
    # fname = L[2]
    # ext = fname.split(".")[-1]
    # file_path = os.path.join(dINI['ROOT'], r'resource\attachment')
    # f = '%s.%s' % (title, ext)
    #
    # file_path = os.path.join(file_path, '%s' % (fname))
    # file = readImage(REQUEST, file_path, 1, '%s' % (f))
    # db.query("update file_pic set counts = counts + 1 where seq = %s" % pk)
    # return file


# 这个是处理uplodify的上传
def uploadify_save(REQUEST):
    print('7777777777777777777')
    # import md5, os, random, traceback
    # try:
    #     imgFile = REQUEST['Filedata']
    #     pk = REQUEST.get('pk', '')
    #     src = REQUEST.get('src', '')
    #     filename = imgFile.filename.strip()
    #     filename = filename.split('\\')[-1]
    #     path = os.path.join(dINI['ROOT'], r'resource\attachment\doc')
    #     make_sub_path(path)
    #     Y = time.strftime("%Y", time.localtime(time.time()))
    #     M = time.strftime("%m", time.localtime(time.time()))
    #     path = os.path.join(path, Y)
    #     make_sub_path(path)
    #     path = os.path.join(path, M)
    #     make_sub_path(path)
    #     result = {
    #         'url': '',
    #         'title': '',
    #         'size': '',
    #         'ispic': '',
    #         'cid': '',
    #         'ctime': '',
    #         'success': 0,
    #         'msg': '',
    #         'has_mid': 0
    #     }
    #     if filename != '':
    #         filename = filename.decode('utf-8').encode('gbk')
    #         ext = filename.split('.')[-1]
    #         save_name = '%s.%s' % (md5.md5("%s%s" % (time.ctime(), random.randint(0, 99999))).hexdigest(), ext)
    #         # db.insert("ueupload" , {'t':'ss'})
    #
    #         file_path = os.path.join(path, save_name)
    #         fF = imgFile.read()
    #         size = len(fF)
    #         if size > int(dINI['limit']):
    #             result['msg'] = '已超过系统默认文件大小'
    #             return write(result)
    #         ext_arr = dINI['unallow'].split(",")
    #         if ext in ext_arr:
    #             result['msg'] = '上传文件格式有错误'
    #             return write(result)
    #
    #         result['url'] = 'doc/%s/%s/%s' % (Y, M, save_name)
    #         pics = 'png,jpeg,gif,tiff,jpg,jpe,tif'.split(",")  # 判断是否图片
    #         ispic = 0
    #         if ext in pics:
    #             ispic = 1
    #         f = open(file_path, 'wb')
    #         f.write(fF)
    #         f.flush()
    #         f.close()
    #         ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    #         cookie = myCookie(REQUEST)
    #         session_user = cookie.igetcookie("__session")
    #         uid = int(session_user['value'])
    #         data = {
    #             'title': filename.replace("." + ext, ''),
    #             'file_name': filename,
    #             'file_size': size,
    #             'is_pic': ispic,
    #             'ctime': ctime,
    #             'cid': uid,
    #             'fname': result['url']
    #         }
    #         if pk != '':
    #             data['m_id'] = int(pk)
    #             result['has_mid'] = 1
    #         if src != '':
    #             data['src'] = src
    #         db.insert("file_pic", data)
    #         pk = db.insertid()
    #
    #         result['title'] = filename.decode('gbk').encode('utf-8')  # 传过去会乱码，所以还是怎么来的，就怎么转回去
    #         result['size'] = size
    #         result['ispic'] = ispic
    #         result['cid'] = uid
    #         result['ctime'] = ctime
    #         result['success'] = 1
    #         result['pk'] = pk
    #
    #         return write(result)
    #     else:
    #         result['msg'] = '上传失败，请重试！'
    #         return write(result)
    # except:
    #     result = '%s\n' % getToday(8)
    #     result += str(traceback.format_exc())
    #     result += '%s============ end \n\n' % getToday(8)
    #     make_sub_path(r'D:/Zope-Instance/data/cfdi/resource/uploadFile_error/')
    #     f = open(r'D:/Zope-Instance/data/cfdi/resource/uploadFile_error/file_log.log', 'w+')
    #     f.write(result)
    #     f.flush()
    #     f.close()

# 这个是处理plupload插件的上传
def qiniu_save(REQUEST):
    file = REQUEST.files['file']  # request的files属性为请求中文件的数据<input 里的name="file">
    url=''
    if file.filename.find('.') > 0:
        file_ext = file.filename.rsplit('.', 1)[1].strip().lower()

        timeStamp = time.time()
        md5name = hashlib.md5()
        md5name.update(str(timeStamp).encode('utf-8'))
        filename = md5name.hexdigest() + '.' + file_ext

        url = qiniu_upload_file(file, filename)

    # file = REQUEST.files['file']
    #
    # # file_ext = ''
    # # if file.filename.find('.') > 0:
    # #     file_ext = file.filename.rsplit('.', 1)[1].strip().lower()
    # # if file_ext in app.config['ALLOWED_EXT']:
    # #     file_name = str(uuid.uuid1()).replace('-', '') + '.' + file_ext
    # #     # url=save_to_local(file,file_name)
    # ext = secure_filename(file.filename).split('.')[-1]
    # timeStamp = time.time()
    # md5name = hashlib.md5()
    # md5name.update(str(timeStamp).encode('utf-8'))
    # filename = md5name.hexdigest() + '.' + ext
    #
    #
    # url = qiniu_upload_file(file, filename)
    # print(url,'url')
    return url


def qiniu_upload_file(source_file, save_file_name):

    access_key = 'FB380K_uXmob-WLyQRrStnV0N_h1Nbt-Qn4vIYR3'
    secret_key = 'w5QW6sXU3SOTZXmhN9-9koZt8cC_YphUqUd0VZ0Q'
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = 'yjyzj'

    domain_prefix = 'http://cdn.janedao.cn/yjyzj/'#app.config['QINIU_DOMAIN']

    token = q.upload_token(bucket_name, save_file_name)
    ret, info = put_data(token, save_file_name, source_file.stream)

    print(info,'intoooooooo')
    if info.status_code == 200:
        return domain_prefix + save_file_name
    return None
    # # 生成上传 Token，可以指定过期时间等
    # token = q.upload_token(bucket_name, save_file_name,3600)
    # print(token,'token',save_file_name,'save_file_name',source_file.stream)
    # ret2, info2 = put_file(token, save_file_name, source_file)
    # print(type(info2.status_code), info2)
    # ret1, info1 = put_data(token, save_file_name, source_file.stream)
    # ret, info = put_stream(token, save_file_name, source_file.stream)
    # print('6666666666666')
    # print(type(info.status_code),info)
    # if info.status_code == 200:
    #     return domain_prefix + save_file_name
    # return None

