# -*- coding: utf-8 -*-

##############################################################################
#
#
#
##############################################################################
"""Tpl Module"""

from imp import reload
import basic
reload(basic)
from basic import public
DEBUG,CLIENT_NAME=public.DEBUG,public.CLIENT_NAME

if DEBUG=='1':
    import admin.vi.VI_BASE
    reload(admin.vi.VI_BASE)
from admin.vi.VI_BASE             import cVI_BASE


class cBASE_TPL(cVI_BASE):

    def memotest(self):
        '这就是66'
        print('66666')



