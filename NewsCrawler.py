import argparse
import calendar
from datetime import datetime
from multiprocessing import Process
import os
import time
from typing import List

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

from Exceptions import *
from NewsParser import NewsParser


parser = argparse.ArgumentParser()
parser.add_argument('--startY', type=int, required=True)
parser.add_argument('--startM', type=int, required=True)
parser.add_argument('--endY', type=int, required=True)
parser.add_argument('--endM', type=int, required=True)
args = parser.parse_args()

DATA_DIR='./newsData'

class ArticleAttribute():
    """
    연예, 스포츠 기사 이외의 나머지 카테고리의 기사들을 BeautifulSoup로 Crawling

    Args:
        categoriesCode: 각 카테고리 페이지로 이동하기 위한 code
        categoriesFolder: 각 카테고리 기사를 저장하기 위한 번호
        selectedCategories: 실행중에 Crawling할 카테고리
        date: crwaling할 범위 start YY.MM ~ end YY.MM

    func:
        set_category: self.selectedCategories를 채워넣음
        set_date: self.date를 채워넣음
        make_newsURL_form: 정해진 기간동안 모든 기사의 URL을 저장
        file_write: 결과를 저장
        get_URLdata: URL에 접근
        crawling: 각 URL에 대해서 BeautifulSoup로 크롤링 진행
        start: crawling 함수 호출
    """
    def __init__(self):
        self.categoriesCode: dict = {"정치":100,"경제":101,"사회":102,"생활문화":103,"세계":104,"IT과학":105}
        self.categoriesFolder: dict = {"정치":0,"경제":1,"사회":2,"생활문화":3,"세계":4,"IT과학":5}
        self.selectedCategories: list = []
        self.date: dict = {'startYear': 0, 'startMonth': 0, 'endYear': 0, 'endMonth': 0}

    def set_category(self,*args):
        for key in args:
            if self.categoriesCode.get(key) is None:
                raise InvalidCategory
        self.selectedCategories = args

    def set_date(self, startYear: int, startMonth: int, endYear: int, endMonth:int):
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

    @staticmethod
    def make_newsURL_form(NewsURL: str, start_year: int, end_year: int, start_month: int, end_month: int)-> List[str]:
        madeURL=[]
        start, end = 1, 12 
        for year in range(start_year, end_year + 1):
            if start_year == end_year:
                start = start_month
                end = end_month
            else:
                if year == start_year:
                    start = start_month
                elif year == end_year:
                    end = end_month
            for month in tqdm(range(start, end + 1), desc = "Month Iteration"):
                for day in tqdm(range(1, calendar.monthrange(year,month)[1] + 1), desc = "Day Iteration"):
                    if len(str(month)) == 1:
                        month = '0' + str(month)
                    if len(str(day)) == 1:
                        day = '0' + str(day)
                    if datetime.now().month == month and datetime.now().year == year and int(datetime.now().day) < int(day):
                        continue
                    
                    url = NewsURL + str(year) + str(month) + str(day)

                    #끝페이지보다 더 큰 값을 이동하면 자동으로 마지막 페이지로 이동하게 된다.
                    totalpage = NewsParser.find_news_total_page(url+'&page=10000')
                    for page in range(1,totalpage+1):
                        madeURL.append(url+'&page='+str(page))
        return madeURL

    @classmethod
    def file_write(self, file_name:str, title: str, content: list):
        f = open(file_name,'w')
        f.write(title)
        f.write("\n")
        for c in content:
            f.write(c)
            f.write("\n")
        f.close()

    @staticmethod
    def get_URLdata(url: str, max_tries=10):
        header = {"User-Agent": "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url, headers=header)
            except:
                time.sleep(60)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout

    def crawling(self, category_name: str):
        print(str(os.getpid())+" : "+category_name+"\n")
        url= "http://news.naver.com/main/list.nhn?mode=LSD&mid=shm&sid1=" + str(self.categoriesCode.get(category_name)) + "&date="
        urls = self.make_newsURL_form(url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth']) 
        number = 0

        print("Crawling Start!")
        for url in urls:
            print(str(os.getpid())+" : "+url)
            page_html = self.get_URLdata(url)
            document = BeautifulSoup(page_html.content,'html.parser')

            #가운데의 줄을 기준으로 headline과 일반으로 나누어져 있음
            pages = document.select('.newsflash_body .type06_headline li dl')
            pages.extend(document.select('.newsflash_body .type06 li dl'))

            articles = []
            for line in pages:
                articles.append(line.a.get('href')) # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
            del pages

            for content_URL in tqdm(articles):  # 기사 URL
                # 크롤링 대기 시간
                time.sleep(0.01)
                
                # 기사 HTML 가져옴
                content_html = self.get_URLdata(content_URL)
                document_content = BeautifulSoup(content_html.content, 'html.parser')
                
                try:
                    # 기사 제목 가져옴
                    article_title = document_content.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                    title = ''  # 뉴스 기사 제목 초기화
                    title += NewsParser.clear_headline(str(article_title[0].find_all(text=True)))
                    if not title:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 본문 가져옴
                    article_body_contents = document_content.find_all('div', {'id': 'articleBodyContents'})
                    content = NewsParser.clear_content(list(article_body_contents[0].find_all(text=True)))
                    if not len(content):  # 공백일 경우 기사 제외 처리
                        continue

                    try:
                        if not(os.path.isdir(os.path.join(DATA_DIR, str(self.categoriesFolder.get(category_name))))):
                            os.makedirs(os.path.join(DATA_DIR, str(self.categoriesFolder.get(category_name))))
                            print("폴더 생성")
                    except OSError:
                        print("폴더 생성에 실패했습니다.")

                    file_name = DATA_DIR+'/' + str(self.categoriesFolder.get(category_name)) + '/'+category_name + str(number) + ".txt"
                    self.file_write(file_name, title, content)
                    number += 1

                    del content, title
                    del article_title, article_body_contents
                    del content_html, document_content

                except Exception:
                    del content_html, document_content
                    pass

    def start(self):
        # MultiProcess 크롤링
        for category_name in self.selectedCategories:
            proc = Process(target=self.crawling, args=(category_name,))
            proc.start()


if __name__ == "__main__":
    Crawler = ArticleAttribute()
    Crawler.set_category("정치","경제")
    Crawler.set_date(args.startY, args.startM, args.endY, args.endM)
    Crawler.start()
