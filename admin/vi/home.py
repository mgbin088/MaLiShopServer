# -*- coding: utf-8 -*-
##############################################################################
#
#
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
    import admin.vi.VI_BASE
    reload(admin.vi.VI_BASE)

from admin.vi.VI_BASE import cVI_BASE


class chome(cVI_BASE):
    def setClassName(self):
        self.dl_name = ''

    def specialinit(self):
        self.viewid = 'home'
        
    def goPartList(self):
        self.getBreadcrumb()  # 获取面包屑
        # 跳到个人中心..
        # self.js.append('idangerous.swiper.min.js')

        # topMenu = self.biz.getTopMenu()
        # leftMenu = self.biz.getLeftMenu(self.mnuid)
        import platform
        self.assign({
            'sysinfo': platform.platform()
            , 'pythoninfo': platform.python_version()
            , 'machine': platform.machine()
        })
        s = self.runApp('home.html')

        return s



