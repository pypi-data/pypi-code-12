#coding:utf-8

import logging
import logging.config
import config
import os
import utils
import awslib.base.utils

log_dir = os.path.abspath(os.path.split(__file__)[0])
log_conf_file = os.path.join(log_dir,"logger.conf")

app_data_path = utils.get_app_data_path()
log_path = os.path.join(app_data_path,'logs')
awslib.base.utils.mkdirs(log_path)
current_cwd = os.getcwd()

os.chdir(log_path)
#加载日志配置文件
logging.config.fileConfig(log_conf_file)

os.chdir(current_cwd)
#获取root日志
logger = logging.getLogger()
#是否禁止日志
logger.disabled = config.LOGGER_DISABLED 
