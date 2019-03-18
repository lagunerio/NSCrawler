import requests
import csv
from bs4 import BeautifulSoup
import sys
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf-8')

RESULT_FILE_PATH = "" # CSV FILE PATH TO SAVE RESULT
URL_FILE_PATH = ""  # CSV FILE PATH OF URLS
LOG_FILE_PATH = ""  # LOG FILE PATH
FIELDNAMES = ['data_expose_id', 'price', 'shippingfee', 'productname', 'category', 'seller', 'reviews', 'picks'] # SET CSV FIELDNAMES

# USER AGENT SETTING
headers = {
    'User-Agent': ''  # USER AGENT STRING
}
RANGE = 100 # SET SEARCHING RANGE OF PAGE INDEX 

class Crawler:
    def __init__(self, url, filepath):
        self.url = url
        self.filepath = filepath
        self.item = {'data_expose_id':'', 'price':'', 'shippingfee':'', 'productname':'', 'category':'', 'seller':'', 'reviews':'', 'picks':''}

    def scrap(self):
        WriteLog("URL : " + self.url)
        with open(self.filepath, 'a') as f:
            # set csv writer
            writer = csv.DictWriter(f, delimiter=';', fieldnames=FIELDNAMES)

            # set BeautifulSoup
            html = requests.get(self.url, headers=headers).text
            soup = BeautifulSoup(html, 'html.parser')

            # set parameters
            i = 0
            prev = {'data_expose_id':'test prev', 'price':'', 'shippingfee':'', 'productname':'', 'category':'', 'seller':'', 'reviews':'', 'picks':''}
            curr = {'data_expose_id':'test curr', 'price':'', 'shippingfee':'', 'productname':'', 'category':'', 'seller':'', 'reviews':'', 'picks':''}

            while True:
                # get price
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ') > div.info > span.price > em > span.num._price_reload')
                for t in tmp:
                    self.item['price'] = t.text.strip()
                    break

                # get productname
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ') > div.info > a')
                for t in tmp:
                    self.item['productname'] = t.text.strip()
                    break

                # get product id (data expose id)
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ')')
                for t in tmp:
                    self.item['data_expose_id'] = t.get('data-expose-id')
                    break

                # get category
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ') > div.info > span.depth > a')
                cat = ""
                for t in tmp:
                    cat += (t.text + ">")
                self.item['category'] = cat[:-1]

                # get shipping fee
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ') > div.info_mall > ul > li:nth-child(2) > em')
                for t in tmp:
                    self.item['shippingfee'] = t.text.strip()
                    break

                # get seller
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ') > div.info_mall > p > a.btn_detail._btn_mall_detail')
                for t in tmp:
                    self.item['seller'] = t.get('data-mall-name').strip()

                # count reviews
                tmp = soup.select('#_search_list > div.search_list.basis > ul > li:nth-child(' + str(i) + ') > div.info > span.etc > a.graph > em')
                for t in tmp:
                    self.item['reviews'] = t.text.strip()

                # insert item dictionary to items list
                curr = self.item
                if curr==prev:
                    break
                else:
                    if self.item['data_expose_id']!='': # DO NOT SAVE EMPTY DATA
                        writer.writerow(self.item)
                        prev = curr
                    self.item = {'data_expose_id':'', 'price':'', 'shippingfee':'', 'productname':'', 'category':'', 'seller':'', 'reviews':'', 'picks':''}
                    i += 1

# GET URLS AS LIST FROM URL_FILE_PATH
def GetUrl():
    urls = []
    with open(URL_FILE_PATH, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            urls.extend(row)
    return urls

# WRITE LOG TO LOG_FILE_PATH
def WriteLog(string):
    with open(LOG_FILE_PATH, 'a') as f:
        f.write(">> " + str(datetime.now()) + "\n")
        f.write(str(string) + "\n")

def main():
    # EMPTY RESULT_FILE_PATH BEFORE CRAWLING AND WRITE HEADER
    with open(RESULT_FILE_PATH, 'w') as f:
        writer = csv.DictWriter(f, delimiter=';', fieldnames=FIELDNAMES)
        writer.writeheader()
        WriteLog("reset file: " + RESULT_FILE_PATH)

    for url in GetUrl():
        for i in range(1,RANGE):  # SEARCH URLS WHERE PAGE INDEX IS IN THE RANGE
            full_url = url + str(i) # ADD PAGE INDEX TO URL
            crawler = Crawler(full_url, RESULT_FILE_PATH)
            crawler.scrap()
            i += 1
        i = 0

if __name__=="__main__":
    main()


