# -*- coding: utf-8 -*-
#run.py


import os  , sys ,traceback
from imp import reload
reload(sys)

path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(path)
sys.stdout = sys.stderr
import basic
reload(basic)
from basic import public

ROOT,bugcode,DEBUG,CLIENT_NAME,nc_L = public.ROOT,public.bugcode,public.DEBUG,public.CLIENT_NAME,public.nc_L
showadmin,showapi,showupload,requ,a_showupload=public.showadmin,public.showapi,public.showupload,public.requ,public.a_showupload
htinload,apiinload,upinload,adinload,a_upinload=public.htinload,public.apiinload,public.upinload,public.adinload,public.a_upinload
dict_to_xml,paynotify=public.dict_to_xml,public.paynotify


sys.path.append(ROOT)

from flask import Flask,render_template,request,jsonify,redirect

app=Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RTYj'



@app.route('/',methods=['GET', 'POST'])
def index():
    return redirect('admin/login')

@app.route('/api/<int:subid>', methods=['GET','POST'])
def api(subid):
    try:
        REQUEST = request.values
        viewid = REQUEST.get('viewid', '')
        if viewid == 'home':
            sModuleName, className, sModule, sMethodName  = apiinload(REQUEST)
            if DEBUG=='1':
                reload(sModule)
            return showapi(sModuleName,className, sModule, sMethodName, request,subid)
        else:
            return jsonify({ 'code':404,"hello": subid,'msg':'您请求的路径有问题，请检查！'})
    except:
        errstr = str(traceback.format_exc())
        return jsonify({'code': -1, 'msg': '服务器内部错误', 'error_data': errstr})



@app.route('/pay/<int:subid>/notify', methods=['GET','POST'])
def pay(subid):

    try:
        if request.method == 'POST':
            try:
                xml_data = request.data
                dR=paynotify(subid,xml_data)
                if dR==1:
                    result_data = {
                        'return_code': 'FAIL',
                        'return_msg': '参数格式校验错误'
                    }
                else:
                    result_data = {
                        'return_code': 'SUCCESS',
                        'return_msg': 'OK'
                    }
                return dict_to_xml(result_data), {'Content-Type': 'application/xml'}
            except:
                result_data = {
                    'return_code': 'FAIL',
                    'return_msg': '参数格式校验错误'
                }
                return dict_to_xml(result_data), {'Content-Type': 'application/xml'}
    except:
        errstr = str(traceback.format_exc())
        return jsonify({'code': -1, 'msg': '服务器内部错误', 'error_data': errstr})



from admin.routes import admin
app.register_blueprint(admin,url_prefix='/admin')



if __name__ == '__main__':
    app.run()

application=app



