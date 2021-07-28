import re

from bs4 import BeautifulSoup
import requests
from selenium import webdriver

DRIVERT_PATH='./webdriver/chrome/chromedriver.exe'

class NewsParser(object):
    options = webdriver.ChromeOptions()
    #에러 로그 출력 제외(에러 로그 뿐만 아니라 모든 셀레니움 로그 출력 제외인듯)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_argument('headless')
    options.add_argument('disable-gpu')
    special_symbol = re.compile(r'[\{\}\[\]\/?,;:|\)*~`!^\-_+<>@\#$&▲▶◆♥★◀■【】\\\=\(\'\"]')
    content_pattern = re.compile(r'본문 내용|TV플레이어|동영상 뉴스|   flash 오류를 우회하기 위한 함수 추가\nfunction  flash removeCallback     |tt|앵커 멘트|\xa0| 앵커 ')
    entertain_pattern = ["포토", "사진", "SNS", "뉴스엔TV", "THE PHOTO", "화보", "영상", "TEN PHOTO"]
    
    @classmethod
    def find_news_total_page(self, url):
        header = {"User-Agent": "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        try:
            totlapage_url = url
            request_content = requests.get(totlapage_url, headers = header)
            document_content = BeautifulSoup(request_content.content, 'html.parser')
            headline_tag = document_content.find('div', {'class': 'paging'}).find('strong')
            regex = re.compile(r'<strong>(?P<num>\d+)')
            match = regex.findall(str(headline_tag))
            return int(match[0])
        except Exception:
            return 0

    @classmethod
    def find_news_total_pageS(self, urlS):
        try:
            driver = webdriver.Chrome(DRIVERT_PATH, chrome_options = self.options)
            driver.implicitly_wait(5)
            driver.get(urlS)
            driver.implicitly_wait(5)
            total_page = driver.find_element_by_css_selector('#_pageList > strong')
            total_page = int(total_page.text)
            driver.quit ()
            return total_page
        except Exception:
            return 0

    @classmethod
    def clear_headline(self, title):
        Ntitle = title.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        Ntitle = re.sub(self.special_symbol, '', Ntitle)
        return Ntitle

    @classmethod
    def clear_headlineE(self, title):
        Ntitle = title.replace('\\n', '').replace('\\t', '').replace('\\r', '')
        Ntitle = re.sub(self.special_symbol, '', Ntitle)
        for parser in self.entertain_pattern:
            if parser in Ntitle:
                Ntitle=''
                break
        return Ntitle

    @classmethod
    def clear_content(self, contents):
        content = []
        for c in contents:
            Ncontent = c.strip()
            Ncontent = re.sub(self.special_symbol, ' ', Ncontent)
            Ncontent = re.sub(self.content_pattern, '', Ncontent)
            Ncontent.strip()
            if Ncontent=='':
                continue
            content.append(Ncontent)
        while True:
            if content[-1][-2:] == '다.':
                break
            else:
                content.pop()
        return content

    @classmethod
    def clear_contentS(self, contents):
        content = []
        for c in contents:
            Ncontent = c.strip()
            Ncontent = re.sub(self.special_symbol, ' ', Ncontent)
            Ncontent = re.sub(self.content_pattern, '', Ncontent)
            Ncontent.strip()
            if Ncontent == '':
                continue
            content.append(Ncontent)
        while True:
            if content[-1][-2:] == '다.':
                if content[-1] == '현장에서 작성된 기사입니다.':
                    content.pop()
                    continue
                break
            else:
                content.pop()
        return content