## 네이버 뉴스 기사 크롤러(Naver-News-Crawler)

Beautifulsoup와 Selenium을 사용한 네이버 뉴스 기사 크롤러 및 category classification를 진행했습니다. 네이버 뉴스 기사를 정해진 기간 내의 모든 기사를 크롤링할 수 있습니다. 학술 및 공부 목적으로 활용부탁드립니다.

- Python = 3.7
- bs4
- requests
- tqdm
- selenium
- chromedriver_autoinstaller
- numpy
- pandas

## 사전 준비 사항

1. Selenium
   - Selenium과 Chromedriver를 설치해야 합니다.
     - 이 때, Chromedriver의 webdriver 폴더를 같은 경로 내에 위치 시켜야 합니다.
     - ~~추후 자동다운로드 기능을 제공하도록 하겠습니다.~~
     - 자동다운로드 기능이 생겼습니다.

## 사용 방법

연예, 스포츠는 일반 기사와 다른 방식으로 크롤링을 수행하기 때문에 따로 분류하여 크롤링 합니다. 연예, 스포츠 기사는 bs4를 사용했을 경우 페이지 이동이 불가능했기 때문에 selenium을 사용했고, 일반 기사는 bs4를 사용했습니다.

또한 빠른 크롤링을 위해서 cpu_core에 개수에 따라 멀티프로세싱으로 크롤링 진행합니다. (기존 약 3시간 -> 변경 후 약 45분 core 8개 기준)

1. 일반 기사(정치, 경제 등)
   - NewsCrawler.py
     - 파일 실행시 시작연도, 월, 종료연도, 월을 입력해야 합니다.
     - 카테고리는 정치, 경제, 사회, 생활문화, 세계, IT과학을 지원하며 지금은 코드내에서 수정해서 선택적으로 크롤링할 수 있습니다.
       - 추후 구현하도록 하겠습니다.
2. 연예 기사
   - entertainCrawler.py
     - 파일 실행시 시작연도, 월, 종료연도, 월을 입력해야 합니다. -> NewsCralwer.py에만 적용
     - selenium을 사용해서 크롤링하기 때문에 selenium 설치가 필요합니다.
3. 스포츠 기사
   - sportsCrawler.py
     - 파일 실행시 시작연도, 월, 종료연도, 월을 입력해야 합니다. -> NewsCralwer.py에만 적용
     - selenium을 사용해서 크롤링하기 때문에 selenium 설치가 필요합니다.


## 2022년 추가 사항

investing.com 홈페이지에서 각 종목별 기사들을 Crawling 하는 코드를 개발중에 있습니다.