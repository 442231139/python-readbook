# coding=utf-8
import sqlite3


class SqlCude:
    def __init__(self):
        self.conn = sqlite3.connect('cache.db')

    def search(self, table_name, all=False, id=None, name=None, book=None):
        if all:
            cond = ''
        elif id or id == 0:
            cond = 'where id={}'.format(id)
        elif name:
            cond = "where  name='{}'".format(name)
        elif book:
            cond = "where  book='{}'".format(book)
        else:
            raise Exception('参数错误')
        sql = ''' select * from {} {} '''.format(table_name, cond)
        cur = self.conn.cursor()
        res = cur.execute(sql)
        data = res.fetchall()
        return data

    def ex_sql(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()

    def init_table(self):
        cur = self.conn.cursor()
        cur.execute('''
                create table read_book_list(
                    id INTEGER PRIMARY KEY AUTOINCREMENT ,
                    name TEXT  NOT NULL unique,
                    indexes int,
                    is_last default 0
                );    
        ''')
        cur.execute(''' 
                create table bookmark(
                    id INTEGER PRIMARY KEY AUTOINCREMENT ,
                    name TEXT,
                    book int,
                    indexes int
                );
        ''')
        cur.execute(''' 
                create table chapter(
                    id INTEGER PRIMARY KEY AUTOINCREMENT ,
                    order_id int, 
                    name TEXT,
                    book int,
                    indexes int 
                );
        ''')
        cur.execute(''' 
                        create table last_read(
                            name TEXT
                        );
                ''')
        cur.execute(''' insert into last_read values ('a')
                        ''')
        self.conn.commit()
        self.conn.close()


if __name__ == '__main__':
    SqlCude().init_table()