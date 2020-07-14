# LOGBOEK:
# 21:30 - 22:30

# TODO: 
# Pick a site DONE
# Analyze pagem DONE
# Write code 

# Choices:
    # Antiquorum (most data) => seems easy lets try
    # Bonhams
    # Christies

# Analyze page:
# This url lists all the auctions https://catalog.antiquorum.swiss/
# We first need to scrape all the auction price list url (for the first batch, aftwards will do without price list)
# If we have all the auction price list url, we can than scrape all the urls per lot from this page. 
# So now we end up with a big list of url's to scrape. 
# I've already noticed some differences in the lot pages, so I should do a test run on that. 
# When we have the big list of url's to scrape we can just use the other file and easy peasy. 

import requests
import re
import time
import os
import pandas as pd
from bs4 import BeautifulSoup
from openpyxl import Workbook
from selenium import webdriver
from dataclasses import dataclass

class Lot:
    "A lot of a auction"

    def __init__(self, lot_number = None, url = None):
        self.lot_number = lot_number
        self.url = url

    def __repr__(self):  
        return "\nlot_number: %s \nurl: %s" % (self.lot_number, self.url)      

@dataclass
class Watch: 
    "A watch sold at the auction"

    def __init__(self, manufacturer = None, year = None, reference_number = None, model_name = None, currency = None, sold_for = None, estimate_minimum = None, estimate_maximum = None, date_sold = None, material = None, case_number = None, description_condition = None, diameter = None, movement_number = None, calibre = None, bracelet_strap = None, accessoires = None, signed = None, auction_title = None, lot_number = None, url = None):
        # Mandatory
        self.manufacturer = manufacturer
        self.year = year
        self.reference_number = reference_number
        self.model_name = model_name
        self.currency = currency
        self.sold_for = sold_for
        self.estimate_minimum = estimate_minimum
        self.estimate_maximum = estimate_maximum
        self.date_sold = date_sold
        self.material = material
        self.case_number = case_number
        self.description_condition = description_condition
        # Optional
        self.diameter = diameter
        self.movement_number = movement_number
        self.calibre = calibre
        self.bracelet_strap = bracelet_strap
        self.accessoires = accessoires
        self.signed = signed
        # Extra's
        self.auction_title = auction_title
        self.lot_number = lot_number
        self.url = url

    def __repr__(self):  
        return "manufacturer: %s \nyear: %s \nref_num: %s \nmodel_name: %s \ncurrency: %s \nsold_for: %s \nestimate_min: %s \nestimate_maximum: %s \ndate_sold: %s \nmaterial: %s \ncase_num: %s \ndescription_condition: %s \ndiameter: %s \nmovement_number: %s \ncalibre: %s \nbracelet_strap: %s \naccesoires: %s \nsigned: %s \nauction_title: %s \nlot_number: %s \nurl: %s " % (self.manufacturer, self.year, self.reference_number, self.model_name, self.currency, self.sold_for, self.estimate_minimum, self.estimate_maximum, self.date_sold, self.material, self.case_number, self.description_condition, self.diameter, self.movement_number, self.calibre, self.bracelet_strap, self.accessoires, self.signed, self.auction_title, self.lot_number, self.url)      

def main():
    watches_list = []
 
    for i, auction_url in enumerate(get_all_auctions_urls()): 
        # Only scraping the first 21 auctions due to webpage consitency 
        if i == 21:
            break

        for lot in get_all_lots(auction_url):
            watch = scrape_watchinfo(lot)
            watches_list.append(watch)
   
        create_excelsheet(watches_list, i)
    # lot = Lot(1, "https://catalog.antiquorum.swiss/en/lots/birks-challenger-lot-324-337?page=0")
    # watch = scrape_watchinfo(lot)
    # print(watch)
    

