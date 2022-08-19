from selenium import webdriver
from selenium.webdriver.common.by import By

from time import sleep

import requests

from bs4 import BeautifulSoup
import random

import pandas as pd

"""
1. ticker list update
2. ip 우회?
"""


def get_content(news_href, investing_url):
    articles_href = investing_url+news_href
    req = requests.get(articles_href, headers=header)
    if req.status_code == 200:
        html = req.text
        soup2 = BeautifulSoup(html, 'html.parser')
        release_time = soup2.find(
            'div', class_='contentSectionDetails').find('span').text
        contents = soup2.find(
            'div', class_='WYSIWYG articlePage').find_all(['p', 'ul'])
        text = ''
        for content in contents:
            if content.text.startswith('By'):
                continue
            if content.find('a') and "Continue reading" in content.find('a').text:
                return False, False
            text += content.text + '\n'
        return text, release_time


header = {"User-Agent": "Mozilla/5.0"}

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = webdriver.Chrome('./chromedriver.exe', options=options)

investing_url = "https://www.investing.com"

data_rows = []
unique_id = 0
tickers = ['TSLA']
for ticker in tickers:
    driver.get(investing_url)
    driver.implicitly_wait(5)
    search = driver.find_element(
        by=By.XPATH, value='/html/body/div[5]/header/div[2]/div/div[3]/div[1]/input')
    search.send_keys(ticker)
    driver.implicitly_wait(5)
    rows = driver.find_element(
        by=By.XPATH, value='/html/body/div[5]/header/div[2]/div/div[3]/div[2]/div[1]/div[1]/div[2]/div')
    for row in rows.find_elements(by=By.TAG_NAME, value='a'):
        if 'USA' in row.find_element(by=By.TAG_NAME, value='i').get_attribute('class'):
            href = row.get_attribute('href')
            print(href)
            break
    # driver.get(href+"-news")
    page = 1
    sleep(6)
    driver.quit()
    href = href+'-news'+"/"+str(page)
    while True:
        req = requests.get(href, headers=header)
        sleep(0.5)
        if req.status_code == 200:
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.select("#leftColumn > div.mediumTitle1 > article")
            if len(articles) == 0:
                print("Last Page")
                break

            for article in articles:
                unique_id += 1
                article_id = article['data-id']
                infos = article.find('div', class_='textDiv')
                news_href = infos.find('a')['href']
                # Pro version 기사 skip
                if news_href.startswith('/pro'):
                    print(news_href)
                    continue
                news_title = infos.find('a')['title']
                provider = infos.find('span').find('span').text.split()[1]
                sleep(random.random())
                # 외부 사이트 이동하는 provider skip 필요
                if provider in ['Seeking Alpha']:
                    continue
                text, release_time = get_content(news_href, investing_url)
                sleep(random.random())
                data_rows.append((unique_id, ticker, provider,
                                 news_href, release_time, news_title, text))
            page += 1
            try:
                next = soup.find(
                    'div', class_='sideDiv inlineblock text_align_lang_base_2').find('a')['href']
                href = investing_url + next
            except:
                print("No Next")
                break
        else:
            print("Wrong Connection")
            break

df = pd.DataFrame(data_rows, columns=[
                  'article_id', 'Ticker', 'provider', 'url', 'release_time', 'title', 'content'])
df.to_csv("./results_crawl.csv")
