# coding=utf-8
import sqlite3


class SqlCude:
    def __init__(self):
        self.conn = sqlite3.connect('cache.db')

    def search(self, table_name, ):
        pass
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
                    indexes int
                );
        ''')
        cur.execute(''' 
                create table chapter(
                    id INTEGER PRIMARY KEY AUTOINCREMENT ,
                    order_id int, 
                    name TEXT,
                    indexes int 
                );
        ''')
        self.conn.commit()
        self.conn.close()


if __name__ == '__main__':
    SqlCude().init_table()
