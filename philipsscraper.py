# LOGBOOK
# 21/04/2020, 21:30 - 23.00
# 21/04/2020, 00:45 - 01.30
# 22/04/2020, 20:30 - 22.30
# 24/04/2020, 23:30 - 00.00
# 25/04/2020, 20:30 - 23:00
# 03/04/2020, 21:00 - 01:00

# AUCTION ID's (30)
# https://www.phillips.com/auctions/auction/NY080119
# https://www.phillips.com/auctions/auction/HK080319
# https://www.phillips.com/auctions/auction/CH080219
# https://www.phillips.com/auctions/auction/HK080119
# https://www.phillips.com/auctions/auction/HK080219
# https://www.phillips.com/auctions/auction/CH080119
# https://www.phillips.com/auctions/auction/NY080118
# https://www.phillips.com/auctions/auction/HK080218
# https://www.phillips.com/auctions/auction/CH080218
# https://www.phillips.com/auctions/auction/HK080118
# https://www.phillips.com/auctions/auction/CH080118
# https://www.phillips.com/auctions/auction/CH080318
# https://www.phillips.com/auctions/auction/HK080217
# https://www.phillips.com/auctions/auction/CH080217
# https://www.phillips.com/auctions/auction/CH080317
# https://www.phillips.com/auctions/auction/NY080117
# https://www.phillips.com/auctions/auction/HK080117 !!!!!Filter data, false entry
# https://www.phillips.com/auctions/auction/CH080117
# https://www.phillips.com/auctions/auction/HK080216
# https://www.phillips.com/auctions/auction/HK080316
# https://www.phillips.com/auctions/auction/CH080216
# https://www.phillips.com/auctions/auction/HK080116
# https://www.phillips.com/auctions/auction/CH080116
# https://www.phillips.com/auctions/auction/CH080016
# https://www.phillips.com/auctions/auction/HK080115
# https://www.phillips.com/auctions/auction/CH080515
# https://www.phillips.com/auctions/auction/CH080415
# https://www.phillips.com/auctions/auction/CH080215
# https://www.phillips.com/auctions/auction/CH080115

# LINKS
# 1: https://www.phillips.com/auctions/past/filter/Department%3DWatches
# 2: https://www.phillips.com/auctions/auction/NY080119
# 3: https://www.phillips.com/detail/patek-philippe/NY080119/1

# ANALYZING THE PAGE
# 1: Op link 1 is te zien dat er auctions van 2015 tot 2019 zijn.
# 2: Er staan 32 auctions weergeven in de watches department
# 3: Op link 2 valt te zien dat het aantal lots staat weergeven, dit aantal hebben wij nodig in het script. 
# 4: Als we dan de eerste lot pakken, zien we de volgende link 3.
# 5: Deze link delen we op in stukjes: {base-url}/detail/patek-philippe/{auction_id}/{lot_id}
# 6: Als we dan de lot_id verhogen met 1, komt de volgende lot(horloge) in beeld.
# 7: Omdat we weten hoeveel lots er per auction zijn kunnen we gemakellijk alle lots van een auction af door de lot_id te verhogen met 1.

import requests
import re
from openpyxl import Workbook
from bs4 import BeautifulSoup
from dataclasses import dataclass


class Auction:
    "Auction of the watch department"

    def __init__(self, url = "", number_of_lots = 0):
        self.url = url
        self.number_of_lots = number_of_lots

@dataclass
class Watch: 
    "A watch sold at the auction"

    def __init__(self, manufacturer = None, year = None, reference_number = None, model_name = None, sold_for = None, estimate_minimum = None, estimate_maximum = None, date_sold = None, material = None, case_number = None, description_condition = None, diameter = None, movement_number = None, calibre = None, bracelet_strap = None, accessoires = None, signed = None ):
        # Mandatory
        self.manufacturer = manufacturer
        self.year = year
        self.reference_number = reference_number
        self.model_name = model_name
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

    def __repr__(self):  
        return "manufacturer: %s \nyear: %s \nref_num: %s \nmodel_name: %s \nsold_for: %s \nestimate_min: %s \nestimate_maximum: %s \ndate_sold: %s \nmaterial: %s \ncase_num: %s \ndescription_condition: %s \ndiameter: %s \nmovement_number: %s \ncalibre: %s \nbracelet_strap: %s \naccesoires: %s \nsigned: %s" % (self.manufacturer, self.year, self.reference_number, self.model_name, self.sold_for, self.estimate_minimum, self.estimate_maximum, self.date_sold, self.material, self.case_number, self.description_condition, self.diameter, self.movement_number, self.calibre, self.bracelet_strap, self.accessoires, self.signed)      
    
