# coding=utf-8
import linecache
import re
import json

page_input = 0
page_when = 0
page_old = 0
file_path = '57408.txt'
book_history = 'book_history'


def read_search_name(chapter_name):
    # 输入章节跳转执行章节行
    with open(file_path, 'r') as f:
        index = 0
        res = f.readline()
        while chapter_name not in res:
            res = f.readline()
            index += 1
        print (res, index)
        return index


def read_one_chapter(index):
    # 给出指定行，可打印至下一行
    res = linecache.getline(file_path, index)
    print('1', res)
    res = linecache.getline(file_path, index + 1)
    while not re.match('第', res):
        index += 1
        res = linecache.getline(file_path, index)
        if res not in ['\n', '\r', '\n\r']:
            print(res.replace('\n', ''))
    print(index)


def history(file_name):
    with open(book_history, 'r+') as f:
        c = f.read()
        print c
        res = json.loads(c)
        if file_name not in res.get('list'):
            res['list'].append(file_name)
            res['config'][file_name] = {
                'index': 0
            }
            with open(book_history, 'w+') as c:
                c.write(json.dumps(res))
            return {'res': 0}
        else:
            return {'res': res.get('config').get(file_path).get('index')}


def go_on(file_name):
    index = history(file_name).get('res')
    print index
    with open(file_name, 'r') as f:
        res = f.readline()
        when = 1
        while when < index:
            res = f.readline()
            when += 1
        print(res)
        res = f.readline()
        while not re.match('第', res):
            index += 1
            res = f.readline()
            if res not in ['\n', '\r', '\n\r']:
                print res.replace('\n', '')
        return index


import os
import sqlite3
from sql_create import SqlCude


class SqliteCon:

    def __init__(self, book_name):
        if not os.path.isfile('./cache.db'):
            SqlCude().init_table()


# read_search_name('第九百六十章')
# read_one_chapter(89)
go_on(file_path)
# history(file_path)
