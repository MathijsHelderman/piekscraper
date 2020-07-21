import time
import requests
import json
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

from website import Website
from auction import Auction
from watch import Watch


class Antiquorum_old(Website):

    # Generic
    def get_auction_name(self, url):
        index = url.find('auctions')
        url = url[index:]
        url_blocks = url.split('/')
        for part in url_blocks:
            if part.find('ecatalogue') >= 0:
                url_blocks.remove(part)
        return url_blocks[1] + ': ' + url_blocks[2]

    def check_error_url(self, soup):
        try:
            text = soup.find('div', attrs={'class': 'notfound-top-text'}).find(
                'p', attrs={'class': 'apologise-text'}).get_text()
            return True if text.find('We apologize for the inconvenience.') >= 0 else False
        except Exception as err:
            if err.args[0] == "'NoneType' object has no attribute 'find'":
                return False
            else:
                print('Error sothebys old check_error_url():', err)
                return False

    def get_nav_con(self, soup):
        nav_con = soup.find('div', attrs={'class', 'lot-navigation'})
        # print('Navcon:', nav_con)
        # print('Navcon len:', len(nav_con))
        return nav_con

    def get_detail_con(self, soup):
        detail_con = soup.find('div', attrs={'class': 'lotdetail-header'})
        # print('Navcon:', detail_con)
        # print('Navcon len:', len(detail_con))
        return detail_con

    def get_desc(self, soup):
        desc = soup.find(
            'div', attrs={'class': 'lotdetail-details-content'})
        # print('desc:', desc)
        # print('desc len:', len(desc))
        return desc

    def get_desc_index_of_attr(self, desc, attr):
        i = 0
        for part in desc:
            if isinstance(part, str):
                if part.lower().find(attr.lower()) >= 0:
                    return i
            elif part.get_text().lower().find(attr.lower()) >= 0:
                return i
            i += 1
        return -1

    # def get_desc_attr(self, desc, attr):
    #     if desc.find('•') >= 0:
    #         print('middle')
    #     elif desc.find(',')>=

    #     index = self.get_desc_index_of_attr(desc, attr)
    #     a = ''
    #     if index != -1:
    #         a = desc[index]
    #         for tag in a.find_all('strong'):
    #             tag.decompose()
    #         a = a.get_text()
    #         a = a.replace('\xa0', ' ')
    #         a = a.lstrip(": ").lstrip()
    #     # print("%s: %s" % (attr, a))
    #     return a

    def get_desc_attr(self, desc, attr):
        a = ''
        desc_text = desc.find(
            'div', attrs={'class': 'lotdetail-description-text'})

        # determine how the description text is ordered
        desc_array_strong = desc_text.find_all('strong')
        if len(desc_array_strong) > 2:
            index = self.get_desc_index_of_attr(desc_array_strong, attr)
            if index != -1:
                a = desc_array_strong[index]
                a = a.next_sibling
        else:
            # The text will have to be searched for keywords
            desc_text = desc_text.get_text()

            # Check if the info is ordered by '•'
            if desc_text.find('•') >= 0:
                desc_arr_points = desc_text.split('•')
                index = self.get_desc_index_of_attr(
                    desc_arr_points, attr)
                if index != -1:
                    a = desc_arr_points[index]
            # Check if a is still empty and if the info is ordered by semicolons ';'
            if a == '' and desc_text.find(';') >= 0:
                desc_arr_semicolon = desc_text.split(';')
                index = self.get_desc_index_of_attr(
                    desc_arr_semicolon, attr)
                if index != -1:
                    a = desc_arr_semicolon[index]
            # Check if a is still empty
            if a == '':
                # final hope is checking if the information is ordered by commas
                desc_arr_commas = desc_text.split(',')
                # guess if it's not just a couple of commas used in the text instead of
                # seperators based on the number of occurrences
                if len(desc_arr_commas) > 3:
                    index = self.get_desc_index_of_attr(
                        desc_arr_commas, attr)
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

    def get_lot_number(self, detail_con):
        try:
            lot = detail_con.find(
                'div', attrs={'class': 'lotdetail-lotnumber'}).get_text()
            # print('Lot:', lot)
            return lot
        except Exception:
            return ''

    def get_next_url(self, nav_con):
        return ''

    def get_lot_detail(self, desc):
        detail = desc.find(
            'div', attrs={'class': 'lotdetail-subtitle'})
        NoneType = type(None)  # pylint: disable=unused-argument
        if detail is not None:
            detail = detail.get_text()
        else:
            detail = desc.find(
                'div', attrs={'class': 'lotdetail-guarantee'})
            if detail is not None:
                detail = detail.get_text()
            else:
                detail = None
        return detail

    # Watch
    def get_manufacturer(self, desc):
        try:
            mf = desc.find(
                'div', attrs={'class': 'lotdetail-guarantee'}).get_text()
            if len(mf) > 40:
                mf = mf.split(',')
                mf = mf[0]
            # print('mf:', mf)
            return mf
        except Exception:
            return ''

    def get_year(self, desc):
        try:
            text = self.get_lot_detail(desc)

            if text is None:
                return ''
            else:
                circa = text.find('CIRCA')
                if circa >= 0:
                    year = text[circa:]
                    year = super().remove_chars(year, 'start')
                    year = super().get_first_valid_year(year)

                else:
                    made_in = text.find('MADE IN')
                    if made_in >= 0:
                        year = text[made_in:]
                        year = super().remove_chars(year, 'start')
                        year = super().get_first_valid_year(year)
                    else:
                        # Else search for the first 4 digit number and hope it's the correct year
                        year = super().get_first_valid_year(text)

                year = year.replace('\xa0', ' ')
                return year
        except Exception:
            return ''

    def get_reference_number(self, desc):
        try:
            text = self.get_lot_detail(desc)

            if text is None:
                return ''
            else:
                text = text.split()
                ref_index = -1
                for t in text:
                    if t == 'REF':
                        ref_index = text.index(t)
                        break
                    elif t == 'REFERENCE':
                        ref_index = text.index(t)
                        break
                    elif t == 'REF.':
                        ref_index = text.index(t)
                        break

                if ref_index == -1:
                    return ''
                else:
                    ref = text[(ref_index + 1)]
                    # print('ref:', ref)
                    return ref
        except Exception:
            return ''

    def get_model_name(self, desc):
        try:
            mn = self.get_lot_detail(desc)
            mn_array = mn.split(',')
            if len(mn_array) > 2:
                mn = mn[1]
            mn = mn.replace('\xa0', ' ')
            mn = mn.lstrip()
            return mn
        except Exception:
            return ''

    def get_sold_for(self, detail_con):
        try:
            sf = detail_con.find(
                'div', attrs={'class': 'price-sold'}).get_text()
            sf = super().remove_chars(sf, 'start')
            sf = super().remove_chars(sf, 'end')
            # print("sf:", sf)
            return sf
        except Exception:
            return ''

    def get_estimate_minimum(self, detail_con):
        try:
            emin = detail_con.find(
                'span', attrs={'class': 'range-from'}).get_text()
            # print("Emin:", emin)
            return emin
        except Exception:
            return ''

    def get_estimate_maximum(self, detail_con):
        try:
            emax = detail_con.find(
                'span', attrs={'class': 'range-to'}).get_text()
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
        return ''

    def get_diameter(self, desc):
        try:
            d = self.get_desc_attr(desc, 'Dimensions')
            if d == '':
                d = self.get_desc_attr(desc, 'Size')
            if d == '':
                d = self.get_desc_attr(desc, 'diameter')
                d = d[d.find('diameter'):]
            if d == '':
                d = self.get_desc_attr(desc, 'length')
                d = d[d.find('length'):]
            if d == '':
                d = self.get_desc_attr(desc, 'mm')
                d = d[(d.find('mm') - 5):]

            d = super().remove_chars(d, 'start')
            # print('diameter:"%s"' % d)
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
            cal = self.get_desc_attr(desc, 'Calibre')
            if cal == '':
                cal = self.get_desc_attr(desc, 'cal.')
            if cal == '':
                cal = self.get_desc_attr(desc, 'cal')
            return cal
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
