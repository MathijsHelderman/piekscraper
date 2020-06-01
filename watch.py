import json
from dataclasses import dataclass


@dataclass
class Watch:
    "A watch sold at the auction"

    def __init__(self, manufacturer, year, reference_number, model_name, sold_for, estimate_minimum, estimate_maximum, date_sold, material, case_number, description_condition, diameter, movement_number, calibre, bracelet_strap, accessoires, signed, auction_name, currency, lot_number, url):
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
        self.auction_name = auction_name
        self.currency = currency
        self.lot_number = lot_number
        self.url = url

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=False, indent=4)
