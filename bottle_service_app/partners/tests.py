from django.test import TestCase
from unittest.mock import patch, Mock

from distributor.models import Distributor, LocomotionType
from location.models import Address
from location.tools import GeoLocation
from partners.matches import PartnerMatch
from partners.models import Partners, PartnerStatus
from partners.views import update_status
from restaurant.models import Restaurant
from django.urls import reverse
from django.contrib.auth import get_user_model
from authentication.enums import BottleServiceAccountType


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
        self.assertEqual(partner_list[0].minutes_distance, 10)
        self.assertEqual(partner_list[0].locomotion, 'walk')
        save_partner = Partners.objects.get(distributor=distributor, restaurant=restaurant)
        self.assertEqual(save_partner.distributor, distributor)
        self.assertEqual(save_partner.restaurant, restaurant)
        self.assertEqual(save_partner.minutes_distance, 10)
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


class PartnerUpdateStatusTests(TestCase):
    def setUp(self):
        self.r_user = get_user_model().objects.create_user(
            email='r_test@example.com',
            account_type=BottleServiceAccountType.RESTAURANT,
            password='password'
        )
        self.d_user = get_user_model().objects.create_user(
            email='d_test@example.com',
            account_type=BottleServiceAccountType.DISTRIBUTOR,
            password='password'
        )
        self.r_user_bad = get_user_model().objects.create_user(
            email='r_bad_test@example.com',
            account_type=BottleServiceAccountType.RESTAURANT,
            password='password'
        )
        self.d_user = get_user_model().objects.create_user(
            email='d_bad_test@example.com',
            account_type=BottleServiceAccountType.DISTRIBUTOR,
            password='password'
        )
        self.partners = Partners.objects.create(restaurant=self.r_user.restaurant, distributor=self.d_user.distributor,
                                                status=PartnerStatus.MATCHED, locomotion=LocomotionType.WALK,
                                                minutes_distance=1000,)
        self.partners_id = self.partners.id

# Test request match
    def test_update_partner_status_restaurant_request_match_good_path(self):
        user = self.r_user
        request_type = 'match'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.MATCHED
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL)

    def test_update_partner_status_distributor_request_match_good_path(self):
        user = self.d_user
        request_type = 'match'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.MATCHED
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_RESTAURANT_APPROVAL)

    def test_update_partner_status_restaurant_request_match_bad_path_restaurant_id_not_matched(self):
        user = self.r_user_bad
        request_type = 'match'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.MATCHED
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.MATCHED)

    def test_update_partner_status_restaurant_request_match_bad_path_current_state_not_matched(self):
        user = self.r_user_bad
        request_type = 'match'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL)

# Test request reject

    def test_update_partner_status_restaurant_request_reject_good_path_matched(self):
        user = self.r_user
        request_type = 'reject'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.MATCHED
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.REJECTED_BY_RESTAURANT)

    def test_update_partner_status_distributor_request_reject_good_path_matched(self):
        user = self.d_user
        request_type = 'reject'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.MATCHED
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.REJECTED_BY_DISTRIBUTOR)

    def test_update_partner_status_restaurant_request_reject_good_path_pending_restaurant(self):
        user = self.r_user
        request_type = 'reject'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_RESTAURANT_APPROVAL
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.REJECTED_BY_RESTAURANT)

    def test_update_partner_status_distributor_request_reject_good_path_pending_distributor(self):
        user = self.d_user
        request_type = 'reject'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.REJECTED_BY_DISTRIBUTOR)

    def test_update_partner_status_restaurant_request_reject_bad_path_pending_distributor(self):
        user = self.r_user
        request_type = 'reject'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL)

    def test_update_partner_status_distributor_request_reject_bad_path_pending_restaurant(self):
        user = self.d_user
        request_type = 'reject'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_RESTAURANT_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_RESTAURANT_APPROVAL)

# Test request dissolve

    def test_update_partner_status_distributor_request_dissolve_good_pathr(self):
        user = self.d_user
        request_type = 'dissolve'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.APPROVED
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.MATCHED)

# Test accept request

    def test_update_partner_status_distributor_request_accept_good_path(self):
        user = self.d_user
        request_type = 'accept'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.APPROVED)

    def test_update_partner_status_restaurant_request_accept_good_path(self):
        user = self.r_user
        request_type = 'accept'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_RESTAURANT_APPROVAL
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.APPROVED)

    def test_update_partner_status_distributor_request_accept_bad_path_wrong_pending_status(self):
        user = self.d_user
        request_type = 'accept'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_RESTAURANT_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_RESTAURANT_APPROVAL)

    def test_update_partner_status_restaurant_request_accept_bad_path_wrong_pending_status(self):
        user = self.r_user
        request_type = 'accept'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL)

# Test cancel request

    def test_update_partner_status_distributor_request_cancel_good_path(self):
        user = self.d_user
        request_type = 'cancel'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_RESTAURANT_APPROVAL
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.MATCHED)

    def test_update_partner_status_restaurant_request_cancel_good_path(self):
        user = self.r_user
        request_type = 'cancel'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.MATCHED)

    def test_update_partner_status_distributor_request_cancel_bad_path_wrong_pending_status(self):
        user = self.d_user
        request_type = 'cancel'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_DISTRIBUTOR_APPROVAL)

    def test_update_partner_status_restaurant_request_cancel_bad_path_wrong_pending_status(self):
        user = self.r_user
        request_type = 'cancel'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.PENDING_RESTAURANT_APPROVAL
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.PENDING_RESTAURANT_APPROVAL)

# Test reopen request

    def test_update_partner_status_distributor_request_reopen_good_path(self):
        user = self.d_user
        request_type = 'reopen'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.REJECTED_BY_DISTRIBUTOR
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.MATCHED)

    def test_update_partner_status_restaurant_request_reopen_good_path(self):
        user = self.r_user
        request_type = 'reopen'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.REJECTED_BY_RESTAURANT
        self.partners.save()

        update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.MATCHED)

    def test_update_partner_status_restaurant_request_reopen_bad_path_wrong_pending_status(self):
        user = self.r_user
        request_type = 'reopen'
        partner_id = self.partners_id

        self.partners.status = PartnerStatus.REJECTED_BY_DISTRIBUTOR
        self.partners.save()

        with self.assertRaises(Exception):
            update_status(user, request_type, partner_id)

        partners = Partners.objects.get(id=partner_id)

        self.assertEqual(partners.status_enum, PartnerStatus.REJECTED_BY_DISTRIBUTOR)
