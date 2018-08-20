## -*- coding: utf-8 -*-

from datetime import timedelta
from celery.schedules import crontab

# Broker and Backend
BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# Timezone
CELERY_TIMEZONE='Asia/Shanghai'    # 指定时区，不指定默认为 'UTC'
# CELERY_TIMEZONE='UTC'

# import
CELERY_IMPORTS = (
    'celery_app.pfc'
)

# schedules
CELERYBEAT_SCHEDULE = {
    'add-every-600-seconds' : {
        'task' : 'celery_app.pfc.send_mail',
        'schedule' : 600.0,
    },
'add-every-300-seconds' : {
        'task' : 'celery_app.pfc.silk_mp3',
        'schedule' : 200.0,
    }
# 'multiply-at-some-time': {
    #     'task': 'celery_app.celery.send_mail_0',
    #     'schedule': crontab(hour=0, minute=30),  # 每天早上 0 点 50 分执行一次
    #    'args': ()                               # 任务函数参数
    # },
    # 'multiply-at-time': {
    #     'task': 'celery_app.celery.send_mail_13',
    #     'schedule': crontab(hour=13, minute=30),  # 每天早上 13 点 50 分执行一次
    #    'args': ()                               # 任务函数参数
    # }
}