auctions_list = []
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/NY080119/1" ,75))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/HK080319/801" ,321)) 
auctions_list.append(Auction("https://www.phillips.com/detail/roger-dubuis/CH080219/100" ,186))
auctions_list.append(Auction("https://www.phillips.com/detail/patek-philippe/NY080119/1" ,75))
auctions_list.append(Auction("https://www.phillips.com/detail/tudor/CH080319/1" ,64))
auctions_list.append(Auction("https://www.phillips.com/detail/patek-philippe/HK080119/901" ,297))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/HK080219/801 ",82))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080119/1" ,220))
auctions_list.append(Auction("https://www.phillips.com/detail/fp-journe/NY080118/1" ,120 ))
auctions_list.append(Auction("https://www.phillips.com/detail/blancpain/HK080218/801" ,259))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080218/1" ,226))
auctions_list.append(Auction("https://www.phillips.com/detail/omega/HK080118/801" ,231))
auctions_list.append(Auction("https://www.phillips.com/detail/heuer/CH080118/101" ,185))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080318/1" ,32))
auctions_list.append(Auction("https://www.phillips.com/detail/jaegerlecoultre/HK080217/801" ,168)) 
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080217/101" ,157))
auctions_list.append(Auction("https://www.phillips.com/detail/heuer/CH080317/1" ,43))
auctions_list.append(Auction("https://www.phillips.com/detail/heuer/NY080117/1" ,50))
auctions_list.append(Auction("https://www.phillips.com/detail/de-beers/HK080117/801 ",356))
auctions_list.append(Auction("https://www.phillips.com/detail/omega/CH080117/1" ,237))
auctions_list.append(Auction("https://www.phillips.com/detail/de-beers/HK080216/850" ,300))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/HK080316/801" ,41))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080216/1" ,196))
auctions_list.append(Auction("https://www.phillips.com/detail/de-beers/HK080116/1" ,390))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080116/101" ,138))
auctions_list.append(Auction("https://www.phillips.com/detail/jaegerlecoultre/CH080016/1" ,88))
auctions_list.append(Auction("https://www.phillips.com/detail/de-beers/HK080115/1 ",357))
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080515/101" ,203))
auctions_list.append(Auction("https://www.phillips.com/detail/iwc/CH080415/1" ,44))
auctions_list.append(Auction("https://www.phillips.com/detail/vacheron-constantin/CH080215/61 ",164)) 
auctions_list.append(Auction("https://www.phillips.com/detail/rolex/CH080115/1" ,60))

watches_list = [] 

