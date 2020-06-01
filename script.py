import time
import requests
import json
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from watch import Watch
from auction import Auction
from sothebys_auctions import auctions as _AUCTIONS
from website import Website
from sothebys_old import Sothebys_old
from sothebys_new import Sothebys_new

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
_TEST_URL_OLD_DESIGN = 'https://www.sothebys.com/en/auctions/ecatalogue/2019/watches-db1902/lot.1.html'


def get_correct_website(url: str) -> Website:
    if url.find('.html') >= 0:
        return Sothebys_old(_DOMAIN_URL)
    else:
        return Sothebys_new(_DOMAIN_URL)


def printProgressBar(iteration, total, prefix='Auctions:', suffix='complete', decimals=1, length=50, fill='█', printEnd=""):
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

            print(watch.toJSON())

            return watch, w.get_next_url(nav_con)
        else:
            print("Error! Something went wrong. Response code:",
                  response.status_code)
            exit()
    except requests.exceptions.RequestException as err:
        print("Err:", err)
        exit()


def get_watches_from_auction(auction: Auction):
    start_time = time.time()

    first_url_done = False
    next_url = auction.first_url
    w = get_correct_website(next_url)
    auction_name = w.get_auction_name(next_url)
    print("\n\n--- Auction name: '%s' ---" % auction_name)

    counter = 0
    watch_list = []

    while next_url != '' and next_url is not None and counter < _MAX_NUMBER_OF_REQUESTS_PER_ACUCTION:
        # print('\n\nnexturl=', next_url)
        w = get_correct_website(next_url)
        watch, next_url = get_watch_info(w, auction, next_url, auction_name)

        # Make sure the program does not end up in an endless loop
        if first_url_done == False:
            first_url_done = True
        elif next_url == auction.first_url:
            next_url = ''

        # print("\rLot: %d" % counter, end="\r")
        if watch == -1:
            # Error with page
            break
        elif w.is_watch(watch):
            watch_list.append(watch)
            counter += 1
            print("--- Number of watches in auction: %d ---" %
                  counter, end="\r")

    print("--- Number of watches in auction: %d ---" % counter)
    print("--- Auction scraping time: %s seconds ---\n" %
          (time.time() - start_time))
    return watch_list, counter


def get_watches_from_sothebys():
    total_list = []
    total_number_of_watches = 0
    total_start_time = time.time()

    index = 0
    l = len(_AUCTIONS)
    printProgressBar(index, l)

    for auction in _AUCTIONS:
        auction_watch_list, number_of_watches = get_watches_from_auction(
            auction)
        total_list.append(auction_watch_list)
        total_number_of_watches += number_of_watches
        printProgressBar(index + 1, l)
        index += 1

    print("\n--- Total number of watches: %s ---" % total_number_of_watches)
    print("--- Total number of auctions: %d ---" % l)
    print("--- Total Sothebys scraping time: %s seconds ---" %
          (time.time() - total_start_time))
    return total_list, total_number_of_watches


def format_watch_list_to_xlsx(watch_list):
    pass


# MAIN
# TERMINAL PRINT START
print("\n=============================")
print("=== Piekscraper: Sothebys ===")
print("=============================\n")

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
