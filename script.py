import requests
from bs4 import BeautifulSoup
# url = "https://www.sothebys.com/en/buy/auction/2020/watches-online-2/rolex-panama-canal-submariner-ref-16613-limited"
# url = 'http://dataquestio.github.io/web-scraping-pages/simple.html'
url = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/'

ua = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=ua)
print("Response code:", response.status_code)
soup = BeautifulSoup(response.content, 'html.parser')
estimate_container = soup.find('p', attrs={'class': 'css-1g8ar3q'})
print("Estimate:", estimate_container)
