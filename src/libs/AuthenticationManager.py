# -*- coding:utf8 -*-

import requests
from pub import logger

class UserAuth:


    def __init__(self):
        self.api = "https://api.saintic.com/user"
        self.headers = {'User-Agent' : 'SaintIC Team Auth'}
        self.timeout = 5

    def login(self, username, password):
        r = requests.post(self.api, params={"action": "log"}, data={"username": username, "password": password}, headers=self.headers, verify=False, timeout=self.timeout)
        res = r.json()
        logger.info(res)
        if r.status_code == requests.codes.ok:
            res = r.json()
            if "success" in res.get("msg") and res.get('code') == 0:
                return True
        return False

    def registry(self, username, password):
        r = requests.post(self.api, params={"action": "reg"}, data={"username": username, "password": password}, headers=self.headers, verify=False, timeout=self.timeout)
        res = r.json()
        logger.info(res)
        if r.status_code == requests.codes.ok:
            if "success" in res.get("msg") and res.get('code') == 0:
                return True
        return False
