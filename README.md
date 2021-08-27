## 네이버 뉴스 기사 크롤러(Naver-News-Crawler)

Beautifulsoup와 Selenium을 사용한 네이버 뉴스 기사 크롤러 및 category classification를 진행했습니다. 네이버 뉴스 기사를 정해진 기간 내의 모든 기사를 크롤링할 수 있습니다. 학술 및 공부 목적으로 활용부탁드립니다.

- Python = 3.7
- bs4
- requests
- tqdm

## 사전 준비 사항

1. Selenium
   - Selenium과 Chromedriver를 설치해야 합니다.
     - 이 때, Chromedriver의 webdriver 폴더를 같은 경로 내에 위치 시켜야 합니다.
     - 추후 자동다운로드 기능을 제공하도록 하겠습니다.

## 사용 방법

연예, 스포츠는 일반 기사와 다른 방식으로 크롤링을 수행하기 때문에 따로 분류하여 크롤링 합니다. 연예, 스포츠 기사는 bs4를 사용했을 경우 페이지 이동이 불가능했기 때문에 selenium을 사용했고, 일반 기사는 bs4를 사용했습니다.

1. 일반 기사(정치, 경제 등)
   - NewsCrawler.py
     - args.startY, args.startM, args.endY,  args.endM 가 필요합니다.
     - 카테고리는 정치, 경제, 사회, 생활문화, 세계, IT과학을 지원하며 지금은 코드내에서 수정해서 선택적으로 크롤링할 수 있습니다.
       - 추후 구현하도록 하겠습니다.
2. 연예 기사
   - entertainCrawler.py
     - args.startY, args.startM, args.endY,  args.endM 가 필요합니다.
     - selenium을 사용해서 크롤링하기 때문에 selenium 설치가 필요합니다.
3. 스포츠 기사
   - sportsCrawler.py
     - args.startY, args.startM, args.endY,  args.endM 가 필요합니다.
     - selenium을 사용해서 크롤링하기 때문에 selenium 설치가 필요합니다.