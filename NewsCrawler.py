import os
import re
import time
import calendar
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from multiprocessing import Process
from tqdm import tqdm
from Exceptions import *
from NewsParser import NewsParser


class ArticleAttribute():
    def __init__(self):
        self.categoriesCode = {"정치":100,"경제":101,"사회":102,"생활문화":103,"세계":104,"IT과학":105}
        self.categoriesFolder = {"정치":0,"경제":1,"사회":2,"생활문화":3,"세계":4,"IT과학":5}
        self.selectedCategories = []
        self.date = {'startYear': 0, 'startMonth': 0, 'endYear': 0, 'endMonth': 0}
        self.DATA_DIR='./newsData'
        
    def setCategory(self,*args):
        for key in args:
            if self.categoriesCode.get(key) is None:
                raise InvalidCategory
        self.selectedCategories = args

    def setDate(self,startYear,startMonth,endYear,endMonth):
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
    def makeNewsURLForm(NewsURL, startYear, endYear, startMonth, endMonth):
        madeURL=[]
        start, end = 1, 12 
        for year in range(startYear,endYear+1):
            if startYear == endYear:
                start = startMonth
                end = endMonth
            else:
                if year == startYear:
                    start = startMonth
                elif year == endYear:
                    end = endMonth
            for month in tqdm(range(start,end+1),desc="Month Iteration"):
                for day in tqdm(range(1,calendar.monthrange(year,month)[1]+1),desc="Day Iteration"):
                    if len(str(month)) == 1:
                        month = '0' + str(month)
                    if len(str(day)) == 1:
                        day = '0' + str(day)
                    if datetime.now().month == month and datetime.now().year == year and int(datetime.now().day) < int(day):
                        continue
                    
                    url = NewsURL + str(year) + str(month) + str(day)

                    #끝페이지보다 더 큰 값을 이동하면 자동으로 마지막 페이지로 이동하게 된다.
                    totalpage = NewsParser.findNewsTotalpage(url+'&page=10000')
                    for page in range(1,totalpage+1):
                        madeURL.append(url+'&page='+str(page))
        return madeURL

    @classmethod
    def fileWrite(self,fileName,title,content):
        f = open(fileName,'w')
        f.write(title)
        f.write("\n")
        for c in content:
            f.write(c)
            f.write("\n")
        f.close()

    @staticmethod
    def getURLdata(url, max_tries=10):
        header = {"User-Agent": "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url, headers=header)
            except:
                time.sleep(60)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout

    def crawling(self,categoryName):
        print(str(os.getpid())+" : "+categoryName+"\n")
        url= "http://news.naver.com/main/list.nhn?mode=LSD&mid=shm&sid1=" + str(self.categoriesCode.get(categoryName)) + "&date="
        urls = self.makeNewsURLForm(url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth']) 
        number=0

        print("Crawling Start!")
        for url in urls:
            print(str(os.getpid())+" : "+url)
            pageHtml = self.getURLdata(url)
            document = BeautifulSoup(pageHtml.content,'html.parser')

            #가운데의 줄을 기준으로 headline과 일반으로 나누어져 있음
            pages = document.select('.newsflash_body .type06_headline li dl')
            pages.extend(document.select('.newsflash_body .type06 li dl'))

            articles = []
            for line in pages:
                articles.append(line.a.get('href')) # 해당되는 page에서 모든 기사들의 URL을 post 리스트에 넣음
            del pages

            for contentURL in tqdm(articles):  # 기사 URL
                # 크롤링 대기 시간
                time.sleep(0.01)
                
                # 기사 HTML 가져옴
                contentHtml = self.getURLdata(contentURL)
                documentContent = BeautifulSoup(contentHtml.content, 'html.parser')
                
                try:
                    # 기사 제목 가져옴
                    articleTitle = documentContent.find_all('h3', {'id': 'articleTitle'}, {'class': 'tts_head'})
                    title = ''  # 뉴스 기사 제목 초기화
                    title += NewsParser.clearHeadline(str(articleTitle[0].find_all(text=True)))
                    if not title:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 본문 가져옴
                    articleBodyContents = documentContent.find_all('div', {'id': 'articleBodyContents'})
                    content = NewsParser.clearContent(list(articleBodyContents[0].find_all(text=True)))
                    if not len(content):  # 공백일 경우 기사 제외 처리
                        continue

                    try:
                        if not(os.path.isdir(os.path.join(self.DATA_DIR,str(self.categoriesFolder.get(categoryName))))):
                            os.makedirs(os.path.join(self.DATA_DIR,str(self.categoriesFolder.get(categoryName))))
                            print("폴더 생성")
                    except OSError:
                        print("폴더 생성에 실패했습니다.")

                    fileName = self.DATA_DIR+'/'+str(self.categoriesFolder.get(categoryName))+'/'+categoryName+str(number)+".txt"
                    self.fileWrite(fileName,title,content)
                    number+=1

                    del content, title
                    del articleTitle, articleBodyContents
                    del contentHtml, documentContent

                except Exception:
                    del contentHtml, documentContent
                    pass

    def start(self):
        # MultiProcess 크롤링
        for categoryName in self.selectedCategories:
            proc = Process(target=self.crawling, args=(categoryName,))
            proc.start()


if __name__ == "__main__":
    Crawler = ArticleAttribute()
    Crawler.setCategory("정치","경제")
    Crawler.setDate(2019, 11, 2019, 11)
    Crawler.start()
