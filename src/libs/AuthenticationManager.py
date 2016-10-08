# -*- coding:utf8 -*-

import requests
from utils.tool import logger

class UserAuth:


    def __init__(self):
        self.api = "https://auth.saintic.com/api/user/"
        self.api = "http://127.0.0.1:10030/api/user/"
        self.headers = {'User-Agent' : 'SaintIC Auth'}
        self.timeout = 10

    def login(self, username, password):
        r = requests.post(self.api, params={"action": "log"}, data={"username": username, "password": password}, headers=self.headers, verify=False, timeout=self.timeout)
        res = r.json()
        logger.info(res)
        if res.get('code') == 0:
            return True
        return False

    def registry(self, username, password):
        r = requests.post(self.api, params={"action": "reg"}, data={"username": username, "password": password}, headers=self.headers, verify=False, timeout=self.timeout)
        res = r.json()
        logger.info(res)
        if  res.get('code') == 0:
            return True
        return False
