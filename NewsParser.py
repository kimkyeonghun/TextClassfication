import requests
import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver

class NewsParser(object):
    options =webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    driverPath='./webdriver/chrome/chromedriver.exe'
    specialSymbol = re.compile(r'[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$&▲▶◆♥★◀■【】\\\=\(\'\"]')
    contentPattern = re.compile(r'본문 내용|TV플레이어|동영상 뉴스|   flash 오류를 우회하기 위한 함수 추가\nfunction  flash removeCallback     |tt|앵커 멘트|\xa0| 앵커 ')
    EntertainPattern=["포토","사진","SNS","뉴스엔TV","THE PHOTO","화보","영상","TEN PHOTO"]
    
    @classmethod
    def findNewsTotalpage(self,url):
        header = {"User-Agent": "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        try:
            totlapage_url = url
            request_content = requests.get(totlapage_url, headers= header)
            document_content = BeautifulSoup(request_content.content, 'html.parser')
            headline_tag = document_content.find('div', {'class': 'paging'}).find('strong')
            regex = re.compile(r'<strong>(?P<num>\d+)')
            match = regex.findall(str(headline_tag))
            return int(match[0])
        except Exception:
            return 0

    @classmethod
    def findNewsTotalpageS(self,urlS):
        try:
            driver = webdriver.Chrome(self.driverPath,chrome_options=self.options)
            driver.implicitly_wait(5)
            driver.get(urlS)
            driver.implicitly_wait(5)
            totalPage=driver.find_element_by_css_selector('#_pageList > strong')
            totalPage=int(totalPage.text)
            driver.quit()
            return totalPage
        except Exception:
            return 0

    @classmethod
    def clearHeadline(self,title):
        Ntitle = title.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        Ntitle = re.sub(self.specialSymbol, '', Ntitle)
        return Ntitle

    @classmethod
    def clearHeadlineE(self,title):
        Ntitle = title.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        Ntitle = re.sub(self.specialSymbol, '', Ntitle)
        for parser in self.EntertainPattern:
            if parser in Ntitle:
                Ntitle=''
                break
        return Ntitle

    @classmethod
    def clearContent(self,contents):
        content=[]
        for c in contents:
            Ncontent = c.strip()
            Ncontent = re.sub(self.specialSymbol, ' ', Ncontent)
            Ncontent = re.sub(self.contentPattern, '', Ncontent)
            Ncontent.strip()
            if Ncontent=='':
                continue
            content.append(Ncontent)
        while True:
            if content[-1][-2:]=='다.':
                break
            else:
                content.pop()
    
        return content

    @classmethod
    def clearContentS(self,contents):
        content=[]
        for c in contents:
            Ncontent = c.strip()
            Ncontent = re.sub(self.specialSymbol, ' ', Ncontent)
            Ncontent = re.sub(self.contentPattern, '', Ncontent)
            Ncontent.strip()
            if Ncontent=='':
                continue
            content.append(Ncontent)
        while True:
            if content[-1][-2:]=='다.':
                if content[-1]=='현장에서 작성된 기사입니다.':
                    content.pop()
                    continue
                break
            else:
                content.pop()
    
        return content