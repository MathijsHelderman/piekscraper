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

from antiquorum_auctions import auctions as _AUCTIONS_ANTI


class Lot:
    "A lot of a auction"

    def __init__(self, lot_number=None, url=None):
        self.lot_number = lot_number
        self.url = url

    def __repr__(self):
        return "\nlot_number: %s \nurl: %s" % (self.lot_number, self.url)


@dataclass
class Watch:
    "A watch sold at the auction"

    def __init__(self, manufacturer=None, year=None, reference_number=None, model_name=None, currency=None, sold_for=None, estimate_minimum=None, estimate_maximum=None, date_sold=None, material=None, case_number=None, description_condition=None, diameter=None, movement_number=None, calibre=None, bracelet_strap=None, accessoires=None, signed=None, auction_title=None, lot_number=None, url=None):
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
        return "manufacturer: %s \nyear: %s \nref_num: %s \nmodel_name: %s \ncurrency: %s \nsold_for: %s \nestimate_min: %s \nestimate_maximum: %s \ndate_sold: %s \nmaterial: %s \ncase_num: %s \ndescription_condition: %s \ndiameter: %s \nmovement_number: %s \ncalibre: %s \nbracelet_strap: %s \naccesoires: %s \nsigned: %s \nauction_title: %s \nlot_number: %s \nurl: %s \n\n" % (self.manufacturer, self.year, self.reference_number, self.model_name, self.currency, self.sold_for, self.estimate_minimum, self.estimate_maximum, self.date_sold, self.material, self.case_number, self.description_condition, self.diameter, self.movement_number, self.calibre, self.bracelet_strap, self.accessoires, self.signed, self.auction_title, self.lot_number, self.url)


def main():
    # watches_list = []

    # for i, auction_url in enumerate(_AUCTIONS_ANTI):
    #     # Only scraping the first 21 auctions due to webpage consitency
    #     if i < 19:
    #         continue
    #     elif i >= 23:
    #         break

    #     max_numb = 0
    #     for lot in get_all_lots(auction_url):
    #         if max_numb >= 3:
    #             break
    #         watch = scrape_watchinfo(lot)
    #         print(watch)
    #         watches_list.append(watch)
    #         max_numb += 1

    #     create_excelsheet(watches_list, i)
    # lot = Lot(1, "https://catalog.antiquorum.swiss/en/lots/patek-philippe-ref-ref-5060-lot-109-204?page=0")
    # lot = Lot(1, "https://catalog.antiquorum.swiss/en/lots/panerai-lot-303-3?page=0")
    lot = Lot(
        1, "https://catalog.antiquorum.swiss/en/lots/omega-ref-st-105-003-lot-302-296?page=0")

    watch = scrape_watchinfo(lot)
    print(watch)