def get_all_lots(auction_url):
    print("getting all lots....")

    page = requests.get(auction_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    link_elements = soup.select("a[class=lotnumber]")
    
    lots = []
    for link in link_elements:
        lot = Lot(link.text, "https://catalog.antiquorum.swiss" + link['href'])
        lots.append(lot)

    print("[found %s wacthes]" %(str(len(lots))))   
    return lots    

def get_all_auctions_urls():
    print("getting all auctions url....")

    url = "https://catalog.antiquorum.swiss/"
    driver = webdriver.Chrome()
    driver.get(url)

    scroll_down_page(driver)

    link_elements = driver.find_elements_by_link_text("Price List")
    auction_urls = []

    for link in link_elements:
        auction_urls.append(link.get_attribute("href"))
    
    driver.close()
    
    print("[found %s auctions]" %(str(len(auction_urls))))
    print_auction_urls(auction_urls)
    return auction_urls

def print_auction_urls(auction_list):
    for auction_url in auction_list:
        print("'%s'," %(auction_url))

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def scrape_watchinfo(lot):
    print("scraping %s" %(lot.url))

    page = requests.get(lot.url)
    soup = BeautifulSoup(page.content, 'lxml')
    
    info_element = soup.find_all("div", class_="col-xs-12 col-md-6")[1]
    p_elements = info_element.find_all("p")

    watch = Watch()

    for p in p_elements:
        label = p.find("strong")

        if label is not None:
            label = label.get_text()

            # Switch???? Breaks??????? PERFORMANCE??????
            if label == "Brand": 
                watch.manufacturer = p.get_text().split("Brand", 1)[1].lstrip()
            
            if label == "Model":
                watch.model_name = p.get_text().split("Model", 1)[1].lstrip()

            if label == "Movement No.":
                watch.movement_number = p.get_text().split("Movement No.", 1)[1].lstrip()
            
            if label == "Material":
                watch.material = p.get_text().split("Material", 1)[1].lstrip()

            if label == "Reference":
                watch.reference_number = p.get_text().split("Reference", 1)[1].lstrip()

            if label == "Year":
                watch.year = p.get_text().split("Year", 1)[1].lstrip()

            if label == "Case No.":
                watch.case_number = p.get_text().split("Case No.", 1)[1].lstrip()

            if label == "Bracelet":
                watch.bracelet_strap =p.get_text().split("Bracelet", 1)[1].lstrip()

            if label == "Caliber":
                watch.calibre = p.get_text().split("Caliber", 1)[1].lstrip()

            if label == "Diameter":
                watch.diameter = p.get_text().split("Diameter", 1)[1].lstrip()

            if label == "Signature":
                watch.signed = p.get_text().split("Signature", 1)[1].lstrip()

            if label == "Accessories":
                watch.accessoires = p.get_text().split("Accessories", 1)[1].lstrip()

    try: 
        watch.currency = "".join(re.split("[^a-zA-Z]*", info_element.find_all("h4")[0].get_text()))
    except Exception as inst:
        print("NO CURRENCY")

    try:
        watch.sold_for = info_element.find_all("h4")[1].get_text()[6:].split()[1]
    except Exception as inst:
        print("NO SOLD_FOR")

    try:
        watch.estimate_minimum = info_element.find_all("h4")[0].get_text().split("-")[0].split()[1]
    except Exception as inst:
        print("NO ESTIMATE_MINIMUM")

    try: 
        watch.estimate_maximum = info_element.find_all("h4")[0].get_text().split("-")[1]
    except Exception as inst:
        print("NO ESTIMATE_MAXIMUM")

    try:    
        watch.date_sold = info_element.find_all("p")[2].get_text().split(',', 1)[1]
    except Exception as inst:
        print("NO DATE_SOLD")

    try:   
        watch.auction_title = info_element.find_all("p")[0].get_text()
    except Exception as inst:
        print("NO AUCTION_TITLE")

    watch.lot_number = lot.lot_number
    watch.url = lot.url
    try:
        watch.description_condition = soup.find("tbody").find("tr").find_all("td")[1].get_text()
    except Exception as inst:
        print("Couldn't find a grading, probaly no watch.")

    return watch

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def create_excelsheet(watches, auction_index):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("creating excel sheet for auction: %s...." %(auction_index))
    # Creating a excel heet   
    workbook = Workbook()
    sheet = workbook.active

    # Append column names first
    sheet.append(["auction_title", "lot_number", "manufacturer", "year", "reference_number", "model_name", "currency", "sold_for", "estimate_minimum", "estimate_maximum", "date_sold", "material", "case_number", "description_condition", "diameter", "movement_number", "calibre", "bracelet_strap", "accessoires", "signed", "url"])
    
    for wa in watches:
        sheet_data = [wa.auction_title, wa.lot_number, wa.manufacturer, wa.year, wa.reference_number, wa.model_name, wa.currency, wa.sold_for, wa.estimate_minimum, wa.estimate_maximum, wa.date_sold, wa.material, wa.case_number, wa.description_condition, wa.diameter, wa.movement_number, wa.calibre, wa.bracelet_strap, wa.accessoires, wa.signed, wa.url]
        
        try:
            sheet.append(sheet_data) 
        except Exception as inst:
            print("exception in excel watch appending...")

    workbook.save(filename="scape_results_%s.xlsx" %(auction_index))

def scroll_down_page(driver):
    print("scrolling down page...")

    SCROLL_PAUSE_TIME = 1.8

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        print("and scrolling...")
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def combine_sheets():
    cwd = os.path.abspath('') 
    files = os.listdir(cwd)  
    print(files)
    df = pd.DataFrame()
    for file in files:
        if file.endswith('.xlsx'):
            df = df.append(pd.read_excel(file), ignore_index=True) 
    df.head() 
    df.to_excel('antiquorum_watches.xlsx')

main()