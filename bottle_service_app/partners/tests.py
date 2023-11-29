from django.test import TestCase
from unittest.mock import patch, Mock

from distributor.models import Distributor
from location.models import Address
from location.tools import GeoLocation
from partners.matches import PartnerMatch
from partners.models import Partners
from restaurant.models import Restaurant


class TestPartnerMatch(TestCase):
    def setUp(self):
        self.partner_match = PartnerMatch()

    @patch.object(GeoLocation, 'get_distance_time')
    def test_create_if_match(self, mock_get_distance_time):
        d_address = Address.objects.create(
            address ='123 Main St',
            city='San Francisco',
            state='CA',
            zip='94111',
            latitude=1.0,
            longitude=2.0
        )
        r_address = Address.objects.create(
            address ='123 Back St',
            city='San Francisco',
            state='CA',
            zip='94111',
            latitude=3.0,
            longitude=4.0
        )
        distributor = Distributor.objects.create(name="Distributor", description="Type of distributor", address=d_address,
                                  minutes_distance=10, locomotion='walk')
        restaurant = Restaurant.objects.create(name="Distributor", description="Type of distributor", address=r_address,
                                minutes_distance=15)

        # Mock the result of get_distance_time
        mock_get_distance_time.return_value = (1000, 600)  # Assuming 1000 meters and 600 seconds

        partner_list = []
        self.partner_match.create_if_match(distributor, restaurant, partner_list)

        # Assert that the partner was created and added to the list
        self.assertEqual(len(partner_list), 1)
        self.assertEqual(partner_list[0].distributor, distributor)
        self.assertEqual(partner_list[0].restaurant, restaurant)
        self.assertEqual(partner_list[0].minutes_distance, 1000)
        self.assertEqual(partner_list[0].locomotion, 'walk')
        save_partner = Partners.objects.get(distributor=distributor, restaurant=restaurant)
        self.assertEqual(save_partner.distributor, distributor)
        self.assertEqual(save_partner.restaurant, restaurant)
        self.assertEqual(save_partner.minutes_distance, 1000)
        self.assertEqual(save_partner.locomotion, 'walk')

    @patch.object(GeoLocation, 'get_distance_time')
    def test_create_if_not_match(self, mock_get_distance_time):
        d_address = Address.objects.create(
            address='123 Main St',
            city='San Francisco',
            state='CA',
            zip='94111',
            latitude=1.0,
            longitude=2.0
        )
        r_address = Address.objects.create(
            address='123 Back St',
            city='San Francisco',
            state='CA',
            zip='94111',
            latitude=3.0,
            longitude=4.0
        )
        distributor = Distributor.objects.create(name="Distributor", description="Type of distributor", address=d_address,
                                                 minutes_distance=10, locomotion='walk')
        restaurant = Restaurant.objects.create(name="Distributor", description="Type of distributor", address=r_address,
                                               minutes_distance=5)

        # Mock the result of get_distance_time
        mock_get_distance_time.return_value = (1000, 600)  # Assuming 1000 meters and 600 seconds

        partner_list = []
        self.partner_match.create_if_match(distributor, restaurant, partner_list)

        # Assert that the partner was created and added to the list
        self.assertEqual(len(partner_list), 0)
