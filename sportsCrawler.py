import argparse
import calendar
from datetime import datetime
import os
from multiprocessing import Process
import time
from tqdm import tqdm
from typing import List

import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import requests
from selenium import webdriver

from Exceptions import *
from NewsParser import NewsParser

parser = argparse.ArgumentParser()
parser.add_argument('--startY', type=int, required=True)
parser.add_argument('--startM', type=int, required=True)
parser.add_argument('--endY', type=int, required=True)
parser.add_argument('--endM', type=int, required=True)
args = parser.parse_args()

DATA_DIR = './newsData/7'
DRIVER_PATH = './webdriver/chrome/chromedriver.exe'


class SportsAttribute():
    def __init__(self):
        # e스포츠는 url이 변경되었음
        self.category_code = {"야구": "kbaseball", '해외야구': 'wbaseball', '축구': 'kfootball', '해외축구': 'wfootball',
                              '농구': 'basketball', '배구': 'volleyball', '골프': 'golf', '일반': 'general', 'e스포츠': 'esports'}
        self.selected_categories = []
        self.date = {'startYear': 0, 'startMonth': 0,
                     'endYear': 0, 'endMonth': 0}

    def set_category(self, *args):
        for key in args:
            if self.category_code.get(key) is None:
                raise InvalidCategory
        self.selected_categories = args

    def set_date(self, startYear: int, startMonth: int, endYear: int, endMonth: int):
        args = [startYear, startMonth, endYear, endMonth]
        if startYear > endYear:
            raise OverFlowYear
        if startMonth < 1 or startMonth > 12:
            raise InvalidMonth
        if endMonth < 1 or endMonth > 12:
            raise InvalidMonth
        if startYear == endYear and startMonth > endMonth:
            raise OverFlowMonth

        for key, date in zip(self.date, args):
            self.date[key] = date

    @staticmethod
    def make_newsURL_form(NewsURL, startYear: int, endYear: int, startMonth: int, endMonth: int) -> List[str]:
        madeURL = []
        start, end = 1, 12
        for year in range(startYear, endYear+1):
            if startYear == endYear:
                start = startMonth
                end = endMonth
            else:
                if year == startYear:
                    start = startMonth
                elif year == endYear:
                    end = endMonth

            for month in tqdm(range(start, end + 1), desc="Month Iteration"):
                for day in tqdm(range(1, calendar.monthrange(year, month)[1] + 1), desc="Day Iteration"):
                    if len(str(month)) == 1:
                        month = '0' + str(month)
                    if len(str(day)) == 1:
                        day = '0' + str(day)
                    if datetime.now().month == month and datetime.now().year == year and int(datetime.now().day) < int(day):
                        continue

                    url = NewsURL + str(year) + str(month) + str(day)

                    # 끝페이지보다 더 큰 값을 이동하면 자동으로 마지막 페이지로 이동하게 된다.
                    totalpage = NewsParser.find_news_total_pageS(
                        url + '&page=10000')
                    for page in range(1, totalpage + 1):
                        madeURL.append(url + '&page=' + str(page))
        return madeURL

    @classmethod
    def fileWrite(self, file_name: str, title: str, content: str):
        f = open(file_name, 'w')
        f.write(title)
        f.write("\n")
        for c in content:
            f.write(c)
            f.write("\n")
        f.close()

    @staticmethod
    def getURLdata(url: str, max_tries=10):
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url)
            except:
                time.sleep(60)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout

    def crawling(self, category_name: str):
        print(str(os.getpid())+" : " + category_name + '\n')
        url = "http://sports.news.naver.com/" + \
            str(self.category_code.get(category_name)) + \
            "/news/index.nhn?isphoto=N&date="
        urls = self.make_newsURL_form(
            url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth'])
        number = 0

        print("Crawling Start!")
        for url in tqdm(urls):
            print(str(os.getpid()) + " : " + url)
            driver = self.set_selenium_options()
            driver.implicitly_wait(2)
            driver.get(url)
            driver.implicitly_wait(2)
            pages = driver.find_elements_by_css_selector('#_newsList > ul >li')

            articles = []
            for page in pages:
                articles.append(page.find_element_by_css_selector(
                    'a').get_attribute('href'))
            del pages
            driver.quit()
            for content_URL in articles:
                time.sleep(0.05)

                content_html = self.getURLdata(content_URL)
                document_content = BeautifulSoup(
                    content_html.content, 'html.parser')

                try:
                    # 기사 제목 가져옴
                    article_title = document_content.find_all(
                        'h4', {'class': 'title'})
                    title = ''  # 뉴스 기사 제목 초기화
                    title += NewsParser.clear_headline(
                        str(article_title[0].find_all(text=True)))
                    if not title:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 본문 가져옴
                    article_body_contents = document_content.find_all(
                        'div', {'id': 'newsEndContents'})
                    content = NewsParser.clear_contentS(
                        list(article_body_contents[0].find_all(text=True)))
                    if not len(content):  # 공백일 경우 기사 제외 처리
                        continue

                    try:
                        if not(os.path.isdir(DATA_DIR)):
                            os.makedirs(DATA_DIR)
                            print("폴더 생성")
                    except OSError:
                        print("폴더 생성에 실패했습니다.")

                    file_name = DATA_DIR+'/'+category_name+str(number)+".txt"
                    self.fileWrite(file_name, title, content)
                    number += 1

                    del content, title
                    del article_title, article_body_contents
                    del content_html, document_content

                except Exception:
                    del content_html, document_content
                    pass

    def set_selenium_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)
        except:
            path = chromedriver_autoinstaller.install()
            driver = webdriver.Chrome(path, chrome_options=options)

        return driver

    def start(self):
        for category_name in self.selected_categories:
            proc = Process(target=self.crawling, args=(category_name,))
            proc.start()


if __name__ == '__main__':
    Crawler = SportsAttribute()
    Crawler.set_category("야구")
    Crawler.set_date(args.startY, args.startM, args.endY, args.endM)
    Crawler.start()
