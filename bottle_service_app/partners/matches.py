from math import ceil

from distributor.models import Distributor
from location.tools import GeoLocation
from partners.models import Partners
from restaurant.models import Restaurant




class PartnerMatch:
    def __init__(self):
        self.geo_location = GeoLocation()

    def create_if_match(self, distributor, restaurant, partner_list):
        distributor_minutes_distance = distributor.minutes_distance
        locomotion_type = distributor.locomotion
        restaurant_minutes_distance = restaurant.minutes_distance
        max_minutes_distance = min(distributor_minutes_distance, restaurant_minutes_distance)
        if distributor.address is None:
            raise Exception('Distributor Address cannot be None')
        if restaurant.address is None:
            raise Exception('Restaurant Address cannot be None')
        distance_meters, duration_seconds = self.geo_location.get_distance_time(
            (distributor.address.latitude, distributor.address.longitude),
            (restaurant.address.latitude, restaurant.address.longitude),
            locomotion_type)
        duration_minutes = max(1, ceil(duration_seconds / 60))

        if duration_minutes <= max_minutes_distance:
            partners = Partners(distributor=distributor, restaurant=restaurant, minutes_distance=duration_minutes,
                                locomotion=locomotion_type)
            partners.save()
            partner_list.append(partners)

    def match_restaurant(self, restaurant):
        partner_list = []

        if restaurant is None:
            raise Exception('Restaurant cannot be None')

        potential_distributors = Distributor.objects.exclude(address__isnull=True)
        for distributor in potential_distributors:
            self.create_if_match(distributor, restaurant, partner_list)
        return partner_list

    def match_distributor(self, distributor):
        partner_list = []

        if distributor is None:
            raise Exception('Distributor cannot be None')

        potential_restaurants = Restaurant.objects.exclude(address__isnull=True)
        for restaurant in potential_restaurants:
            self.create_if_match(distributor, restaurant, partner_list)
        return partner_list
