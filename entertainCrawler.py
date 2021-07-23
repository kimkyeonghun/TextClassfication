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
from selenium import webdriver


class EntertainAttribute():
    number = 0
    def __init__(self):
        self.categoryCode = {"연예":106}
        self.categoriesFolder = {"연예":6}
        self.selectedCategories = []
        self.date = {'startYear': 0, 'startMonth': 0, 'endYear': 0, 'endMonth': 0}
        self.DATA_DIR='./newsData/6'
        self.driverPATH='./webdriver/chrome/chromedriver.exe'
        

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
    
    def setCategory(self,*args):
        for key in args:
            if self.categoryCode.get(key) is None:
                raise InvalidCategory
        self.selectedCategories = args
    

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
                    
                    url = NewsURL + str(year)+ '-' + str(month)+ '-' + str(day)

                    #끝페이지보다 더 큰 값을 이동하면 자동으로 마지막 페이지로 이동하게 된다.
                    madeURL.append(url)
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


    def crawling(self,parseURLs):
        print("Crawling Start!")
        for url in parseURLs:
            pageN=1
            options =webdriver.ChromeOptions()
            options.add_argument('headless')
            options.add_argument('disable-gpu')
            options.add_argument('--start-maximized')
            driver=webdriver.Chrome(self.driverPATH,chrome_options=options)
            end=True
            while end:
                articles=[]
                driver.get(url+"&page="+str(pageN))
                print(str(os.getpid())+":"+url+"&page="+str(pageN))
                time.sleep(1.5)
                pages=driver.find_elements_by_css_selector('#newsWrp > ul > li')
                try:
                    for page in pages:
                        articles.append(page.find_element_by_css_selector('a').get_attribute('href'))
                    del pages

                    for contentURL in articles:
                        time.sleep(0.01)

                        contentHtml = self.getURLdata(contentURL)
                        documentContent = BeautifulSoup(contentHtml.content, 'html.parser')

                        try:
                            articleTitle = documentContent.find_all('h2',{'class': 'end_tit'})
                            title = ''
                            title += NewsParser.clearHeadlineE(str(articleTitle[0].find_all(text=True)))
                            if not title:
                                continue

                            articleBodyContents = documentContent.find_all("div",{"id":"articeBody"})
                            content = NewsParser.clearContent(list(articleBodyContents[0].find_all(text=True)))
                            if not content:
                                continue
                                
                            fileName = self.DATA_DIR+'/'+str(os.getpid())+'_'+str(self.number)+".txt"
                            self.fileWrite(fileName,title,content)
                            self.number += 1

                            del content, title
                            del articleTitle, articleBodyContents
                            del contentHtml, documentContent

                        except Exception:
                            del contentHtml, documentContent
                            pass
                    del articles
                except:
                    end=False
                pageN+=1
            driver.quit()


    def start(self):
        try:
            if not(os.path.isdir(self.DATA_DIR)):
                os.makedirs(self.DATA_DIR)
                print("폴더 생성")
        except OSError:
            print("폴더 생성에 실패했습니다.")
        
        for categoryName in self.selectedCategories:
            url= "https://entertain.naver.com/now#sid=" + str(self.categoryCode.get(categoryName)) + "&date="
            urls = self.makeNewsURLForm(url, self.date['startYear'], self.date['endYear'], self.date['startMonth'], self.date['endMonth'])
            totalURLs=len(urls)
            for i in range(0,totalURLs,10):
                parseURLs = urls[i:i+10]
                proc = Process(target=self.crawling, args=(parseURLs,))
                proc.start()

if __name__ == '__main__':
    Crawler = EntertainAttribute()
    Crawler.setCategory("연예")
    Crawler.setDate(2019, 7, 2019, 11)
    Crawler.start()

