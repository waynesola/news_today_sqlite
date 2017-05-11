#!/usr/bin/python
# -*- coding:UTF-8 -*-

import scrapy
from bs4 import BeautifulSoup
import urlparse
from news_today_sqlite.items import NewsTodaySqliteItem
import re


class AllArticles(scrapy.Spider):
    name = "rmrb"
    allowed_domains = ["paper.people.com.cn"]
    start_urls = [
        "http://paper.people.com.cn"
    ]

    # 爬取当天报纸所有版块
    def parse(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        rs = soup.find_all("div", class_="right_title-name")
        for r in rs:
            href = r.a["href"]
            url = urlparse.urljoin(response.url, href)
            # 这里必须添加 dont_filter=True 属性，否则会跳过第01版
            request_article = scrapy.Request(url, callback=self.parse_item, dont_filter=True)
            yield request_article

    # 爬取某一版块所有文章，传递到parse_article()
    def parse_item(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        ds = soup.find('table', width="265", style="margin-top:3px;").find_all('a')
        for d in ds:
            href = d.get('href')
            url = urlparse.urljoin(response.url, href)
            request_article = scrapy.Request(url, callback=self.parse_article)
            yield request_article

    # 爬取某一篇文章标题、正文、发表日期、链接
    def parse_article(self, response):
        item = NewsTodaySqliteItem()
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        text = "    "
        h3 = soup.find('div', class_="text_c").find('h3')
        h1 = soup.find('div', class_="text_c").find('h1')
        h2 = soup.find('div', class_="text_c").find('h2')
        h4 = soup.find('div', class_="text_c").find('h4')
        if h3:
            text = text + h3.get_text() + '\n\n    '
        if h1:
            text = text + h1.get_text() + '\n\n    '
        if h2:
            text = text + h2.get_text() + '\n\n    '
        if h4:
            text = text + h4.get_text() + '\n\n'
        ps = soup.find('div', style="display:none", id="articleContent").find_all('p')
        for p in ps:
            text += p.get_text()
            text += "\n\n"
        title = soup.find('title').get_text()
        item['title'] = title
        item['text'] = text
        item['link'] = response.url
        # publish = re.sub('\s', '', soup.find('div', id="riqi_", style="float:left;").get_text())
        # publish = re.sub(u"星期", u"  星期", re.sub(u"人民日报", '', publish))
        publish = u"人民日报"
        pub = soup.find("div", class_="ban_t").get_text()
        pub = re.sub('\s', '', pub)
        pos = re.search("PDF", pub).start()
        pub = pub[:pos]
        item['publish'] = publish + u"  第" + pub
        yield item