def get_all_lots(auction_url):
    print("getting all lots....")

    page = requests.get(auction_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    link_elements = soup.select("a[class=lotnumber]")

    lots = []
    for link in link_elements:
        lot = Lot(link.text, "https://catalog.antiquorum.swiss" + link['href'])
        lots.append(lot)

    print("[found %s wacthes]" % (str(len(lots))))
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

    print("[found %s auctions]" % (str(len(auction_urls))))
    print_auction_urls(auction_urls)
    return auction_urls


def print_auction_urls(auction_list):
    for auction_url in auction_list:
        print("'%s'," % (auction_url))


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


# Helper methods

def remove_chars(string, loc):
    i = 0
    if loc == 'start':
        for char in string:
            if char.isdigit():
                string = string[i:]
                break
            i += 1
    elif loc == 'end':
        for char in reversed(string):
            if char.isdigit():
                index = len(string) - i
                string = string[:index]
                break
            i += 1
    elif loc == 'both':
        string = remove_chars(string, 'start')
        string = remove_chars(string, 'end')
    return string


def get_first_valid_year(string):
    number_array = []
    s_array = string.split(' ')
    for s in s_array:
        s = remove_chars(s, 'both')
        if (len(s) == 4 and s.isdigit()) and (int(s) > 1000 and int(s) <= 2020):
            number_array.append(s)

    # print('numbarr:', number_array)
    # return the first possible year
    return number_array[0] if len(number_array) > 0 else ''


def get_desc(info_element):
    try:
        desc = info_element.find_all("strong")[0].find("p").get_text()
        # print("Desc: %s " % desc)
        return desc
    except Exception:
        return ''


def get_desc2(info_element):
    try:
        desc2 = info_element.find_all(
            "strong")[0].find_next_sibling("p").get_text()
        return desc2
    except Exception:
        return ''


def get_desc_index_of_attr(desc, attr):
    i = 0
    for part in desc:
        if isinstance(part, str):
            if part.lower().find(attr.lower()) >= 0:
                return i
        elif part.get_text().lower().find(attr.lower()) >= 0:
            return i
        i += 1
    return -1


def get_desc_attr(desc, attr):
    a = ''

    desc_arr_commas = desc.split(',')
    index = get_desc_index_of_attr(desc_arr_commas, attr)
    if index != -1:
        if attr == 'Signed':
            # When the information is ordered by commas, the 'case'
            # in the "case, dial and movement signed"
            # text is seperated. So search for it at the index - 1
            # to see if the case was signed as well.
            if desc_arr_commas[(index - 1)].lower().find('case') >= 0:
                a = desc_arr_commas[(
                    index - 1)] + ',' + desc_arr_commas[index]
        else:
            a = desc_arr_commas[index]

    a = a.replace('\xa0', ' ')
    a = a.lstrip()
    # print("\n%s: %s" % (attr, a), end='\n')
    return a

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# Getters for watch specs


def get_manufacturer(desc):
    try:
        mf_array = desc.split(',')
        mf = mf_array[0]
        mf = mf.replace('\xa0', ' ')
        mf = mf.lstrip()
        # print('mf:', mf)
        return mf
    except Exception:
        return ''


def get_model_name(desc):
    try:
        mn_array = desc.split(',')
        mn = mn_array[0]
        mn = mn.replace('\xa0', ' ')
        mn = mn.lstrip()
        # print('Model name: ', mn)
        return mn
    except Exception:
        return ''


def get_movement_number(desc):
    try:
        desc = desc.lower()
        mvt = ''
        mvt_index = -1

        mvt = get_desc_attr(desc, 'mvt.')
        if mvt != '':
            mvt_index = mvt.find('mvt.')
        else:
            mvt = get_desc_attr(desc, 'movement number')
            if mvt != '':
                mvt_index = mvt.find('movement number')
            else:
                mvt = get_desc_attr(desc, 'mvt')
                if mvt != '':
                    mvt_index = mvt.find('mvt')

        if mvt_index != -1:
            mvt = mvt[mvt_index:]  # remove everything in front
            mvt = mvt.split()
            mvt = mvt[1]

        return mvt
    except Exception:
        return ''


def get_material(desc):
    try:
        return get_desc_attr(desc, 'case')
    except Exception:
        return ''


def get_reference_number(desc):
    try:
        desc = desc.lower()
        desc = desc.split()
        ref_index = -1

        # TODO : should check every word
        # in whole desc first, before checking every
        # word against every word in the array.
        # Now a word with lower preferability can be
        # found first.
        for t in desc:
            if t.find('reference') >= 0:
                ref_index = desc.index(t)
                break
            elif t.find('ref.') >= 0:
                ref_index = desc.index(t)
                break
            elif t.find('ref') >= 0:
                ref_index = desc.index(t)
                break
            elif t.find('NO.') >= 0:
                ref_index = desc.index(t)
                break
            elif t.find('NO ') >= 0:
                ref_index = desc.index(t)
                break

        if ref_index == -1:
            return ''
        else:
            ref = desc[(ref_index + 1)]
            # print('ref:', ref)
            return ref
    except Exception:
        return ''


def get_year(desc):
    try:
        desc = desc.lower()

        year_index = desc.find('circa')
        if year_index == -1:
            year_index = desc.find('made in')
        if year_index == -1:
            year_index = desc.find('made ')
        if year_index == -1:
            year_index = desc.find('year ')

        # y = desc[year_index:]

        year = get_first_valid_year(desc)
        year = year.replace('\xa0', ' ')
        return year
    except Exception as e:
        print(e)
        return ''

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! up mh - down


def get_diameter(notes, desc, desc2):
    try:
        diameter = ''
        if notes != '':
            notes = notes.lower()
            d_index = notes.find('diam')
            if d_index == -1:
                d_index = notes.find('dim.')
            if d_index == -1:
                d_index = notes.find('dim')
            if d_index >= 0:
                mm_index = notes[d_index:].find('mm')
                diameter = notes[d_index:(d_index + mm_index + 2)]
                diameter = remove_chars(diameter, 'start')
        if diameter == '' and desc2 != '':
            diameter = get_diameter_detail(desc2)
        if diameter == '' and desc != '':
            diameter = get_diameter_detail(desc)

        # print('Diameter/dimensions: "%s"' % diameter)
        return diameter
    except Exception:
        return ''


def get_diameter_detail(desc: str):
    diameter = ''
    d_index = -1

    d = get_desc_attr(desc, 'diam')
    if d != '':
        d_index = d.lower().find('diam')
    else:
        d = get_desc_attr(desc, 'dim.')
        if d != '':
            d_index = d.lower().find('dim.')
        else:
            d = get_desc_attr(desc, 'dim')
            if d != '':
                d_index = d.lower().find('dim')

    if d_index >= 0:
        d = d.lower()
        mm_index = d[d_index:].find('mm')
        diameter = d[d_index:(d_index + mm_index + 2)]
        diameter = remove_chars(diameter, 'start')

    return diameter


def get_case_number(desc, desc2):
    try:
        case_number = ''
        if desc2 ==  '': 
            case_number = get_desc_attr(desc, 'case')
        else:
            case_number = get_desc_attr(desc, 'case')
            if case_number == '':
                case_number = get_desc_attr(desc2, 'case')
        return case_number
    except Exception:
        return ''


def get_calibre(desc, desc2):
    try:
        calibre = ""
        search_word_index = desc.lower().find("cal.")
        if search_word_index == -1: # Did not found search word
            sw_index_desc2 = desc2.lower().find("cal.")
            if sw_index_desc2 > 0:
                calibre = desc2[sw_index_desc2:].split(',')[0]
        else: 
            calibre = desc2[sw_index_desc2:].split(',')[0]
        return calibre
    except Exception:
        return ''


def get_bracelet_strap(desc):
    try:
        return get_desc_attr(desc, 'bracelet').split('.')[0]
    except Exception:
        return ''


def get_accessoires(desc, desc2):
    try:
        accesoires = ""
        search_word_index = desc.lower().find("accompanied")
        if search_word_index == -1: # Did not found search word
            sw_index_desc2 = desc2.lower().find("accompanied")
            if sw_index_desc2 > 0: # Did found search word in desc2
                accesoires = desc[search_word_index:].split(".")[0]
        else:
            accesoires = desc[search_word_index:].split(".")[0]
        return accesoires
    except Exception:
        return ''


def get_signed(notes, desc, desc2):
    try:
        search_word = 'signed'
        signed = ""
        search_word_index_notes = notes.lower().find(search_word)
        if search_word_index_notes == -1: # Did not found search word in notes
            sw_index_desc = desc.lower().find(search_word)
            if sw_index_desc > 0: # Did found search word in desc
                desc = desc.split(".")
                # https://stackoverflow.com/questions/13779526/finding-a-substring-within-a-list-in-python
                signed = next((s for s in desc if search_word in s), None).lstrip() 
            else: 
                sw_index_desc2 = desc.lower().find(search_word)
                if sw_index_desc2 > 0: # Did found search word in desc2
                    desc2 = desc2.split(".")
                    signed = next((s for s in desc if search_word in s), None).lstrip() 
        else:
            signed = notes[:search_word_index_notes].split(".")[0]
        return signed
    except Exception:
        return ''


# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# scraping the watch
def scrape_watchinfo(lot):
    print("\nscraping %s" % (lot.url))

    page = requests.get(lot.url)
    soup = BeautifulSoup(page.content, 'lxml')

    info_element = soup.find_all("div", class_="col-xs-12 col-md-6")[1]
    p_elements = info_element.find_all("p")

    watch = Watch()

    if len(p_elements) < 0:
        for p in p_elements:
            label = p.find("strong")

            if label != None:
                label = label.get_text()

                # Switch???? Breaks??????? PERFORMANCE??????
                if label == "Brand":
                    watch.manufacturer = p.get_text().split("Brand", 1)[
                        1].lstrip()

                if label == "Model":
                    watch.model_name = p.get_text().split("Model", 1)[
                        1].lstrip()

                if label == "Movement No.":
                    watch.movement_number = p.get_text().split(
                        "Movement No.", 1)[1].lstrip()

                if label == "Material":
                    watch.material = p.get_text().split(
                        "Material", 1)[1].lstrip()

                if label == "Reference":
                    watch.reference_number = p.get_text().split(
                        "Reference", 1)[1].lstrip()

                if label == "Year":
                    watch.year = p.get_text().split("Year", 1)[1].lstrip()

                if label == "Case No.":
                    watch.case_number = p.get_text().split(
                        "Case No.", 1)[1].lstrip()

                if label == "Bracelet":
                    watch.bracelet_strap = p.get_text().split(
                        "Bracelet", 1)[1].lstrip()

                if label == "Caliber":
                    watch.calibre = p.get_text().split(
                        "Caliber", 1)[1].lstrip()

                if label == "Diameter":
                    watch.diameter = p.get_text().split(
                        "Diameter", 1)[1].lstrip()

                if label == "Signature":
                    watch.signed = p.get_text().split(
                        "Signature", 1)[1].lstrip()

                if label == "Accessories":
                    watch.accessoires = p.get_text().split(
                        "Accessories", 1)[1].lstrip()
    else:
        desc = get_desc(info_element)  # DONE
        desc2 = get_desc2(info_element)
        notes_element = get_notes(soup)
        # print("NOTES: %s" % (notes_element))

        # TODO
        watch.manufacturer = get_manufacturer(desc)  # DONE
        watch.model_name = get_model_name(desc)  # DONE
        watch.movement_number = get_movement_number(desc)
        watch.material = get_material(desc)
        watch.reference_number = get_reference_number(desc)
        watch.year = get_year(desc)
        # TODO
        watch.case_number = get_case_number(desc, desc2) # DOING
        watch.bracelet_strap = get_bracelet_strap(desc)
        watch.calibre = get_calibre(desc, desc2) # DONE
        watch.diameter = get_diameter(notes_element, desc, desc2) # DONE
        watch.signed = get_signed(notes_element, desc, desc2) # DONE
        watch.accessoires = get_accessoires(desc, desc2) # DONE

    try:
        watch.currency = "".join(
            re.split("[^a-zA-Z]*", info_element.find_all("h4")[0].get_text()))
    except Exception as inst:
        print("NO CURRENCY")

    try:
        watch.sold_for = info_element.find_all(
            "h4")[1].get_text()[6:].split()[1]
    except Exception as inst:
        print("NO SOLD_FOR")

    try:
        watch.estimate_minimum = info_element.find_all(
            "h4")[0].get_text().split("-")[0].split()[1]
    except Exception as inst:
        print("NO ESTIMATE_MINIMUM")

    try:
        watch.estimate_maximum = info_element.find_all(
            "h4")[0].get_text().split("-")[1]
    except Exception as inst:
        print("NO ESTIMATE_MAXIMUM")

    try:
        watch.date_sold = info_element.find_all(
            "p")[2].get_text().split(',', 1)[1]
    except Exception as inst:
        print("NO DATE_SOLD")

    try:
        watch.auction_title = info_element.find_all("p")[0].get_text()

    except Exception as inst:
        print("NO AUCTION_TITLE")

    watch.lot_number = lot.lot_number
    watch.url = lot.url
    try:
        watch.description_condition = soup.find(
            "tbody").find("tr").find_all("td")[1].get_text()
    except Exception as inst:
        print("Couldn't find a grading, probaly no watch.")

    return watch

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


def get_notes(soup):
    try:
        notes_element = soup.find_all("div", {"class": "container"})[2].find_all(
            "div", {"class": "row"})[0].find_all("h4")[2].findNext("div").get_text()
        return notes_element
    except Exception:
        return ""


def create_excelsheet(watches, auction_index):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("creating excel sheet for auction: %s...." % (auction_index))
    # Creating a excel heet
    workbook = Workbook()
    sheet = workbook.active

    # Append column names first
    sheet.append(["auction_title", "lot_number", "manufacturer", "year", "reference_number", "model_name", "currency", "sold_for", "estimate_minimum", "estimate_maximum",
                  "date_sold", "material", "case_number", "description_condition", "diameter", "movement_number", "calibre", "bracelet_strap", "accessoires", "signed", "url"])

    for wa in watches:
        sheet_data = [wa.auction_title, wa.lot_number, wa.manufacturer, wa.year, wa.reference_number, wa.model_name, wa.currency, wa.sold_for, wa.estimate_minimum, wa.estimate_maximum,
                      wa.date_sold, wa.material, wa.case_number, wa.description_condition, wa.diameter, wa.movement_number, wa.calibre, wa.bracelet_strap, wa.accessoires, wa.signed, wa.url]

        try:
            sheet.append(sheet_data)
        except Exception as inst:
            print("exception in excel watch appending...")

    workbook.save(filename="scape_resultz_%s.xlsx" % (auction_index))


def scroll_down_page(driver):
    print("scrolling down page...")

    SCROLL_PAUSE_TIME = 1.8

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        print("and scrolling...")
        # Scroll down to bottom
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

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
