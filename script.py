import time
from time import sleep
import requests
import json
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from openpyxl import Workbook

from website import Website
from auction import Auction
from watch import Watch

from sothebys_auctions import auctions as _AUCTIONS_SOTH
from sothebys_auctions import test_auctions as _TEST_AUCTIONS_SOTH
from sothebys_old import Sothebys_old
from sothebys_new import Sothebys_new

from antiquorum_auctions import auctions as _AUCTIONS_ANTI
from antiquorum_auctions import test_auctions as _TEST_AUCTIONS_ANTI
from antiquorum_old import Antiquorum_old

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
# EDIT: It seems as though the design of the website changed and remains different for auctions before a certain date.
# Weird and annoying as it is, because of the amount of data that's in the old format, it will need a scraper as well.
# The url reflects which design is used on the lot. Ones with .html at the end of the url are of the old format.


# SETUP
_SCRAPING_WEBSITE = 'Antiquorum'
_EXCEL_NAME = 'antiquorum_list_1'
_DEV = True

#
# CONSTANTS
#
if _SCRAPING_WEBSITE == 'Sothebys':
    _DOMAIN_URL = 'https://www.sothebys.com'
elif _SCRAPING_WEBSITE == 'Antiquorum':
    _DOMAIN_URL = 'https://catalog.antiquorum.swiss'

# If _DEV is true, the program runs in developer mode:
_MAX_NUMBER_OF_REQUESTS_PER_ACUCTION = 5 if _DEV else 10000
if _SCRAPING_WEBSITE == 'Sothebys':
    _AUCTIONS = _TEST_AUCTIONS_SOTH if _DEV else _AUCTIONS_SOTH
elif _SCRAPING_WEBSITE == 'Antiquorum':
    _AUCTIONS = _TEST_AUCTIONS_ANTI if _DEV else _AUCTIONS_ANTI


def printProgressBar(iteration, total, prefix='Auctions:', suffix='complete', printEnd="", decimals=1, length=50, fill='█'):
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
        printEnd    - Optional  : end character (e.g. "\r", "\r") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def get_correct_website(url: str) -> Website:
    if url.find('sothebys') >= 0:
        if url.find('.html') >= 0:
            return Sothebys_old(_DOMAIN_URL)
        else:
            return Sothebys_new(_DOMAIN_URL)
    else:
        return Antiquorum_old(_DOMAIN_URL)


def get_watch_info(w: Website, auction: Auction, url: str, auction_name: str):
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
            if w.check_error_url(soup):
                print('\n\nERROR! Lot not found at url:', url, end="\n\n\n")
                return -1, w.get_next_url(soup)

            try:
                # The navigation container which holds next url
                nav_con = w.get_nav_con(soup)

                # Details container
                detail_con = w.get_detail_con(soup)

                # The description block on the page of a watch
                desc = w.get_desc(soup)

            except Exception as err:
                print(err)
                return -1, w.get_next_url(soup)

            # lot_number = w.get_lot_number(detail_con)
            # print("\n\nLot:", lot_number)
            # print("Lot:", lot_number, "url:", url)

            if auction.date != '':
                date = auction.date
            else:
                date = w.get_date_sold(soup)

            watch = Watch(
                # Important
                w.get_manufacturer(desc),
                w.get_year(desc),
                w.get_reference_number(desc),
                w.get_model_name(desc),
                w.get_sold_for(detail_con),
                w.get_estimate_minimum(detail_con),
                w.get_estimate_maximum(detail_con),
                date,
                w.get_material(desc),
                w.get_case_number(desc),
                w.get_description_condition(soup),
                # Optional
                w.get_diameter(desc),
                w.get_movement_number(desc),
                w.get_calibre(desc),
                w.get_bracelet_strap(desc),
                w.get_accessoires(desc),
                w.get_signed(desc),
                auction_name,
                auction.currency,
                w.get_lot_number(detail_con),
                url
            )

            # print(watch.toJSON())

            return watch, w.get_next_url(nav_con)
        else:
            print("Error! Something went wrong. Response code:",
                  response.status_code)
            exit()
    except requests.exceptions.RequestException as err:
        print('\n\nError:', err)
        return -2, url


