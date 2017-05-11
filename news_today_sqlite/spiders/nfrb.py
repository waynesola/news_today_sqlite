#!/usr/bin/python
# -*- coding:UTF-8 -*-

import scrapy
from bs4 import BeautifulSoup
import urlparse
from news_today_sqlite.items import NewsTodaySqliteItem
import re


class AllArticles(scrapy.Spider):
    name = "nfrb"
    allowed_domains = ["epaper.southcn.com"]
    start_urls = [
        "http://epaper.southcn.com/nfdaily/"
    ]

    # 爬取当天报纸所有版块
    def parse(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        hs = soup.find("div", id="btdh").find_all("h3")
        for h in hs:
            href = h.a["href"]
            url = urlparse.urljoin(response.url, href)
            # 这里必须添加 dont_filter=True 属性，否则会跳过第01版
            request_article = scrapy.Request(url, callback=self.parse_item, dont_filter=True)
            yield request_article

    # 爬取某一版块所有文章，传递到parse_article()
    def parse_item(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        ls = soup.find("div", id="content_nav", class_="list").find("ul").find_all('li')
        for l in ls:
            href = l.a.get('href')
            url = urlparse.urljoin(response.url, href)
            request_article = scrapy.Request(url, callback=self.parse_article)
            yield request_article

    # 爬取某一篇文章标题、正文、发表日期、链接
    def parse_article(self, response):
        item = NewsTodaySqliteItem()
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        span = soup.find('div', id="print_area").find('span')
        h1 = soup.find('div', id="print_area").find('h1')
        text = "    "
        if span.string is not None:
            text += span.string + "\n\n    "
        text += h1.get_text() + "\n\n    "
        if span.next_sibling.string is not None:
            text += span.next_sibling.string + "\n\n    "
        ps = soup.find("founder-content").find_all('p')
        for p in ps:
            text += p.get_text() + '\n   '
        title = h1.get_text()
        item['title'] = title
        item['text'] = text
        item['link'] = response.url
        # week = soup.find('li', class_="today").get_text()
        # week = (re.sub('\s', '', week))[-3:]
        # publish = re.sub('/', '-', response.url[39:49])
        # date = arrow.get(publish)
        # publish = date.format('YYYY') + u'年' + date.format('MM') + u'月' + date.format(
        #     'DD') + u'日' + '  ' + week + '  '
        publish = u"南方日报  "
        publish += soup.find('div', class_="left side").find('h3').find('a').get_text()
        item['publish'] = publish
        yield item
