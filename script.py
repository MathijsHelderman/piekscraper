import time
import requests
import json
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from auctions import Auction
from auctions import auctions as _AUCTIONS

# Piekscraper project
# @created_by: Mathijs Helderman & Juan Albergen
#
# Sotheby's
# @author: Mathijs Helderman
#
# Site analyzation
# Auctions, url: https://www.sothebys.com/en/results?from=&to=&f2=00000164-609a-d1db-a5e6-e9fffc050000&q=
# List of lots of a specific auction, like url: https://www.sothebys.com/en/buy/auction/2020/watches-weekly-a-lange-soehne-and-swiss?locale=en
# Specific lot from an auction, like url: https://www.sothebys.com/en/buy/auction/2020/watches-weekly-a-lange-soehne-and-swiss/a-lange-soehne-grand-lange-1-moon-phase-lumen
#
# Conclusion:
#   There are 230 auctions as of 23-04-2020.
#   Unfortunately the next lot url will have to be scraped as well because,
#   the url is not iterable.

#
# CONSTANTS
#
_DOMAIN_URL = 'https://www.sothebys.com'
_MAX_NUMBER_OF_REQUESTS_PER_ACUCTION = 1

#
# URL's of specific watches (for testing)
#
_TEST_URL_FIRST = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/f-p-journe-centigraphe-souverain-ref-cts-aluminium'
_TEST_URL2 = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/patek-philippe-nautilus-ref-5711-stainless-steel'
_TEST_URL_LAST = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/de-beers-gold-plated-hourglass-with-floating'
_TEST_URL_COLLECTOR = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/rolex-double-red-sea-dweller-ref-1665-stainless'
_TEST_URL3 = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/rolex-panama-canal-submariner-ref-16613-limited'
_TEST_URL4 = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/a-lange-soehne-lange-1-mondphase-ref-109-032-pink'
_TEST_URL5 = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/longines-double-hand-ref-5699-stainless-steel'
_TEST_URL6 = 'https://www.sothebys.com/en/buy/auction/2020/watches-online-2/longines-yellow-gold-wristwatch-circa-1940'


class Watch:
    "A watch sold at the auction"

    def __init__(self, manufacturer, year, reference_number, model_name, sold_for, estimate_minimum, estimate_maximum, date_sold, material, case_number, description_condition, diameter=None, movement_number=None, calibre=None, bracelet_strap=None, accessoires=None, signed=None):
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

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4)


def get_watch_info(url, date):
    """
    Getting watch info on sold watches in auctions from sothebys.com
    """
    # This website blocks the requests not coming from any browser,
    # therefore we use a user agent header.
    ua = {"User-Agent": "Mozilla/5.0"}

    # In case of a faulty url or another error with the Request lib
    # we encase the code in a try/except block.
    try:
        response = requests.get(url, headers=ua)

        # Check succesful request
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check if there was an error with the url, for example,
            # in case of an unknown url for a watch.
            if check_error_url(soup):
                exit()

            try:
                # The description block on the page of a watch
                desc = get_desc(soup)

                # The navigation container which holds the prizes and next url
                nav_con = get_nav_con(soup)
            except Exception as err:
                print(err)
                return -1, ''

            # lot_number = get_lot_number(nav_con)
            # print("Lot:", lot_number)
            # print("Lot:", lot_number, "url:", url)

            if date == '':
                date = get_date_sold(soup)

            watch = Watch(
                # Important
                get_manufacturer(desc),
                get_year(desc),
                get_reference_number(desc),
                get_model_name(desc),
                get_sold_for(nav_con),
                get_estimate_minimum(nav_con),
                get_estimate_maximum(nav_con),
                date,
                get_material(desc),
                get_case_number(desc),
                get_description_condition(soup),
                # Optional
                get_diameter(desc),
                get_movement_number(desc),
                get_calibre(desc),
                get_bracelet_strap(desc),
                get_accessoires(desc),
                get_signed(desc)
            )

            # print(watch.toJSON())

            return watch, get_next_url(nav_con)
        else:
            print("Error! Something went wrong. Response code:",
                  response.status_code)
            exit()
    except requests.exceptions.RequestException as err:
        print("Err:", err)
        exit()


def check_error_url(soup):
    """
    On the Sotheby's website, if there is an unforseen error,
    like an unknown url, there is a h1 element with the text: 'Error'
    """
    try:
        h1s = soup.find_all('h1')
        for h1 in h1s:
            h1 = h1.get_text()
            if h1 == 'Error':
                print('Error! Unknown url.')
                return True
        return False
    except Exception as err:
        print("Err:", err)
        return False


def get_lot_number(nav_con):
    lot = nav_con.find(
        'span', attrs={'class': 'css-yxsueo'}).get_text()
    return lot


