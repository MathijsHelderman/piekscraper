import time
import requests
import json
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from watch import Watch
from auction import Auction
from sothebys_auctions import auctions as _AUCTIONS
from website import Website


class Sothebys_new(Website):

    # Generic
    def get_auction_name(self, url):
        index = url.find('auction')
        url = url[index:]
        url_blocks = url.split('/')
        return url_blocks[1] + ': ' + url_blocks[2]

    def check_error_url(self, soup):
        """
        On the Sotheby's website, if there is an unforseen error,
        like an unknown url, there is a h1 element with the text: 'Error'
        """
        try:
            h1s = soup.find_all('h1')
            for h1 in h1s:
                h1 = h1.get_text()
                if h1 == 'Error':
                    return True
            return False
        except Exception as err:
            print("Err:", err)
            return False

    def get_nav_con(self, soup):
        # First find the div in which the navigation container
        nav_con = soup.find(
            'div', attrs={'class': 'css-10pbwcw'})

        # print(nav_con)
        # print(len(nav_con))
        return nav_con

    def get_detail_con(self, soup):
        return self.get_nav_con(soup)

    def get_desc(self, soup):
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
        # In another case, there is a line: "OFFERED WITHOUT RESERVE". Also filter this one out.
        if clean_desc[0].get_text().find('PROPERTY') >= 0:
            clean_desc.remove(clean_desc[0])
        elif clean_desc[0].get_text().find('OFFERED') >= 0:
            clean_desc.remove(clean_desc[0])

        # print(clean_desc)
        # print(len(clean_desc))
        return clean_desc

    def get_desc_index_of_attr(self, desc, attr):
        i = 0
        for p in desc:
            if p.get_text().find(attr) >= 0:
                return i
            i += 1
        return - 1

    def get_desc_attr(self, desc, attr):
        index = self.get_desc_index_of_attr(desc, attr)
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

    def get_lot_number(self, detail_con):
        lot = detail_con.find(
            'span', attrs={'class': 'css-yxsueo'}).get_text()
        return lot

    def get_next_url(self, nav_con):
        try:
            base_url = self._DOMAIN_URL
            next_url = nav_con.find('a', {'class': 'css-1tgvpkp'})['href']
            next_url = base_url + next_url
            # print("Next url:", next_url)
            return next_url
        except Exception as err:
            if err.args[0] == "'NoneType' object is not subscriptable":
                return ''
            else:
                print('Error!', err.args)

    # Watch
    def get_manufacturer(self, desc):
        try:
            mf = desc[0].get_text()
            # print("Mf:", mf)
            return mf
        except Exception:
            return ''

    def get_year(self, desc):
        try:
            year = desc[3].get_text()

            # If a watch does not have the case at place desc[2]
            if desc[3].get_text().find('Dial') >= 0:
                year = desc[2].get_text()

            # Strip all text before the year:
            # sometimes this is 'CIRCA ', sometimes 'MADE IN '
            year = super().remove_chars(year, 'start')

            # print("Year:", year)
            return year
        except Exception:
            return ''

    def get_reference_number(self, desc):
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

    def get_model_name(self, desc):
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

    def get_sold_for(self, detail_con):
        try:
            sf = detail_con.find(
                'span', attrs={'class': 'css-15o7tlo'}).get_text()
            # print("Sf:", sf)
            return sf
        except Exception:
            return ''

    def get_estimate_minimum(self, detail_con):
        try:
            emin = detail_con.find(
                'p', attrs={'class': 'css-1g8ar3q'}).get_text().split(' - ')[0]
            emin = emin.replace('\xa0', ' ')
            emin = super().remove_chars(emin, 'start')
            # print("Emin:", emin)
            return emin
        except Exception:
            return ''

    def get_estimate_maximum(self, detail_con):
        try:
            emax = detail_con.find(
                'p', attrs={'class': 'css-1g8ar3q'}).get_text().split(' - ')[1]
            emax = emax.replace('\xa0', ' ')
            emax = super().remove_chars(emax, 'end')
            # print("Emax:", emax)
            return emax
        except Exception:
            return ''

    def get_date_sold(self, soup):
        try:
            ds = ''
            # print("Date sold:", ds)
            return ds
        except Exception:
            return ''

    def get_material(self, desc):
        try:
            return self.get_desc_attr(desc, 'Case')
        except Exception:
            return ''

    def get_case_number(self, desc):
        try:
            return self.get_desc_attr(desc, 'Case number')
        except Exception:
            return ''

    def get_description_condition(self, soup):
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

    def get_diameter(self, desc):
        try:
            d = self.get_desc_attr(desc, 'Dimensions')
            if d == '':
                d = self.get_desc_attr(desc, 'Size')
            return d
        except Exception:
            return ''

    def get_movement_number(self, desc):
        try:
            return self.get_desc_attr(desc, 'Movement number')
        except Exception:
            return ''

    def get_calibre(self, desc):
        try:
            return self.get_desc_attr(desc, 'Calibre')
        except Exception:
            return ''

    def get_bracelet_strap(self, desc):
        try:
            return self.get_desc_attr(desc, 'Closure')
        except Exception:
            return ''

    def get_accessoires(self, desc):
        try:
            return self.get_desc_attr(desc, 'Accessories')
        except Exception:
            return ''

    def get_signed(self, desc):
        try:
            return self.get_desc_attr(desc, 'Signed')
        except Exception:
            return ''
