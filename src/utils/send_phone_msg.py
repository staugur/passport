# -*- coding: utf-8 -*-
"""
    passport.utils.send_phone_msg
    ~~~~~~~~~~~~~~

    send sms
    
    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import sys, uuid
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
from aliyunsdkdysmsapi.request.v20170525 import QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.http import method_type as MT
from aliyunsdkcore.http import format_type as FT
from config import PHONE
from .tool import phone_check, logger

"""
短信业务调用接口示例，版本号：v20170525

Created on 2017-06-12

"""
try:
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:
    pass
except Exception as err:
    raise err

# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

acs_client = AcsClient(PHONE["ACCESS_KEY_ID"], PHONE["ACCESS_KEY_SECRET"], REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)

def SendSms(phone_numbers, vcode):
    """使用阿里云短信服务发生验证码
    phone_numbers: 手机号
    vcode: 验证码
    """
    if not phone_check(phone_numbers):
        return dict(success=False, msg="Bad phone format")
    business_id = uuid.uuid1()
    sign_name = PHONE["sign_name"]
    template_code = PHONE["template_code"]
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    smsRequest.set_TemplateParam(u'{"code":"%s"}' %vcode)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)
    
    # 数据提交方式
    # smsRequest.set_method(MT.POST)
    
    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)
    
    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理
    if isinstance(smsResponse, dict):
        smsResponse["success"] = smsResponse.get("Code") == "OK"
    else:
        smsResponse["success"] = False
    logger.info(smsResponse)
    return smsResponse
