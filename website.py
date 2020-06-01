from abc import ABC, abstractmethod
from auction import Auction
from watch import Watch


class Website(ABC):

    # Init
    def __init__(self, url):
        self._DOMAIN_URL = url

    # Helper methods
    def remove_chars(self, string, loc):
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

    def get_first_number(self, string):
        # all numbers in the string of length 4, separated either by space ' ' or comma ','
        number_array = [str(s) for s in string.split()
                        if len(s) == 4 and s.isdigit()]
        if len(number_array) == 0:
            number_array = [str(s) for s in string.split(',')
                            if len(s) == 4 and s.isdigit()]

        # print('numbarr:', number_array)
        # return the first 4 digit number
        return number_array[0] if len(number_array) > 0 else ''

    def is_watch(self, watch: Watch):
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

    # Generic
    @abstractmethod
    def get_auction_name(self, url):
        pass

    @abstractmethod
    def check_error_url(self, soup):
        pass

    @abstractmethod
    def get_nav_con(self, soup):
        pass

    @abstractmethod
    def get_detail_con(self, soup):
        pass

    @abstractmethod
    def get_desc(self, soup):
        pass

    @abstractmethod
    def get_desc_index_of_attr(self, desc, attr):
        pass

    @abstractmethod
    def get_desc_attr(self, desc, attr):
        pass

    @abstractmethod
    def get_lot_number(self, detail_con):
        pass

    @abstractmethod
    def get_next_url(self, nav_con):
        pass

    # Watch
    @abstractmethod
    def get_manufacturer(self, desc):
        pass

    @abstractmethod
    def get_year(self, desc):
        pass

    @abstractmethod
    def get_reference_number(self, desc):
        pass

    @abstractmethod
    def get_model_name(self, desc):
        pass

    @abstractmethod
    def get_sold_for(self, detail_con):
        pass

    @abstractmethod
    def get_estimate_minimum(self, detail_con):
        pass

    @abstractmethod
    def get_estimate_maximum(self, detail_con):
        pass

    @abstractmethod
    def get_date_sold(self, soup):
        pass

    @abstractmethod
    def get_material(self, desc):
        pass

    @abstractmethod
    def get_case_number(self, desc):
        pass

    @abstractmethod
    def get_description_condition(self, soup):
        pass

    @abstractmethod
    def get_diameter(self, desc):
        pass

    @abstractmethod
    def get_movement_number(self, desc):
        pass

    @abstractmethod
    def get_calibre(self, desc):
        pass

    @abstractmethod
    def get_bracelet_strap(self, desc):
        pass

    @abstractmethod
    def get_accessoires(self, desc):
        pass

    @abstractmethod
    def get_signed(self, desc):
        pass
