import calendar
from datetime import datetime
from multiprocessing import Pool
import multiprocessing
import os
import sys
from multiprocessing import Process
import time
from tqdm import tqdm
from typing import List

from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import numpy as np
from selenium import webdriver
import pandas as pd
import requests


from Exceptions import *
from NewsParser import NewsParser

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

    def set_date(self):
        startYear = int(input("Please Enter start Year (ex) 2019): "))
        startMonth = int(input("Please Enter start Month (ex) 05): "))
        endYear = int(input("Please Enter end Year (ex) 2019): "))
        endMonth = int(input("Please Enter end Year (ex) 2019): "))
        if not (startYear and startMonth and endYear and endMonth):
            print("Incorrect Year or Month")
            sys.exit()
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

    def get_total_URLs(self, category_name: str):
        print(str(os.getpid())+" : " + category_name + '\n')
        url = "http://sports.news.naver.com/" + \
            str(self.category_code.get(category_name)) + \
            "/news/index.nhn?isphoto=N&date="
        urls = self.make_newsURL_form(
            url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth'])

        print("Crawling Start!")
        print(urls)
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
        return articles, category_name

    def crawling(self, articles, category_name: str):
        datas = pd.DataFrame(columns=["title", "content", "url"])
    
        for content_URL in tqdm(articles, desc=f"{category_name} Crawling"):
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
                   if not(os.path.isdir(os.path.join(DATA_DIR, str(7)))):
                        os.makedirs(os.path.join(DATA_DIR, str(7)))
                        print("폴더 생성")
                except OSError:
                    print("폴더 생성에 실패했습니다.")

                datas = datas.append(
                    {"title": title, "content": content, "url": content_URL}, ignore_index=True)

                del content, title
                del article_title, article_body_contents
                del content_html, document_content

            except Exception:
                del content_html, document_content
                pass

        return datas
    def set_selenium_options(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        path = chromedriver_autoinstaller.install()
        driver = webdriver.Chrome(path, chrome_options=options)

        return driver

    def start(self):
        # for category_name in self.selected_categories:
        #     proc = Process(target=self.crawling, args=(category_name,))
        #     proc.start()
        pool = Pool(processes=len(self.selected_categories))
        articles = pool.map(self.get_total_URLs, self.selected_categories)
        pool.close()
        pool.join()
        print("Fin get URLs")
        for article, category_name in articles:
            article_split = np.array_split(
                article, multiprocessing.cpu_count())
            from functools import partial
            category_crawling = partial(
                self.crawling, category_name=category_name)
            pool = Pool(processes=multiprocessing.cpu_count())
            df = pd.concat(pool.map(category_crawling, article_split))
            # 메모리를 위해서
            pool.close()
            pool.join()
            df.to_csv(
                f"{os.path.join(DATA_DIR, str(7))}/{category_name}.csv")


if __name__ == '__main__':
    Crawler = SportsAttribute()
    Crawler.set_category("야구")
    Crawler.set_date()
    Crawler.start()
