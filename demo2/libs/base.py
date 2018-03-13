# -*- coding: utf-8 -*-
"""
    ProcessName_XXX.libs.base
    ~~~~~~~~~~~~~~

    Base class: dependent services, connection information, and public information.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from utils.tool import plugin_logger


class ServiceBase(object):
    """ 所有服务的基类 """

    def __init__(self):
        #设置全局超时时间(如连接超时)
        self.timeout= 2


class PluginBase(ServiceBase):
    """ 插件基类: 提供插件所需要的公共接口与扩展点 """
    
    def __init__(self):
        super(PluginBase, self).__init__()
        self.logger = plugin_logger
