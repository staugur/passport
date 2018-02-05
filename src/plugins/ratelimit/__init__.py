# -*- coding: utf-8 -*-
"""
    passport.plugins.ratelimit
    ~~~~~~~~~~~~~~

    限流器

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

#: Importing these two modules is the first and must be done.
#: 首先导入这两个必须模块
from __future__ import absolute_import
from libs.base import PluginBase
#: Import the other modules here, and if it's your own module, use the relative Import. eg: from .lib import Lib
#: 在这里导入其他模块, 如果有自定义包目录, 使用相对导入, 如: from .lib import Lib
from flask import request, g, jsonify, make_response
from utils.tool import get_current_timestamp

#：Your plug-in name must be consistent with the plug-in directory name.
#：你的插件名称，必须和插件目录名称等保持一致.
__name__        = "ratelimit"
#: Plugin describes information. What does it do?
#: 插件描述信息,什么用处.
__description__ = "请求限流"
#: Plugin Author
#: 插件作者
__author__      = "Mr.tao <staugur@saintic.com>"
#: Plugin Version
#: 插件版本
__version__     = "0.1" 
#: Plugin Url
#: 插件主页
__url__         = "https://www.saintic.com"
#: Plugin License
#: 插件许可证
__license__     = "MIT"
#: Plugin License File
#: 插件许可证文件
__license_file__= "LICENSE"
#: Plugin Readme File
#: 插件自述文件
__readme_file__ = "README"
#: Plugin state, enabled or disabled, default: enabled
#: 插件状态, enabled、disabled, 默认enabled
__state__       = "disabled"


#: 返回插件主类
def getPluginClass():
    return RateLimiter

#: 插件主类, 不强制要求名称与插件名一致, 保证getPluginClass准确返回此类
class RateLimiter(PluginBase):
    """ 基于用户、ip、时间的每秒、分、时并发限流 """

    def limit(self, **kwargs):
        """请求限流，策略：
        根据用户
        """
        # 获取外部参数
        return
        ip = request.headers.get('X-Real-Ip', request.remote_addr)
        key = "passport:ratelimit:"
        response = make_response(jsonify(msg="RateLimiter"),429)
        response.is_before_request_return = True
        return response

    def register_cep(self):
        """注册上下文入口, 返回扩展点名称及执行的函数"""
        cep = {"before_request_return": self.limit}
        return cep

