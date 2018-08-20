# -*- coding: utf-8 -*-

#routes.py

import traceback
from imp import reload
import basic
reload(basic)
from basic import public
DEBUG,CLIENT_NAME,showadmin,bugcode=public.DEBUG,public.CLIENT_NAME,public.showadmin,public.bugcode


from flask import Blueprint,redirect

admin=Blueprint('admin',__name__)

@admin.route('/',methods=['GET', 'POST'])
def admin_():
    return redirect('admin/login')


@admin.route('/<string:viewid>/',methods=['GET', 'POST'])
def viewid(viewid):
    try:
        return showadmin(viewid)
    except:
        return bugcode(traceback)


