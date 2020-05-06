import re
import os
import time
import requests
import calendar
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
from Exceptions import *
from multiprocessing import Process
from NewsParser import NewsParser
from selenium import webdriver

class SportsAttribute():
    def __init__(self):
        self.driverPath='./webdriver/chrome/chromedriver.exe'
        self.categoryCode={"야구":"kbaseball",'해외야구':'wbaseball','축구':'kfootball','해외축구':'wfootball',
        '농구':'basketball','배구':'volleyball','골프':'golf','일반':'general','e스포츠':'esports'}
        self.selectedCategories=[]
        self.date ={'startYear': 0, 'startMonth': 0, 'endYear': 0, 'endMonth': 0}
        self.DATA_DIR='./newsData/7'

    def setCategory(self,*args):
        for key in args:
            if self.categoryCode.get(key) is None:
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
            
            for month in range(start,end+1):
                for day in range(1,calendar.monthrange(year,month)[1]+1):
                    if len(str(month)) == 1:
                        month = '0' + str(month)
                    if len(str(day)) == 1:
                        day = '0' + str(day)
                    if datetime.now().month == month and datetime.now().year == year and int(datetime.now().day) < int(day):
                        continue
                    
                    url = NewsURL + str(year) + str(month) + str(day)

                    #끝페이지보다 더 큰 값을 이동하면 자동으로 마지막 페이지로 이동하게 된다.
                    totalpage = NewsParser.findNewsTotalpageS(url+'&page=10000')
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
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            try:
                return requests.get(url)
            except:
                time.sleep(60)
            remaining_tries = remaining_tries - 1
        raise ResponseTimeout

    def crawling(self,categoryName):
        print(str(os.getpid())+" : "+categoryName+'\n')
        url= "http://sports.news.naver.com/"+str(self.categoryCode.get(categoryName))+"/news/index.nhn?isphoto=N&date="
        urls = self.makeNewsURLForm(url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth']) 
        number = 0

        print("Crawling Start!")
        for url in tqdm(urls):
            print(str(os.getpid())+" : "+url)
            options =webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('disable-gpu')
            driver = webdriver.Chrome(self.driverPath,chrome_options=options)
            driver.implicitly_wait(2)
            driver.get(url)
            driver.implicitly_wait(2)
            pages=driver.find_elements_by_css_selector('#_newsList > ul >li')

            articles=[]
            for page in pages:
                articles.append(page.find_element_by_css_selector('a').get_attribute('href'))
            del pages
            driver.quit()
            for contentURL in articles:
                time.sleep(0.05)

                contentHtml = self.getURLdata(contentURL)
                documentContent = BeautifulSoup(contentHtml.content, 'html.parser')

                try:
                    # 기사 제목 가져옴
                    articleTitle = documentContent.find_all('h4',{'class': 'title'})
                    title = ''  # 뉴스 기사 제목 초기화
                    title += NewsParser.clearHeadline(str(articleTitle[0].find_all(text=True)))
                    if not title:  # 공백일 경우 기사 제외 처리
                        continue

                    # 기사 본문 가져옴
                    articleBodyContents = documentContent.find_all('div', {'id': 'newsEndContents'})
                    content = NewsParser.clearContentS(list(articleBodyContents[0].find_all(text=True)))
                    if not len(content):  # 공백일 경우 기사 제외 처리
                        continue

                    try:
                        if not(os.path.isdir(self.DATA_DIR)):
                            os.makedirs(self.DATA_DIR)
                            print("폴더 생성")
                    except OSError:
                        print("폴더 생성에 실패했습니다.")


                    fileName = self.DATA_DIR+'/'+categoryName+str(number)+".txt"
                    self.fileWrite(fileName,title,content)
                    number+=1

                    del content, title
                    del articleTitle, articleBodyContents
                    del contentHtml, documentContent

                except Exception:
                    del contentHtml, documentContent
                    pass


    def start(self):
        for categoryName in self.selectedCategories:
            proc = Process(target=self.crawling, args=(categoryName,))
            proc.start()

if __name__=='__main__':
    Crawler = SportsAttribute()
    Crawler.setCategory("야구")
    Crawler.setDate(2019, 11, 2019, 11)
    Crawler.start()

