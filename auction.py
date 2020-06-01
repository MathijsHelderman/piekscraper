class Auction:
    """
    Auction of watches
    """

    def __init__(self, first_url, date='', currency='USD', number_of_lots=0):
        self.first_url = first_url
        self.date = date
        self.currency = currency
        self.number_of_lots = number_of_lots
