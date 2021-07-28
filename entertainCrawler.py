import argparse
import calendar
from datetime import datetime
import os
from multiprocessing import Process
import time
from typing import List

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from tqdm import tqdm

from Exceptions import *
from NewsParser import NewsParser

parser = argparse.ArgumentParser()
parser.add_argument('--startY', type=int, required=True)
parser.add_argument('--startM', type=int, required=True)
parser.add_argument('--endY', type=int, required=True)
parser.add_argument('--endM', type=int, required=True)
args = parser.parse_args()

DATA_DIR = './newsData/6'

DRIVER_PATH='./webdriver/chrome/chromedriver.exe'

class EntertainAttribute():
    number = 0
    def __init__(self):
        self.category_code = {"연예" : 106}
        self.selected_categories = []
        self.date = {'startYear': 0, 'startMonth': 0, 'endYear': 0, 'endMonth': 0}

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

        for key,date in zip(self.date,args):
            self.date[key] = date
    
    def set_category(self,*args):
        for key in args:
            if self.category_code.get(key) is None:
                raise InvalidCategory
        self.selected_categories = args

    def set_driver_option(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
            #options.add_argument('--start-maximized')
        driver = webdriver.Chrome(DRIVER_PATH, chrome_options = options)
        return driver

    @staticmethod
    def make_newsURL_form(NewsURL: str, startYear: int, endYear: int, startMonth: int, endMonth: int) -> List[str]:
        madeURL=[]
        start, end = 1, 12 
        for year in range(startYear, endYear + 1):
            if startYear == endYear:
                start = startMonth
                end = endMonth
            else:
                if year == startYear:
                    start = startMonth
                elif year == endYear:
                    end = endMonth
            
            for month in tqdm(range(start, end + 1), desc = "Month Iteration"):
                for day in tqdm(range(1, calendar.monthrange(year, month)[1] + 1), desc = "Day Iteration"):
                    if len(str(month)) == 1:
                        month = '0' + str(month)
                    if len(str(day)) == 1:
                        day = '0' + str(day)
                    if datetime.now().month == month and datetime.now().year == year and int(datetime.now().day) < int(day):
                        continue
                    
                    url = NewsURL + str(year)+ '-' + str(month)+ '-' + str(day)

                    #끝페이지보다 더 큰 값을 이동하면 자동으로 마지막 페이지로 이동하게 된다.
                    madeURL.append(url)
        return madeURL

    @classmethod
    def file_write(self, file_name: str, title: str, content: list):
        f = open(file_name,'w')
        f.write(title)
        f.write("\n")
        
        for c in content:
            f.write(c)
            f.write("\n")
        f.close()

    @staticmethod
    def get_URLdata(url: str, max_tries=10):
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url)
            except:
                time.sleep(60)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout


    def crawling(self, parse_URLs: str):
        print("Crawling Start!")
        for url in parse_URLs:
            pageN=1
            driver = self.set_driver_option()
            end=True
            while end:
                articles=[]
                driver.get(url+"&page="+str(pageN))
                print(str(os.getpid())+":"+url+"&page="+str(pageN))
                time.sleep(1.5)
                pages = driver.find_elements_by_css_selector('#newsWrp > ul > li')
                try:
                    for page in pages:
                        articles.append(page.find_element_by_css_selector('a').get_attribute('href'))
                    del pages

                    for content_URL in articles:
                        time.sleep(0.01)

                        content_html = self.get_URLdata(content_URL)
                        document_content = BeautifulSoup(content_html.content, 'html.parser')

                        try:
                            article_title = document_content.find_all('h2', {'class': 'end_tit'})
                            title = ''
                            title += NewsParser.clear_headlineE(str(article_title[0].find_all(text=True)))
                            if not title:
                                continue

                            article_body_contents = document_content.find_all("div", {"id": "articeBody"})
                            content = NewsParser.clear_content(list(article_body_contents[0].find_all(text=True)))
                            if not content:
                                continue
                                
                            file_name = DATA_DIR+'/'+str(os.getpid())+'_'+str(self.number)+".txt"
                            self.file_write(file_name, title, content)
                            self.number += 1

                            del content, title
                            del article_title, article_body_contents
                            del content_html, document_content

                        except Exception:
                            del content_html, document_content
                            pass

                    del articles
                except:
                    end = False
                pageN += 1

            driver.quit()

    def start(self):
        try:
            if not(os.path.isdir(DATA_DIR)):
                os.makedirs(DATA_DIR)
                print("폴더 생성")
        except OSError:
            print("폴더 생성에 실패했습니다.")
        
        for category_name in self.selected_categories:
            url = "https://entertain.naver.com/now#sid=" + str(self.category_code.get(category_name)) + "&date="
            urls = self.make_newsURL_form(url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth'])
            totalURLs = len(urls)
            for i in range(0, totalURLs, 10):
                parseURLs = urls[i: i + 10]
                proc = Process(target = self.crawling, args = (parseURLs,))
                proc.start()

if __name__ == '__main__':
    Crawler = EntertainAttribute()
    Crawler.set_category("연예")
    Crawler.set_date(args.startY, args.startM, args.endY, args.endM)
    Crawler.start()