def get_desc(soup):
    # First find the div in which the description is written
    desc = soup.find_all(
        'div', attrs={'class': 'css-xs9w33'})[0]

    # Start a clean list
    clean_desc = []

    # Now find all p tags in which no <br/> tag is written
    # for p_without_br in (p for p in desc.find_all('p')
    #                      if (not p.find('br')) and (p.get_text().find('PROPERTY') < 0)):
    for p_without_br in (p for p in desc.find_all('p') if not p.find('br')):
        clean_desc.append(p_without_br)

    # In the following url, there is an extra p tag as the first p tag in the description:
    # https://www.sothebys.com/en/buy/auction/2020/watches-online-2/rolex-double-red-sea-dweller-ref-1665-stainless
    # it says that this watch is the property of an, in this case, European collector.
    # To prevent this line from messing up the order of the description it needs to be removed.
    if clean_desc[0].get_text().find('PROPERTY') >= 0:
        clean_desc.remove(clean_desc[0])

    # print(clean_desc)
    # print(len(clean_desc))
    return clean_desc


def get_nav_con(soup):
    # First find the div in which the navigation container
    nav_con = soup.find(
        'div', attrs={'class': 'css-10pbwcw'})

    # print(nav_con)
    # print(len(nav_con))
    return nav_con


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
    return string


def get_manufacturer(desc):
    try:
        mf = desc[0].get_text()
        # print("Mf:", mf)
        return mf
    except Exception:
        return ''


def get_year(desc):
    try:
        year = desc[3].get_text()

        # If a watch does not have the case at place desc[2]
        if desc[3].get_text().find('Dial') >= 0:
            year = desc[2].get_text()

        # Strip all text before the year:
        # sometimes this is 'CIRCA ', sometimes 'MADE IN '
        year = remove_chars(year, 'start')

        # print("Year:", year)
        return year
    except Exception:
        return ''


def get_reference_number(desc):
    try:
        ref = desc[1].get_text()

        # Sometimes there is a string with 'REF&nbsp;',
        # the 'REF ' is then not recognized...
        ref = ref.replace('\xa0', ' ')

        refnumb = ref.find("REF ")
        if refnumb >= 0:
            ref = ref[refnumb:]
            ref = ref.lstrip("REF ").lstrip()
        elif ref.find("REFERENCE ") >= 0:
            ref = ref[ref.find("REFERENCE "):]
            ref = ref.lstrip("REFERENCE ").lstrip()
        else:
            ref = ''
        # print("Ref:", ref)
        return ref
    except Exception:
        return ''


def get_model_name(desc):
    try:
        mn = desc[1].get_text()

        # Sometimes there is a string with 'REF&nbsp;',
        # the 'REF ' is then not recognized...
        mn = mn.replace('\xa0', ' ')

        refnumb = mn.find("REF ")
        if refnumb >= 0:
            mn = mn[:refnumb]
            mn = mn.rstrip(", ")
        elif mn.find("REFERENCE ") >= 0:
            mn = mn[:mn.find("REFERENCE ")]
            mn = mn.rstrip(", ")

        # print("Model name:", mn)
        return mn
    except Exception:
        return ''


def get_sold_for(nav_con):
    try:
        sf = nav_con.find(
            'span', attrs={'class': 'css-15o7tlo'}).get_text()
        # print("Sf:", sf)
        return sf
    except Exception:
        return ''


def get_estimate_minimum(nav_con):
    try:
        emin = nav_con.find(
            'p', attrs={'class': 'css-1g8ar3q'}).get_text().split(' - ')[0]
        emin = emin.replace('\xa0', ' ')
        emin = remove_chars(emin, 'start')
        # print("Emin:", emin)
        return emin
    except Exception:
        return ''


def get_estimate_maximum(nav_con):
    try:
        emax = nav_con.find(
            'p', attrs={'class': 'css-1g8ar3q'}).get_text().split(' - ')[1]
        emax = emax.replace('\xa0', ' ')
        emax = remove_chars(emax, 'end')
        # print("Emax:", emax)
        return emax
    except Exception:
        return ''


def get_date_sold(soup):
    try:
        ds = ''
        # print("Date sold:", ds)
        return ds
    except Exception:
        return ''


def get_desc_index_of_attr(desc, attr):
    i = 0
    for p in desc:
        if p.get_text().find(attr) >= 0:
            return i
        i += 1
    return - 1


def get_desc_attr(desc, attr):
    index = get_desc_index_of_attr(desc, attr)
    a = ''
    if index != -1:
        a = desc[index]
        for tag in a.find_all('strong'):
            tag.decompose()
        a = a.get_text()
        a = a.replace('\xa0', ' ')
        a = a.lstrip(": ").lstrip()
    # print("%s: %s" % (attr, a))
    return a


def get_material(desc):
    try:
        return get_desc_attr(desc, 'Case')
    except Exception:
        return ''


def get_case_number(desc):
    try:
        return get_desc_attr(desc, 'Case number')
    except Exception:
        return ''


