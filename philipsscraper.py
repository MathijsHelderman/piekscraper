# LOGBOOK
# 21/04/2020, 21:30 - 23.00
# 21/04/2020, 00:45 - 01.30
# 22/04/2020, 20:30 - 22.30

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
# 7: Omdat we weten hoeveel lots er per auction zijn kunnen we alle lots van een auction af door de lot_id te verhogen met 1.

import requests
from bs4 import BeautifulSoup

class Auction:
    "Auction of the watch department"

    def __init__(self, url = "", number_of_lots = 0):
        self.url = url
        self.number_of_lots = number_of_lots

class Watch: 
    "A watch sold at the auction"

    def __init__(self, manufacturer, year, reference_number, model_name, sold_for, estimate, date_sold, material, case_number, description_condition, diameter = None, movement_number = None, calibre = None, bracelet_strap = None, accessoires = None, signed = None ):
        # Mandatory
        self.manufacturer = manufacturer
        self.year = year
        self.reference_number = reference_number
        self.model_name = model_name
        self.sold_for = sold_for
        self.estimate_minimum = estimate
        self.date_sold = date_sold
        self.material = material
        self.case_number = case_number
        # Optional
        self.diameter = diameter
        self.movement_number = movement_number
        self.calibre = calibre
        self.bracelet_strap = bracelet_strap
        self.accessoires = accessoires
        self.signed = signed
        
# Dit zijn alle eerste pagina's van een auction, met het totaal aantal lots(watches) in een auction
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
for i in range(1):

    url = auctions_list[0].url
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    info_elements = soup.find("ul", class_="info-list").find("li").find("p").find_all("span")
    # Dit werkt dus niet voor alle paginas, aangezien er soms velden niet zijn waardoor de index niet meer klopt
    # DUS
    # 1 Loop door alle "spans"
    # 2 Check welke "strong" hoort bij een watch attribuut
    # 3 Voeg de "text" toe aan watch attribuut

    manufacturer = info_elements[0].find("text").get_text()
    year = info_elements[1].find("text").get_text()
    reference_number = info_elements[2].find("text").get_text()
    movement_number = info_elements[3].find("text").get_text()
    case_number = info_elements[4].find("text").get_text()
    model_name = info_elements[5].find("text").get_text()
    material = info_elements[6].find("text").get_text()
    calibre = info_elements[7].find("text").get_text()
    bracelet_strap = info_elements[8].find("text").get_text()
    diameter = info_elements[10].find("text").get_text() #TODO: format without "Diameter"
    signed = info_elements[11].find("text").get_text()
    accessoires = info_elements[12].find("text").get_text()

    sold_for = soup.find("p", class_="lot-detail-header__sold").get_text() #TODO: format without "SOLD FOR"
    estimate = soup.find("p", class_="lot-detail-header__estimate").find("br").get_text()
    date_sold = soup.find("div", class_="sale-title-banner").find("a").find("span").get_text()

    description_condition = soup.find("p", class_="lot-detail-header__title").find("em").get_text()

    watch = Watch(manufacturer, year, reference_number, model_name, sold_for, estimate, date_sold, material, case_number, description_condition, diameter, movement_number, calibre, bracelet_strap, accessoires, signed)
    watches_list.append(watch)

    attributes_of_watch = vars(watch)
    print(', '.join("%s: %s" % item for item in attributes_of_watch.items()))
    
#TODO: Go to next watch -> End of auction ? -> go to next auction -> ...
#TODO: Create xlsx file
#TODO: Create columns from watch attribute names
#TODO: Append each watch as a record 
#fin