# for each auction in auction_list
for auction_id in range(len(auctions_list)):
    print("auction_id: %s" %(auction_id))
    # for each lot in auction
    for lot_index in range(auctions_list[auction_id].number_of_lots):
        # GET_PAGE()
        # van 1 tot number_of_lots
        res = auctions_list[auction_id].url.rsplit("/", 1) #https://www.phillips.com/detail/blancpain/HK080218/801 => #https://www.phillips.com/detail/blancpain/HK080218
        lot_id = int(res[1]) + lot_index #lot_id = 801 + 1
        url = res[0] + "/" + str(lot_id) #https://www.phillips.com/detail/blancpain/HK080218/802
        print(url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')

           
        try:
            info_elements = soup.find("ul", class_="info-list").find("li").find("p").find_all("span")
        except Exception as inst:
            print("WARNING: No lot on lot_id: " + str(lot_id) + " and " + "auction_id: " + str(auction_id))
            break
        
        # 1 Loop door alle "spans"
        watch = Watch()

        # get_watch
        for k in range(len(info_elements)):
            # 2 Check welke "strong" hoort bij een watch attribuut
            attribute = info_elements[k].find("strong").get_text()[:-1]

            if attribute == "Manufacturer":
                # 3 Voeg de "text" toe aan watch attribuut
                manufacturer = info_elements[k].find("text").get_text()
                watch.manufacturer = manufacturer
                
            if attribute == "Year":
                year = info_elements[k].find("text").get_text()
                watch.year = year
                
            if attribute == "Reference No":
                reference_number = info_elements[k].find("text").get_text()
                watch.reference_number = reference_number
                
            if attribute == "Movement No":
                movement_number = info_elements[k].find("text").get_text()
                watch.movement_number = movement_number
                        
            if attribute == "Case No": 
                case_number = info_elements[k].find("text").get_text()
                watch.case_number = case_number
                
            if attribute == "Model Name":
                model_name = info_elements[k].find("text").get_text()
                watch.model_name = model_name
                
            if attribute == "Material":
                material = info_elements[k].find("text").get_text()
                watch.material = material
                
            if attribute == "Calibre":      
                calibre = info_elements[k].find("text").get_text()
                watch.calibre = calibre
                
            if attribute == "Bracelet/Strap":
                bracelet_strap = info_elements[k].find("text").get_text()
                watch.bracelet_strap = bracelet_strap
                
            if attribute == "Dimensions":
                diameter = info_elements[k].find("text").get_text()
                if diameter.endswith('Diameter'):
                    diameter = diameter[:-8]
                else:
                    print("WARNING: Irregular diameter on lot_id: " + str(lot_id) + " and " + "auction_id: " + str(auction_id))
                    watch.diameter = diameter    
            # if attribute == "Clasp/Buckle":
            #     clasp_buckle = info_elements[i].find("text").get_text()
            #     
            if attribute == "Signed":
                signed = info_elements[k].find("text").get_text()
                watch.signed = signed
                
            if attribute == "Accessories":
                accessoires = info_elements[k].find("text").get_text()
                watch.accessoires = accessoires
        try:
            sold_for = soup.find("p", class_="lot-detail-header__sold").get_text()
        except Exception as inst:
            print("WARNING: No lot on lot_id: " + str(lot_id) + " and " + "auction_id: " + str(auction_id))

        if sold_for.startswith('sold for'):
            watch.sold_for = sold_for[-8:] # i: "SOLD FOR $23,000" => o: "$23,000"
        else:
            print("WARNING: Irregular sold_For on lot_id: " + str(lot_id) + " and " + "auction_id: " + str(auction_id))
            watch.sold_for = sold_for
            
        #TODO: should be fixed    
        estimate_element = soup.find("p", class_="lot-detail-header__estimate")
        if estimate_element is not None:
            watch.estimate_minimum = "$" + estimate_element.contents[4]
            watch.estimate_maximum = "$" + estimate_element.contents[8]
        else: 
            watch.estimate_minimum = "Estimate on Request" 
            watch.estimate_maximum = "Estimate on Request" 

        date_sold = soup.find("div", class_="sale-title-banner").find("a").find("span").get_text() # "NEW YORK AUCTION 10 DECEMBER 2019"
        regExp_result = re.search(r"\d", date_sold) # Search for all the digit occurences in this string 
        if regExp_result is not None:
            digit_position = regExp_result.start() # Get the index of the first digit occurence 
            watch.date_sold = date_sold[digit_position:999] # Do some string magic that removes part of string that isnt in given range. 
        else:
            print("WARNING: Irregular date_sold on lot_id: " + str(lot_id) + " and " + "auction_id: " + str(auction_id))
            watch.date_sold = date_sold

        description_condition = soup.find("p", class_="lot-detail-header__title").find("em").get_text()
        watch.description_condition = description_condition
        watches_list.append(watch)
        print("Successfully scraped watch on lot_id: " + str(lot_id) + " and " + "auction_id: " + str(auction_id))

    # Creating a excel heet   
    workbook = Workbook()
    sheet = workbook.active

    # Append column names first
    sheet.append(["manufacturer", "year", "reference_number", "model_name", "sold_for", "estimate_minimum", "estimate_maximum", "date_sold", "material", "case_number", "description_condition", "diameter", "movement_number", "calibre", "bracelet_strap", "accessoires", "signed"])

    for wa in watches_list:
        sheet_data = [wa.manufacturer, wa.year, wa.reference_number, wa.model_name, wa.sold_for, wa.estimate_minimum, wa.estimate_maximum, wa.date_sold, wa.material, wa.case_number, wa.description_condition, wa.diameter, wa.movement_number, wa.calibre, wa.bracelet_strap, accessoires, wa.signed]
        sheet.append(sheet_data)   
    
    workbook.save(filename="hello_world.xlsx")
