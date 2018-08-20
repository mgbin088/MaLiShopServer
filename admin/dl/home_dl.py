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
 

class chome_dl(cBASE_DL):
    
    
    
    def getDBInfo(self):
        sql = '''
        SELECT DB_NAME(database_id) AS [Database Name],[Name] AS [Logical Name],[Physical_Name] AS [Physical Name],((size * 8) / 1024) AS [size],[differential_base_time] AS [Differential Base Time] 
        FROM sys.master_files 
        WHERE DB_NAME(database_id) IN('mysite') 
        '''
        return self.db.fetch(sql)
        