from selenium import webdriver
from selenium.webdriver.common.by import By

from time import sleep

import requests

from bs4 import BeautifulSoup
import random

"""
1. 결과물 정리하는 코드 추가해야함
2. ticker list update
3. ip 우회?
"""

def get_content(news_href, investing_url):
    articles_href = investing_url+news_href
    req = requests.get(articles_href, headers=header)
    if req.status_code == 200:
        html = req.text
        soup2 = BeautifulSoup(html, 'html.parser')
        release_time = soup2.find('div',class_='contentSectionDetails').text
        contents = soup2.find('div',class_='WYSIWYG articlePage').find_all(['p','ul'])
        text = ''
        for content in contents:
            if content.find('a') and "Continue reading" in content.find('a').text:
                return False, False
            text += content.text + ' '
        return text, release_time

header = {"User-Agent": "Mozilla/5.0"}

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome('./chromedriver.exe', options=options)

investing_url = "https://www.investing.com"

tickers = ['TSLA']
for ticker in tickers:
    driver.get(investing_url)
    driver.implicitly_wait(5)
    search = driver.find_element(by=By.XPATH, value='/html/body/div[4]/header/div[2]/div/div[3]/div[1]/input')
    search.send_keys(ticker)
    driver.implicitly_wait(5)
    rows = driver.find_element(by=By.XPATH, value= '/html/body/div[4]/header/div[2]/div/div[3]/div[2]/div[1]/div[1]/div[2]/div')
    for row in rows.find_elements(by=By.TAG_NAME, value='a'):
        if 'USA' in row.find_element(by=By.TAG_NAME, value='i').get_attribute('class'):
            href = row.get_attribute('href')
            print(href)
            break
    # driver.get(href+"-news")
    page = 1
    while True:
        req = requests.get(href+'-news'+"/"+str(page), headers = header)
        sleep(0.5)
        if req.status_code==200:
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.select("#leftColumn > div.mediumTitle1 > article")
            if len(articles) == 0:
                print("Last Page")
                break

            for article in articles:
                article_id = article['data-id']
                infos = article.find('div',class_='textDiv')
                news_href = infos.find('a')['href']
                news_title = infos.find('a')['title']
                provider = infos.find('span').find('span').text
                sleep(random.random())
                if provider in ['Seeking Alpha']:
                    continue
                text, release_time = get_content(news_href, investing_url)
                sleep(random.random())
            page+=1
            try:
                next = soup.find('div', class_='sideDiv inlineblock text_align_lang_base_2').find('a')['href']
                if investing_url + next != href+'-news'+"/"+str(page):
                    break
                href = investing_url + next
            except:
                print("No Next")
                break
        else:
            print("Wrong Connection")
            break

sleep(6)
driver.quit()