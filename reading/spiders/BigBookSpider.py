import re
from urllib import request

import os

import scrapy
from bs4 import BeautifulSoup

from reading.items import ReadingSpiderItem


def down(url):
    '''

    :param url:  文章目录地址
    :return:
    '''
    try:
        print(url)
        response = request.urlopen(url)
        html = response.read().decode("utf-8")
        bs = BeautifulSoup(html, "lxml")
        words = bs.find("div", id="readArea").div.findAll("div")[1].text
        words = words.strip().replace(" ", "").replace("\n", "")  #章节内容
        title = bs.find("div", id="readArea").div.h1.text  #章节名
        title=title.replace(" ", "").replace("\n", "")
        filename = ''.join(title) + '.json'
        with open(filename, "a+") as f:
            b = ''.join(words)
            f.write(b)
    except BaseException as e:
        with open("error.txt",'a+') as f:
            f.write(url)
        pass


class ReadingspiderSpider(scrapy.Spider):
    name = 'bigreadingSpider'  # 爬虫名
    allowed_domains = ['']  # 总域
    start_urls = ['http://top.17k.com/']  # 起始页

    def parse(self, response):
        items = []
        roots = BeautifulSoup(response.body, "lxml")
        # lists = roots.findAll("div",attrs={'style': r'display: block;'})  # attrs={"class": "TABBOX","style":"display: block;"})
        lists=roots.findAll("div",class_="TABBOX")
        for info in lists:
            item = ReadingSpiderItem()
            item['list_name'] = info.find("h2", class_='tit')
            try:
                os.mkdir(item['list_name'].text)  # 创建排行榜名称文件夹
            except IOError:
                pass
            os.chdir(item['list_name'].text)  # 切换到排行榜名称文件夹.find("ul",class_="BOX_Top1")
            # print(info.find("div",class_='TYPE').find("ul",class_="BOX Top1").findAll("li"))
            for li in info.find("div",class_='TYPE').find("ul",class_="BOX Top1").findAll("li",limit=10):
                item['name']=li.find("a").text
                item['link']=li.find("a")['href'].replace("book","list")
                print(item['name'])
                print(item['link'])
                headers = {'User-Agent':
                               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                               (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}
                req = request.Request(item['link'], headers=headers)
                try:
                    os.mkdir(item['name'])  # 创建书名名称文件夹
                except IOError:
                    pass
                os.chdir(item['name'])  # 进入书名名称文件夹
                response = request.urlopen(req)
                html = response.read().decode("utf-8")
                bslist = BeautifulSoup(html, "lxml")
                urllist = bslist.find("div", class_="Main List").findAll("dl")[1].find("dd")
                print(urllist)
                for link in urllist.findAll("a"):
                    if 'href' in link.attrs:
                        endurl = "http://www.17k.com" + link.attrs['href']
                        down(endurl)
                path_now = os.getcwd()  # 返回当前工作目录
                path_last = os.path.dirname(path_now)  # 获取文件路径中所在的目录
                os.chdir(path_last)  # 切换到书名上一级->排行榜目录
            path_now = os.getcwd()  # 返回当前工作目录
            path_last = os.path.dirname(path_now)  # 获取文件路径中所在的目录
            os.chdir(path_last)  # 切换到书名上一级->排行榜目录