def get_description_condition(soup):
    try:
        dc = soup.find_all(
            'div', attrs={'class': 'css-xs9w33'})[1].find_all('p')
        dcstr = ''
        for p in dc:
            # In all condition reports there is something like
            # a footnote which always starts with 'Please note'
            if p.get_text().find('Please note that the movement has not been tested') >= 0:
                break
            elif p.get_text().find('Due to the ongoing situation with Coronavirus') >= 0:
                continue
            elif p.get_text().find('The lot is sold in the condition it is in at the time of sale') >= 0:
                break
            elif p.get_text().find('Watches Department is pleased to offer Condition Reports to potential purchasers') >= 0:
                break
            else:
                dcstr = dcstr + " " + p.get_text()
        # print("Condition:", dcstr)
        return dcstr
    except Exception:
        return ''


def get_diameter(desc):
    try:
        d = get_desc_attr(desc, 'Dimensions')
        if d == '':
            d = get_desc_attr(desc, 'Size')
        return d
    except Exception:
        return ''


def get_movement_number(desc):
    try:
        return get_desc_attr(desc, 'Movement number')
    except Exception:
        return ''


def get_calibre(desc):
    try:
        return get_desc_attr(desc, 'Calibre')
    except Exception:
        return ''


def get_bracelet_strap(desc):
    try:
        return get_desc_attr(desc, 'Closure')
    except Exception:
        return ''


def get_accessoires(desc):
    try:
        return get_desc_attr(desc, 'Accessories')
    except Exception:
        return ''


def get_signed(desc):
    try:
        return get_desc_attr(desc, 'Signed')
    except Exception:
        return ''


def get_next_url(nav_con):
    try:
        base_url = _DOMAIN_URL
        next_url = nav_con.find('a', {'class': 'css-14g6ay4'})['href']
        next_url = base_url + next_url
        # print("Next url:", next_url)
        return next_url
    except Exception as err:
        if err.args[0] == "'NoneType' object is not subscriptable":
            return ''
        else:
            print('Error!', err.args)


def get_auction_name(url):
    index = url.find('auction')
    url = url[index:]
    url_blocks = url.split('/')
    return url_blocks[1] + ': ' + url_blocks[2]


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @author: https://stackoverflow.com/a/34325723
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def is_watch(watch: Watch):
    # counter = 0
    # for key, value in vars(watch).items():
    #     # print(key[:4], ":", value)
    #     if value == '':
    #         counter += 1
    # # print("Counter:", counter)
    # if counter >= 5:
    #     return False
    # else:
    return True


def get_watches_from_auction(auction: Auction):
    start_time = time.time()

    auction_name = get_auction_name(auction.first_url)
    print("\n\n--- Auction name: '%s' ---" % auction_name)

    next_url = auction.first_url
    counter = 0
    watch_list = []

    while next_url != '' and counter < _MAX_NUMBER_OF_REQUESTS_PER_ACUCTION:
        watch, next_url = get_watch_info(next_url, auction.date)

        # print("\rLot: %d" % counter, end="\r")
        if watch == -1:
            # Error with page
            break
        elif is_watch(watch):
            watch_list.append(watch)
            counter += 1
            print("--- Number of watches in auction: %d ---" %
                  counter, end="\r")

    print("--- Number of watches in auction: %d ---" % counter)
    print("--- Auction scraping time: %s seconds ---" %
          (time.time() - start_time))
    return watch_list, counter


def get_watches_from_sothebys():
    total_list = []
    total_number_of_lots = 0
    total_start_time = time.time()

    index = 0
    l = len(_AUCTIONS)
    printProgressBar(
        index, l, prefix='\nTotal progress:', suffix='Complete', length=50)

    for auction in _AUCTIONS:
        auction_list, number_of_lots = get_watches_from_auction(auction)
        total_list.append(auction_list)
        total_number_of_lots += number_of_lots
        printProgressBar(
            index + 1, l, prefix='\nTotal progress:', suffix='Complete', length=50)
        index += 1

    print("\n--- Total number of watches: %s ---" % total_number_of_lots)
    print("--- Total number of auctions: %d ---" % l)
    print("--- Total Sothebys scraping time: %s seconds ---" %
          (time.time() - total_start_time))
    return total_list, total_number_of_lots


def format_watch_list_to_xlsx(watch_list):
    pass


# MAIN
# TERMINAL PRINT START
print("\n=============================")
print("=== Piekscraper: Sothebys ===")
print("=============================")

# get_watch_info(_TEST_URL_FIRST)
# print("")
# get_watch_info(_TEST_URL2)
# print("")
# get_watch_info(_TEST_URL_LAST)
# print("")
# get_watch_info(_TEST_URL_COLLECTOR)
# print("")
# get_watch_info(_TEST_URL3)
# get_watch_info(_TEST_URL4)
# get_watch_info(_TEST_URL5)
# get_watch_info(_TEST_URL6)

sothebys_watch_list = get_watches_from_sothebys()
format_watch_list_to_xlsx(sothebys_watch_list)
