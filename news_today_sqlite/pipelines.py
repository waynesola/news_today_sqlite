# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
from news_today_sqlite.items import NewsTodaySqliteItem


class NewsTodaySqlitePipeline(object):
    def process_item(self, item, spider):
        if item.__class__ == NewsTodaySqliteItem:  # 此句非必要，在多个items时可能需要用到
            conn = sqlite3.connect('C:/Program Files/DB Browser for SQLite/database/test.db')
            cur = conn.cursor()
            sql = "insert into mytable1(title,publish,link,text) values (?,?,?,?)"
            cur.execute(sql, (item['title'], item['publish'], item['link'], item['text'],))
            conn.commit()
            cur.close()
            conn.close()
        return item