def get_watches_from_auction(auction: Auction):
    start_time = time.time()

    first_url_done = False
    retried_connection = False
    next_url = auction.first_url
    w = get_correct_website(next_url)
    auction_name = w.get_auction_name(next_url)
    print("\n\n--- Auction name: '%s' ---" % auction_name)

    counter = 0
    watch_list = []

    while next_url != '' and next_url is not None and counter < _MAX_NUMBER_OF_REQUESTS_PER_ACUCTION:
        # To prevent the next_url from being the same as the current url
        # it needs to be checked after getting the next_url. An example of this
        # error is found at: https://www.sothebys.com/en/auctions/ecatalogue/2013/important-watches-hk0476/lot.2458.html,
        # where the next url button is linked to the same lot, which causes an endless loop...
        last_url = next_url

        # print('\n\nnexturl=', next_url)
        w = get_correct_website(next_url)
        watch, next_url = get_watch_info(w, auction, next_url, auction_name)

        # Make sure the program does not end up in an endless loop
        if first_url_done == False:
            first_url_done = True
        elif next_url == auction.first_url:
            next_url = ''
        elif next_url == last_url:
            index = next_url.find('/lot.')
            new_lot_number = int(watch.lot_number) + 1
            new_end_url_string = '/lot.' + str(new_lot_number) + '.html'
            new_url = next_url[:index] + new_end_url_string
            next_url = new_url

        # print("\rLot: %d" % counter, end="\r")
        if watch == -1:
            # Error with page
            break
        elif watch == -2:
            if retried_connection:
                break
            else:
                retried_connection = True
                sleep(300)
        elif w.is_watch(watch):
            watch_list.append(watch)
            counter += 1
            print("--- Number of watches in auction: %d ---" %
                  counter, end="\r")

        if counter == _MAX_NUMBER_OF_REQUESTS_PER_ACUCTION and not _DEV:
            print('ERROR! Too many lots in one auction, infinite loop...')
            exit()
            raise SystemExit

    print("--- Number of watches in auction: %d ---" % counter)
    print("--- Auction scraping time: %s seconds ---\n" %
          (time.time() - start_time))
    return watch_list, counter

def get_watches_from_website():
    total_list = []
    total_number_of_watches = 0
    total_start_time = time.time()

    index = 0
    l = len(_AUCTIONS)
    printProgressBar(index, l)

    for auction in _AUCTIONS:
        if _SCRAPING_WEBSITE == 'Antiquorum':
            auction = createAuctionFromURL(auction) ## TODO: Make this nicer
        auction_watch_list, number_of_watches = get_watches_from_auction(
            auction)
        total_list += auction_watch_list
        total_number_of_watches += number_of_watches
        index += 1
        printProgressBar(index, l)

    print("\n--- Total number of watches: %s ---" % total_number_of_watches)
    print("--- Total number of auctions: %d ---" % l)
    print("--- Total Sothebys scraping time: %s seconds ---" %
          (time.time() - total_start_time))
    return total_list, total_number_of_watches


def createAuctionFromURL(auction_url: str):
    """
    Different kind of auction definitions on the different sites.
    TODO: Needs to be better accomodated instead of this ugly method.
    """



def format_watch_list_to_xlsx(watch_list):
    start_time = time.time()
    if len(watch_list) == 0:
        raise Exception('No watches in watch_list.')
    try:
        # Creating a excel heet
        workbook = Workbook()
        sheet = workbook.active
        print('\nStarting the process of creating the Excel file...\n')

        # Append column names first
        sheet.append([
            "manufacturer",
            "year",
            "reference_number",
            "model_name",
            "sold_for",
            "estimate_minimum",
            "estimate_maximum",
            "date_sold",
            "material",
            "case_number",
            "description_condition",
            "diameter",
            "movement_number",
            "calibre",
            "bracelet_strap",
            "accessoires",
            "signed",
            "auction_name",
            "currency",
            "lot_number",
            "url"])

        index = 0
        l = len(watch_list)
        printProgressBar(index, l, '\rWatches converted:', '\r', '\r')

        for w in watch_list:
            sheet_data = [
                w.manufacturer,
                w.year,
                w.reference_number,
                w.model_name,
                w.sold_for,
                w.estimate_minimum,
                w.estimate_maximum,
                w.date_sold,
                w.material,
                w.case_number,
                w.description_condition,
                w.diameter,
                w.movement_number,
                w.calibre,
                w.bracelet_strap,
                w.accessoires,
                w.signed,
                w.auction_name,
                w.currency,
                w.lot_number,
                w.url
            ]
            sheet.append(sheet_data)

            index += 1
            printProgressBar(index, l, '\rWatches converted:', '\r', '\r')

        print('\n--- Done adding watches to Excel file ---')
        path = '/Users/matti/Desktop/' + _EXCEL_NAME + '.xlsx'
        print('--- Saving Excel file to:"%s" ---' % path)
        workbook.save(filename=path)
        print('--- Excel file saved ---')
        print("--- Excel file creation time: %s seconds ---" %
              (time.time() - start_time))
    except Exception as err:
        print('Error while creating Excel file:', err)
        exit()


# MAIN
# TERMINAL PRINT START
print("\n=============================")
print("=== Piekscraper: %s ===" % _SCRAPING_WEBSITE)
print("=============================\n")

watch_list, total_number_of_watches = get_watches_from_website()
if not _DEV:
    format_watch_list_to_xlsx(watch_list)
# print('Watchlist:', watch_list)
# print('First watch:', watch_list[0].toJSON())
