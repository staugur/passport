# -*- coding: utf-8 -*-
"""
    passport.utils.upyunstorage
    ~~~~~~~~~~~~~~

    Upyun class.

    :copyright: (c) 2017 by staugur.
    :license: MIT, see LICENSE for more details.
"""

import upyun
import os
from config import UPYUN as Upyun
from .tool import logger


class CloudStorage(upyun.UpYun):

    def __init__(self, timeout=8, endpoint=upyun.ED_AUTO, debug=False):
        bucket, username, password = Upyun["bucket"], Upyun["username"], Upyun["password"]
        upyun.UpYun.__init__(self, bucket, username, password, timeout=timeout, endpoint=endpoint, debug=debug)
        self.debug = debug

    def exists(self, key):
        '''
         文件或者目录是否存在，返回True或者False
        '''
        try:
            self.getinfo(key)  #若不存在，会抛出异常
            return True
        except:
            return False

    def isdir(self, key):
        '''
        是否为目录
        返回False：不存在/不是
        '''
        if self.exists(key):
            info = self.getinfo(key)
            if info['file-type'] == 'folder':
                return True
        return False

    def isfile(self, key):
        '''
        是否为文件
        返回False：不存在/不是文件
        '''
        if self.exists(key):
            info = self.getinfo(key)
            if info['file-type'] == 'file':
                return True
        return False

    def tree(self, key):
        '''
        类似于linux下的tree。返回由字典组成的列表。每个字典如下
        {'time': '1397960869', 'type': 'folder',
        'path': 'ui.totop.css', 'size': '733'}
        '''
        if self.isfile(key):
            info = self.getinfo(key)
            yield {'path':key, 'time':info['file-date'],
                          'type':'file','size':info['file-size']}
            return
        # is dir
        info = self.getinfo(key)
        yield {'path':key, 'type':'folder'}
        dirs = [key]
        dirs_index = 0
        while dirs_index < len(dirs):
            for item in self.getlist(dirs[dirs_index]):
                if self.debug:
                    logger.debug(dirs[dirs_index])
                    logger.debug(item)
                path = self.__combine_path(dirs[dirs_index], item['name'])
                if item['type'] == 'F':
                    dirs.append(path)
                    yield {'path':path, 'type':'folder'}
                else:
                    yield {'path':path,'time':item['time'] ,
                                  'type':'file','size':item['size']}
            dirs_index += 1

    def make_dirs(self, key):
        '''
        创建目录name，支持创建多级目录
        '''
        if self.exists(key):
            return
        if key[-1] == '/':
            key = key[0:-1]
        key_split = key.split('/')
        dirs = []
        start = 2
        while start <= len(key_split):
            logger.debug('/'.join(key_split[0:start]))
            dirs.append( '/'.join(key_split[0:start]) )
            start += 1
        dirs.sort(key=lambda x:len(x))
        for dir_name in dirs:
            self.mkdir(dir_name)
        if self.debug:
            logger.debug(dirs)

    def __to_unicode(self, s):
        return s.decode('utf-8')

    def __get_dir(self, key):
        '''
        从路径中提取dir
        '''
        if self.isdir(key):
            return key
        elif self.isfile(key):
            s = key.split('/')
            s.pop() #pop the last element
            return '/'.join(s)
        else:
            raise upyun.UpYunClientException(str(key) + ' not found')

    def __get_filename(self, key):
        '''
        从路径中提取file name
        '''
        if self.isfile(key):
            s = key.split('/')
            return s[-1]
        else:
            raise upyun.UpYunClientException(str(key) + ' is dir or  not found')

    def __unify_path(self,path):
        '''
        统一路径分割符
        '''
        return path.strip().replace(os.sep, '/')

    def __combine_path(self, path1, path2):
        path1 = self.__unify_path(path1)
        path2 = self.__unify_path(path2)
        if len(path1) == 0:
            return path2
        return (path1 + '/' + path2).replace('//', '/').replace('///','/')
