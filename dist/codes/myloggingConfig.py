#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author: kraho
@license: LGPL
@contact: kraho@outlook.com
@software: None
@file: myloggingConfig.py
@time:  2019年1月5日 15点44分
@desc: 封装一个日志模块
'''


import logging
import logging.handlers
import os
from datetime import datetime

LEVELS = {'NOSET': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}


logs_dir = os.path.join(os.path.curdir, "logs")
if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
    pass
else:
    os.mkdir(logs_dir)
name = datetime.now().strftime("%Y%m%d%H%M%S")
# define a rotating file handler
rotatingFileHandler = logging.handlers.RotatingFileHandler(filename ="./logs/%s.log"%name,
                                                  maxBytes = 1024 * 1024 * 50,
                                                  encoding= 'utf-8',
                                                  backupCount = 5)

formatter = logging.Formatter("%(asctime)s %(message)s")

rotatingFileHandler.setFormatter(formatter)
# rotatingFileHandler.encoding = "utf-8"

logging.getLogger("").addHandler(rotatingFileHandler)

#define a handler whitch writes messages to sys

console = logging.StreamHandler()

console.setLevel(logging.NOTSET)

#set a format which is simple for console use

formatter = logging.Formatter("%(message)s")

#tell the handler to use this format

console.setFormatter(formatter)

#add the handler to the root logger

# logging.getLogger("").addHandler(console)

# set initial log level
logger = logging.getLogger("")
logger.setLevel(logging.NOTSET) 


    