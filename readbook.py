# coding=utf-8
import linecache
import re
import json
import os, time, sys
from sql_create import SqlCude

reload(sys)
sys.setdefaultencoding('utf8')


def read_search_name(chapter_name, file_path):
    # 输入章节跳转执行章节行
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
            conf = json.loads(f.read().replace("'", '"'))
        except Exception as e:
            raise '配置文件出错：', e
    when_read = ''
    line_number = conf.get('page_line_number')
    up = conf.get('up')
    down = conf.get('down')
    checks = conf.get('checks')
    book = conf.get('show_book')
    mark = conf.get('show_mark')
    quite = conf.get('quite')
    cha = conf.get('cha')
    add = conf.get('add')
    chapters = conf.get('show_cha')
    color = conf.get('color')

    def __init__(self):
        if not os.path.isfile('./cache.db'):
            SqlCude().init_table()

    def y_c(self, zh):
        b = {
            u'一': 1, u'二': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9, u'十': 10,
            u'百': 100, u'千': 1000, u'万': 10000
        }
        zh = zh.replace(u'零', '')
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
                book_list.append(book_name)
        return book_list

    def action_read(self, book_name, index, plus=True):
        index = int(index)
        self.when_read = book_name
        if not plus:
            index -= self.line_number
        if index < 0:
            index = 0
        init = 0
        while self.line_number > init:
            res = linecache.getline(book_name, index)
            index += 1
            init += 1
            if res not in ['\n', '\r', '\n\r']:
                os.system('cls')
                print res.replace('\n', '').replace('  ', '')
        SqlCude().ex_sql('''update read_book_list set indexes='%s' where name='%s' ''' % (index, book_name))
        SqlCude().ex_sql('''update last_read set name='%s' ''' % book_name)
        is_go_on = raw_input('')
        if is_go_on.lower() == self.down:
            self.action_read(book_name, index)
        elif is_go_on.lower() == self.up:
            self.action_read(book_name, index, plus=False)
        elif is_go_on.lower() == self.add:
            name = raw_input('请输入标签名')
            SqlCude().ex_sql(
                "insert into bookmark (name, book, indexes) values ('{}','{}','{}')".format(name, book_name, index))
            print 'add ok'
            self.action_read(book_name, index)
        else:
            self.check()

    def show_chapters(self, book_name, index=0):
        res = SqlCude().search('chapter', book=book_name)
        indexes = {}
        if res:
            for i in res[index:index + 10]:
                print i[1], ' : ', i[2]
                indexes[str(i[1])] = int(i[-1])
            is_go_on = raw_input('')
            if is_go_on.isdigit():
                self.action_read(book_name, indexes.get(str(is_go_on)))
            elif is_go_on == self.up:
                index = index - 10 if index >= 10 else 0
                self.show_chapters(book_name, index=index)
            elif is_go_on == self.down:
                index += 10
            self.show_chapters(book_name, index=index)
        else:
            self.init_chapter(book_name)
            time.sleep(0.1)
            self.show_chapters(book_name)

    def init_chapter(self, book_name):
        with open(book_name, 'r') as t:
            res = t.readline()
            book_index = 0
            while res:
                if re.match('第', res):
                    ccc = re.sub(u'[一二三四五六七八九十百千万]', '', unicode(res, 'utf-8'))
                    if ccc[0:2] == u'第{}'.format(self.cha):
                        zh_num = res.split('章')[0].replace('第', '').replace(' ', '')
                        numbner = self.y_c(zh_num)
                        sql = "insert into chapter (order_id, name, book, indexes) values ('{}','{}','{}','{}')".format(
                            numbner, res, book_name, book_index)
                        SqlCude().ex_sql(sql)
                book_index += 1
                res = t.readline()

    def book_mark(self, index=0):
        mark_list = SqlCude().search('bookmark', book=self.when_read)
        indexes = {}
        if mark_list:
            for i in mark_list[index:index + 10]:
                print i[1], ' : ', i[2]
                indexes[str(i[0])] = int(i[-1])
            is_go_on = raw_input('')
            if is_go_on.isdigit():
                self.action_read(self.when_read, indexes.get(str(is_go_on)))
            elif is_go_on == self.up:
                index = index - 10 if index >= 10 else 0
                self.show_chapters(self.when_read, index=index)
            elif is_go_on == self.down:
                index += 10
                self.show_chapters(self.when_read, index=index)
            else:
                self.check()
        else:
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
        if is_last_name and is_last_name != '0':
            self.book_read(is_last_name)
        else:
            self.display_book()

    def display_book(self):
        book_list = self.book_list()
        for index, i in enumerate(book_list):
            print index, ' : ', i.split('\\')[-1]
        check_book = raw_input('请输入编号')
        if check_book.lower() == self.chapters:
            self.check()
        self.book_read(book_list[int(check_book)])

    def check(self, book_name=None):
        if not self.when_read:
            self.when_read = SqlCude().search('last_read', all=True)[0][0]
        check = raw_input('主界面，请选择')
        # 书列表
        if check.lower() == self.book:
            self.display_book()
        # 章节
        elif check.lower() == self.chapters:
            self.show_chapters(self.when_read)
        elif check.lower() == self.mark:
            self.book_mark()

        # 继续上次
        elif check.lower() == '':
            self.run()
        # 退出
        elif check.lower() == self.quite:
            print 'bye !!!'
            return

    def test(self):
        pass


# read_search_name('第九百六十章')
# read_one_chapter(89)
# go_on(file_path)
# history(file_path)
SqliteCon().check()
SqlCude()
# test
# haha
