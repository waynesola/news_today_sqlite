#!/usr/bin/python
# -*- coding:UTF-8 -*-

import scrapy
from bs4 import BeautifulSoup
import urlparse
from news_today_sqlite.items import NewsTodaySqliteItem
import re


class AllArticles(scrapy.Spider):
    name = "byt_szjj"
    allowed_domains = ["banyuetan.org"]
    start_urls = [
        "http://www.banyuetan.org/chcontent/sz/szgc/index.shtml"
    ]

    # 爬取第一页，传递给parse_page()
    def parse(self, response):
        page = 1
        url = "http://www.banyuetan.org/chcontent/sz/szgc/index.shtml"
        yield scrapy.Request(url, callback=self.parse_page)
        if page >= 2:
            for r in range(2, page + 1):
                url = "http://www.banyuetan.org/chcontent/sz/szgc/index_" + str(r) + ".shtml"
                yield scrapy.Request(url, callback=self.parse_page)

    # 爬取当前页面所有文章，传递到parse_item()
    def parse_page(self, response):
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        ls = soup.find("div", class_="list_cont_li").ul.find_all("li")
        for l in ls:
            # 排除分隔行
            if l.a:
                href = l.a.get('href')
                url = urlparse.urljoin(response.url, href)
                yield scrapy.Request(url, callback=self.parse_article)

    # 爬取某一篇文章标题、正文、发表日期、链接
    def parse_article(self, response):
        item = NewsTodaySqliteItem()
        data = response.body
        soup = BeautifulSoup(data, "html5lib")
        tag = soup.find('div', class_="content_con_list")
        text = "    "
        title = re.sub('\s', '', tag.find('h1').get_text())
        text = text + title + '\n\n    '
        h2_bs = tag.find('h2').find_all('b')
        for b in h2_bs:
            text = text + b.get_text() + "    "
        text += "\n\n    "
        ps = soup.find('div', class_="text", id="showneirong").find_all('p')
        for p in ps:
            text += p.get_text()
            text += "\n\n    "
        item['title'] = title
        item['text'] = text
        item['link'] = response.url
        publish = tag.h2.span.b.get_text()
        item['publish'] = u"半月谈—时政聚焦  " + publish
        yield item
