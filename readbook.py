# coding=utf-8
import linecache
import re
import json
import os
import time
import sys
import datetime
from sql_create import SqlCude

reload(sys)
sys.setdefaultencoding('utf8')
os.system('chcp 65001')


def read_search_name(chapter_name, file_path):
    # 输入章节跳转执行章节行 不启用
    with open(file_path, 'r') as f:
        index = 0
        res = f.readline()
        while chapter_name not in res:
            res = f.readline()
            index += 1
        print (res, index)
        return index


class SqliteCon(object):
    with open('config.conf', 'r') as f:
        try:
            conf = json.loads(re.sub('#.*\n', '', f.read().replace("'", '"')))
        except Exception as e:
            raise Exception('配置文件出错： %s' % e)
    when_read = ''
    conf_list = ['line_number', 'up', 'down', 'checks', 'book', 'mark', 'quite', 'cha', 'add', 'chapters', 'color']
    for i in conf_list:
        locals()[i] = conf.get(i)

    def __init__(self):
        if not os.path.isfile('./cache.db'):
            SqlCude().init_table()

    def y_c(self, zh):
        b = {
            u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10,
            u'百': 100, u'千': 1000, u'万': 10000
        }
        zh = zh.replace(u'零', '')
        if zh[:1] == u'十':
            zh = u'一' + zh
        d = 0
        for i in range(0, len(zh), 2):
            split_zh = zh[i:i + 2]
            if len(split_zh) == 2:
                zh_num = b.get(split_zh[0]) * b.get(split_zh[1])
            else:
                zh_num = b.get(split_zh[0])
            d += zh_num
        return d

    def book_list(self):
        path = os.getcwd()
        book_dirs = os.walk(os.path.join(path, 'books'))
        book_list = []
        for a, b, f in book_dirs:
            for i in f:
                book_name = os.path.join(a, i)
                book_list.append(book_name.decode('gbk').encode('utf-8'))
        return book_list

    def action_read(self, book_name, index, plus=True):
        index = int(index)

        self.when_read = book_name
        if isinstance(book_name, str):
            book_name = unicode(book_name)
        if index < 0:
            index = 0
        init = 0
        os.system('cls')
        print_all = ''
        while self.line_number > init:
            res = linecache.getline(book_name, index)
            if plus:
                index += 1
            else:
                index -= 1
            if res not in ['\n', '\r', '\n\r']:
                print_content = res.replace('\n', '').replace('\t', '')
                if plus:
                    print_all += print_content + '\n'
                else:
                    print_all = print_content + '\n' + print_all
                init += 1
        chuli = '\033[1;{}m{}\033[0m'.format(self.color, print_all)
        print chuli
        SqlCude().ex_sql('''update read_book_list set indexes='%s' where name='%s' ''' % (index, book_name))
        SqlCude().ex_sql('''update last_read set name='%s' ''' % book_name)
        is_go_on = raw_input('')
        if is_go_on.lower() == self.down:
            self.action_read(book_name, index)
        elif is_go_on.lower() == self.up:
            self.action_read(book_name, index, plus=False)
        elif is_go_on.lower() == self.add:
            name = raw_input('请输入标签名')
            if not name:
                name = linecache.getline(book_name, index)
            SqlCude().ex_sql(
                "insert into bookmark (name, book, indexes) values ('{}','{}','{}')".format(name, book_name, index))
            print 'add ok'
            self.action_read(book_name, index)
        else:
            self.check()

    def show_chapters(self, index=0):
        book_name = self.when_read
        res = SqlCude().search('chapter', book=book_name)
        indexes = {}
        while res:
            for_res = res[index:index + 10]
            if not for_res:
                self.show_chapters(book_name)
            for i in for_res:
                print i[1], ' : ', str(i[2])
                indexes[str(i[1])] = int(i[-1])
            is_go_on = raw_input('')
            if is_go_on.isdigit():
                self.action_read(book_name, indexes.get(is_go_on))
            elif is_go_on == self.up:
                index = index - 10 if index >= 10 else 0
                self.show_chapters(book_name, index=index)
            elif is_go_on == self.down:
                index += 10
            else:
                self.check()
        else:
            print 'init ing...'
            if book_name == 'a':
                book_list = self.book_list()
                for i in book_list:
                    self.init_chapter(i)
                    book_name = i
            else:
                self.init_chapter(book_name)
            time.sleep(0.1)
            print 'init ok'
            self.when_read = book_name
            self.show_chapters()

    def init_chapter(self, book_name):
        if isinstance(book_name, str):
            book_name = unicode(book_name)
        with open(book_name, 'r') as t:
            res = t.readline()
            book_index = 1
            sql_str = ""
            while res:
                if re.match('第', res):
                    ccc = re.sub(u'[一二三四五六七八九十百千万]', '', unicode(res, 'utf-8'))
                    if ccc[0:2] == u'第{}'.format(self.cha):
                        zh_num = res.split('章')[0].replace('第', '').replace(' ', '')
                        number = self.y_c(zh_num)
                        sql_str += "('{}','{}','{}','{}'),".format(number, res, book_name, book_index)
                res = t.readline()
                if '\r\n' in res:
                    book_index += 1
                book_index += 1

        if sql_str:
            sql_str = sql_str[:-1]
            insert_sql = ''' insert into  chapter (order_id, name, book, indexes) values {}'''.format(sql_str)
            SqlCude().ex_sql(insert_sql)

    def book_mark(self, index=0):
        mark_list = SqlCude().search('bookmark', book=self.when_read)
        indexes = {}
        if mark_list:
            for_mark = mark_list[index:index + 10]
            if not for_mark:
                self.book_mark()
            for i in for_mark:
                print i[0], ' : ', str(i[1])
                indexes[str(i[0])] = int(i[-1])
            is_go_on = raw_input('')
            if is_go_on.isdigit():
                self.action_read(self.when_read, indexes.get(str(is_go_on)))
            elif is_go_on == self.up:
                index = index - 10 if index >= 10 else 0
                self.show_chapters(self.when_read, index=index)
            elif is_go_on == self.down:
                index += 10
                self.book_mark(index)
            else:
                self.check()
        else:
            print '没有书签'
            self.check()

    def book_read(self, name):
        res = SqlCude().search('read_book_list', name=name)
        if not res:
            SqlCude().ex_sql("insert into read_book_list (name, indexes) values ('%s', '1')" % name)
            time.sleep(0.1)
            self.book_read(name)
        else:
            index = res[0][2]
            self.action_read(name, index)

    def run(self):
        is_last_name = SqlCude().search('last_read', True)[0][0]
        if is_last_name and is_last_name != 'a':
            self.book_read(is_last_name)
        else:
            self.display_book()

    def display_book(self):
        book_list = self.book_list()
        check_num = map(str, range(len(book_list)))
        for index, i in enumerate(book_list):
            print index, ' : ', i.split('\\')[-1]
        check_book = raw_input('请输入编号')
        if check_book.isdigit and check_book in check_num:
            self.book_read(book_list[int(check_book)])
        self.check()

    def quite_down(self):
        print 'bye !!!'
        os._exit(0)

    def check(self):
        if not self.when_read:
            self.when_read = SqlCude().search('last_read', all=True)[0][0]
        function_dict = {self.book: self.display_book, self.chapters: self.show_chapters,
                         self.mark: self.book_mark, self.down: self.run, self.quite: self.quite_down}
        check = raw_input('主界面，请选择')
        if check in function_dict:
            function_dict[check]()
        else:
            self.check()


def action():
    try:
        SqliteCon().check()
    except Exception as e:
        print 'ERROR:>>>', e
    finally:
        action()


if __name__ == '__main__':
    action()
    # SqliteCon().check()
