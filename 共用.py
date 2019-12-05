# -*- coding=utf-8 -*-
import json
import configparser
导入的资料={}

def 导入json(文件目录: str, 使用缓存: bool = True) -> dict:
    if 使用缓存:
        if 文件目录 not in 导入的资料:
            导入的资料[文件目录] = json.load(open(文件目录,encoding='utf-8'))
    else:
        return json.load(open(文件目录,encoding='utf-8'))
    return 导入的资料[文件目录]

def 导入ini(文件目录: str) -> dict:
    cf = configparser.ConfigParser()
    cf.read(文件目录,encoding='utf-8')
    r ={}
    for i in cf.sections():
        r[i] = {}
        for a, b in cf.items(i):
            r[i][a] = b
    return r

class 脚本错误(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg
