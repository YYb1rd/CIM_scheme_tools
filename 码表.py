# -*- coding:utf-8 -*-
from .共用 import 导入json, 脚本错误
import re
from warnings import warn

class 词条:
    def __init__(self, 词语: str = "", 编码: str = "", **其它):
        self.词语 = 词语
        self.编码 = 编码
        self.其它 = 其它
    def __repr__(self):
        return '词条：{:>4} = {}'.format(self.词语, self.编码)

class 码表:
    def __init__(self, 数据流: iter, 码表名称: str = '', 码表格式: str = '', 码表头: str = '', 码表文件编码: str = 'U8', **其它):
        self.主数据 = list(数据流)
        self.码表名称 = 码表名称
        self.码表格式 = 码表格式
        self.码表头 = 码表头
        self.码表文件编码 = 码表文件编码
        self.其它 = 其它
        if not isinstance(self.主数据[0], 词条):
            raise TypeError("码表必须由词条对象组成")

    提示的行数 = 10
    def __repr__(self):
        r = []
        r.append('码表《{}》，共有{}则词条。\n'.format(self.码表名称, len(self.主数据)))
        for i in range(码表.提示的行数):
            r.append('第{:<3} {!r}'.format(i + 1, self.主数据[i]))
        r.append('\n…………')
        return ''.join(r)
    
    @staticmethod
    def 设置提示行数(数: int):
        码表.提示的行数 = 数
        
    @classmethod
    def 打开文件(cls, 文件目录: str, 码表格式: str = None, 文件编码: str = None, 开始行数: int = None):
        """
        :param 文件目录: 本地文件的地址
        :param 格式: 包含“多多”“rime”“小小”“极点”“酷极”“搜狗”“QQ”“加加”9类
        :param 文件编码: 文件的汉字编码，如“GBK”“big5”“utf-8”
        :param 开始行数: 有些码表开头是配置信息，需要跳过。而码表正式开始的部分称为开始行数
               如果定义了格式（小小、多多、rime）且没定义行数，程序会自动记录码表头。
        :return: 新的码表对象
        """

        匹配规则 = {'多多': re.compile(r'^.+\t[\x21-\x7e０-９]$'),
                    '小小': re.compile(r'^[\x21-\x7e]+( .+)+$'),
                    '加加': re.compile(r'^[a-z]+=.+$'),
                    '搜狗': re.compile(r'^(?P<编码>[a-z]+),(?P<重码>\d+)=(?P<词语>.+)$'),
                    'QQ': re.compile(r'^(?P<编码>[a-z]+)=(?P<重码>\d+),(?P<词语>.+)$')}
        匹配规则['rime'] = 匹配规则['多多']
        匹配规则['极点'] = 匹配规则['酷极'] = 匹配规则['小小']

        def 判断文件编码():
            """返回文件数据"""
            nonlocal 文件编码
            if not 文件编码:
                for i in ['utf-8', 'utf-16', 'gbk', 'gb18030', 'big5']:
                    try:
                        with open(文件目录, encoding=i) as f:
                            文件数据 = f.readlines()
                        文件编码 = i
                        return 文件数据
                    except UnicodeDecodeError:
                        continue
                raise 脚本错误("无法识别文件的编码格式。")
            else:
                with open(文件目录, encoding = 文件编码) as f:
                    文件数据 = f.readlines()
                    return 文件数据
                
        def 判断码表格式():
            nonlocal 码表格式
            有标识的规则 = (('rime', re.compile(r'^.+\t.+\t.+$|^\.\.\.|# Rime dictionary:$')),
                            ('多多', re.compile(r'#[固用辅次类]$|#[类序]\d*$|^\$ddcmd\(|^---config@')),
                            ('小小', re.compile(r'^\[DATA\]$|wildcard=')),
                            ('QQ', 匹配规则['QQ']),
                            ('搜狗', 匹配规则['搜狗']))
            用数量判断的规则 = {'加加': 0, '小小': 0, '多多': 0}
            数量判断极限 = 50
            for i in 文件数据:
                i = i.strip()
                for a, b in 有标识的规则:
                    if b.search(i):
                        码表格式 = a
                        return None
                for a in 用数量判断的规则:
                    if 匹配规则[a].match(i):
                        用数量判断的规则[a] += 1
                        if 用数量判断的规则[a] > 数量判断极限:
                            码表格式 = a
                            return None
            for a, b in 用数量判断的规则.items():
                if b > len(文件数据) * 0.8:
                    码表格式 = a
                    return None
            raise 脚本错误('无法判断文件的码表格式。')

        def 判断开始行数():
            nonlocal 开始行数
            #开始前的标识 = {'多多': re.compile(r'^---config@'),
                        #  '小小': re.compile(r'\[DATA\]'),
                        #  'rime': re.compile(r'\.\.\.')}

            for n, i in enumerate(文件数据):
                if 匹配规则[码表格式].match(i):
                    开始行数 = n + 1
                    return None
                
        def 处理多多rime(n, i):
            r = i.split('\t')
            if len(r) == 1:
                raise warn('文件第{}行（{}）无法识别为{}格式'.format(开始行数 + n, i, 码表格式))
            yield 词条(r[0], r[1])
        def 处理小小极点(n, i):
            r = i.split(' ')
            if len(r) == 1:
                raise warn('文件第{}行（{}）无法识别为{}格式'.format(开始行数 + n, i, 码表格式))
            c = range(1, len(r))
            for a in c:
                yield 词条(r[0], r[a])
        def 处理QQ搜狗(n, i):
            r = 匹配规则[码表格式].match(i)
            if not r:
                raise warn('文件第{}行（{}）无法识别为{}格式'.format(开始行数 + n, i, 码表格式))
            yield 词条(r.group('词语'), r.group('编码'), 重码=r.group('重码'))
        def 处理加加(n, i):
            r = i.split('=')
            if len(r) != 2:
                raise warn('文件第{}行（{}）无法识别为{}格式'.format(开始行数 + n, i, 码表格式))
            yield 词条(r[1], r[0])
        处理各规则的方式 = {'多多': 处理多多rime,
                        'rime': 处理多多rime,
                        'QQ': 处理QQ搜狗,
                        '搜狗': 处理QQ搜狗,
                        '加加': 处理加加,
                        '小小': 处理小小极点,
                        '极点': 处理小小极点,
                        '酷极': 处理小小极点}
        
        def 生成器():
            for n, i in enumerate(文件数据[开始行数-1:]):
                for q in 处理各规则的方式[码表格式](n, i):
                    yield q

        # 开始函数

        文件数据 = 判断文件编码()
        if not 码表格式:
            判断码表格式()
        if not 开始行数:
            判断开始行数()
        return 码表(生成器(), 码表格式=码表格式, 码表名称=文件目录, 码表头=''.join(文件数据[:开始行数 - 1]), 码表文件编码=文件编码)



            
    @classmethod
    def 从列表导入(cls, 列表: list, 词语位置: int = 0, 编码位置: int = 1):
        """
        :param 列表: 二维列表[["词","aa"],["语","bb"]]
        :param 词语位置: 在二级列表中，词语的索引值
        :param 编码位置
        :return: 新的码表对象
        """
        return 码表((词条(i[词语位置], i[编码位置]) for i in 列表),"二维列表")
