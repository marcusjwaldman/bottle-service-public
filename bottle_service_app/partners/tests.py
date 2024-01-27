from django.test import TestCase
from unittest.mock import patch, Mock

from distributor.models import Distributor, LocomotionType
from location.models import Address
from location.tools import GeoLocation
from partners.matches import PartnerMatch
from partners.menu import customer_menu
from partners.models import Partners, PartnerStatus, Menu, MenuStatus, MenuItemCategory, Item, MenuItem
from partners.views import update_status, update_menu_status
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
        self.d_user_bad = get_user_model().objects.create_user(
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


class MenuUpdateStatusTests(TestCase):
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
        self.d_user_bad = get_user_model().objects.create_user(
            email='d_bad_test@example.com',
            account_type=BottleServiceAccountType.DISTRIBUTOR,
            password='password'
        )
        self.partners = Partners.objects.create(restaurant=self.r_user.restaurant, distributor=self.d_user.distributor,
                                                locomotion=LocomotionType.WALK,
                                                minutes_distance=1000,)
        self.partners_id = self.partners.id

        self.menu = Menu.objects.create(
            distributor=self.d_user.distributor,
            restaurant=self.r_user.restaurant,
            delivery_minutes=100,
        )
        self.menu_id = self.menu.id

# Test request match
    def test_update_menu_status_submit_good_path(self):
        user = self.d_user
        request_type = 'submit'
        menu_id = self.menu_id

        self.partners.status = PartnerStatus.APPROVED
        self.partners.save()

        self.menu.status = MenuStatus.DRAFT
        self.menu.save()

        update_menu_status(user, request_type, menu_id)

        menu = Menu.objects.get(id=menu_id)

        self.assertEqual(menu.status_enum, MenuStatus.PENDING_RESTAURANT_APPROVAL)

# Test request match
    def test_update_menu_status_submit_bab_path_wrong_pending_status(self):
        user = self.d_user
        request_type = 'submit'
        menu_id = self.menu_id

        self.partners.status = PartnerStatus.APPROVED
        self.partners.save()

        self.menu.status = MenuStatus.PENDING_RESTAURANT_APPROVAL
        self.menu.save()

        with self.assertRaises(Exception):
            update_menu_status(user, request_type, menu_id)

        menu = Menu.objects.get(id=menu_id)

        self.assertEqual(menu.status_enum, MenuStatus.PENDING_RESTAURANT_APPROVAL)

# Test request match
    def test_update_menu_status_submit_bab_path_wrong_user_type(self):
        user = self.r_user
        request_type = 'submit'
        menu_id = self.menu_id

        self.partners.status = PartnerStatus.APPROVED
        self.partners.save()

        self.menu.status = MenuStatus.DRAFT
        self.menu.save()

        with self.assertRaises(Exception):
            update_menu_status(user, request_type, menu_id)

        menu = Menu.objects.get(id=menu_id)

        self.assertEqual(menu.status_enum, MenuStatus.DRAFT)

# Test request match
    def test_update_menu_status_submit_bab_path_no_partner(self):
        user = self.d_user_bad
        request_type = 'submit'
        menu_id = self.menu_id

        self.partners.status = PartnerStatus.APPROVED
        self.partners.save()

        self.menu.status = MenuStatus.DRAFT
        self.menu.save()

        with self.assertRaises(Exception):
            update_menu_status(user, request_type, menu_id)

        menu = Menu.objects.get(id=menu_id)

        self.assertEqual(menu.status_enum, MenuStatus.DRAFT)

# Test request match
    def test_update_menu_status_submit_bab_path_wrong_partner_status(self):
        user = self.d_user
        request_type = 'submit'
        menu_id = self.menu_id

        self.partners.status = PartnerStatus.REJECTED_BY_RESTAURANT
        self.partners.save()

        self.menu.status = MenuStatus.DRAFT
        self.menu.save()

        with self.assertRaises(Exception):
            update_menu_status(user, request_type, menu_id)

        menu = Menu.objects.get(id=menu_id)

        self.assertEqual(menu.status_enum, MenuStatus.DRAFT)

# Test request match
    def test_update_menu_status_submit_bab_path_wrong_partner(self):
        user = self.d_user
        request_type = 'submit'
        menu_id = self.menu_id

        self.partners.status = PartnerStatus.APPROVED
        self.partners.distributor = self.d_user_bad.distributor
        self.partners.save()

        self.menu.status = MenuStatus.DRAFT
        self.menu.save()

        with self.assertRaises(Exception):
            update_menu_status(user, request_type, menu_id)

        menu = Menu.objects.get(id=menu_id)

        self.assertEqual(menu.status_enum, MenuStatus.DRAFT)


class CustomerMenuTests(TestCase):
    def test_grouped_by_category(self):
        # Arrange
        restaurant = Restaurant.objects.create(name="Restaurant A")
        distributor = Distributor.objects.create(name="Distributor A")
        menu = Menu.objects.create(restaurant=restaurant, distributor=distributor, status=MenuStatus.APPROVED)
        category = MenuItemCategory.objects.get(name="Beverage")
        item1 = Item.objects.create(name="Item 1", category=category, price=10, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category, price=15, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu, item=item1)
        menu_item2 = MenuItem.objects.create(parent_menu=menu, item=item2)

        # Act
        result = customer_menu(restaurant)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertIn(category, result)
        self.assertEqual(len(result[category]), 2)
        self.assertIn(menu_item1, result[category])
        self.assertIn(menu_item2, result[category])

    def test_grouped_by_2_categories(self):
        # Arrange
        restaurant = Restaurant.objects.create(name="Restaurant A")
        distributor = Distributor.objects.create(name="Distributor A")
        menu = Menu.objects.create(restaurant=restaurant, distributor=distributor, status=MenuStatus.APPROVED)
        category_1 = MenuItemCategory.objects.get(name="Red Wine")
        category_2 = MenuItemCategory.objects.get(name="White Wine")
        item1 = Item.objects.create(name="Item 1", category=category_1, price=10, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category_2, price=15, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu, item=item1)
        menu_item2 = MenuItem.objects.create(parent_menu=menu, item=item2)

        # Act
        result = customer_menu(restaurant)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn(category_1, result)
        self.assertIn(category_2, result)
        self.assertEqual(len(result[category_1]), 1)
        self.assertEqual(len(result[category_2]), 1)
        self.assertIn(menu_item1, result[category_1])
        self.assertIn(menu_item2, result[category_2])

    def test_sorted_by_price(self):
        # Arrange
        restaurant = Restaurant.objects.create(name="Restaurant A")
        distributor = Distributor.objects.create(name="Distributor A")
        menu = Menu.objects.create(restaurant=restaurant, distributor=distributor, status=MenuStatus.APPROVED)
        category = MenuItemCategory.objects.get(name="Beverage")
        item1 = Item.objects.create(name="Item 1", category=category, price=15, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category, price=10, distributor=distributor, description="Test")
        item3 = Item.objects.create(name="Item 3", category=category, price=12, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu, item=item1)
        menu_item2 = MenuItem.objects.create(parent_menu=menu, item=item2)
        menu_item3 = MenuItem.objects.create(parent_menu=menu, item=item3)

        # Act
        result = customer_menu(restaurant)

        # Assert
        self.assertEqual(menu_item2.id, result[category][0].id)
        self.assertEqual(menu_item3.id, result[category][1].id)
        self.assertEqual(menu_item1.id, result[category][2].id)


    def test_sorted_by_calcuated_price(self):
        # Arrange
        restaurant = Restaurant.objects.create(name="Restaurant A")
        distributor = Distributor.objects.create(name="Distributor A")
        menu = Menu.objects.create(restaurant=restaurant, distributor=distributor, status=MenuStatus.APPROVED)
        category = MenuItemCategory.objects.get(name="Beverage")
        item1 = Item.objects.create(name="Item 1", category=category, price=15, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category, price=10, distributor=distributor, description="Test")
        item3 = Item.objects.create(name="Item 3", category=category, price=12, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu, item=item1, overridden_price=100)
        menu_item2 = MenuItem.objects.create(parent_menu=menu, item=item2, percentage_adjustment=100)
        menu_item3 = MenuItem.objects.create(parent_menu=menu, item=item3, dollar_adjustment=15)

        # Act
        result = customer_menu(restaurant)

        # Assert
        self.assertEqual(menu_item2.id, result[category][0].id)
        self.assertEqual(menu_item3.id, result[category][1].id)
        self.assertEqual(menu_item1.id, result[category][2].id)

    def test_only_restaurant_menus(self):
        # Arrange
        restaurant_a = Restaurant.objects.create(name="Restaurant A")
        restaurant_b = Restaurant.objects.create(name="Restaurant B")
        distributor = Distributor.objects.create(name="Distributor A")
        menu_a = Menu.objects.create(restaurant=restaurant_a, distributor=distributor, status=MenuStatus.APPROVED)
        menu_b = Menu.objects.create(restaurant=restaurant_b, distributor=distributor, status=MenuStatus.APPROVED)
        category = MenuItemCategory.objects.get(name="Beverage")
        item1 = Item.objects.create(name="Item 1", category=category, price=10, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category, price=15, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu_a, item=item1)
        menu_item2 = MenuItem.objects.create(parent_menu=menu_b, item=item2)

        # Act
        result = customer_menu(restaurant_a)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[category]), 1)
        self.assertIn(menu_item1,result[category])
        self.assertNotIn(menu_item2, result[category])


    def test_only_approved_restaurant_menus(self):
        # Arrange
        restaurant_a = Restaurant.objects.create(name="Restaurant A")
        distributor = Distributor.objects.create(name="Distributor A")
        menu_a = Menu.objects.create(restaurant=restaurant_a, distributor=distributor, status=MenuStatus.APPROVED)
        menu_b = Menu.objects.create(restaurant=restaurant_a, distributor=distributor, status=MenuStatus.DRAFT)
        category = MenuItemCategory.objects.get(name="Beverage")
        item1 = Item.objects.create(name="Item 1", category=category, price=10, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category, price=15, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu_a, item=item1)
        menu_item2 = MenuItem.objects.create(parent_menu=menu_b, item=item2)

        # Act
        result = customer_menu(restaurant_a)

        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[category]), 1)
        self.assertIn(menu_item1,result[category])
        self.assertNotIn(menu_item2,result[category])

    def test_none_restaurant_parameter(self):
        # Act
        with self.assertRaises(TypeError):
            customer_menu(None)

    def test_invalid_restaurant_parameter(self):
        # Arrange
        restaurant = "Restaurant A"

        # Act and Assert
        with self.assertRaises(TypeError):
            customer_menu(restaurant)

    def test_no_approved_restaurant_menus(self):
        # Arrange
        restaurant_a = Restaurant.objects.create(name="Restaurant A")
        restaurant_b = Restaurant.objects.create(name="Restaurant B")
        distributor = Distributor.objects.create(name="Distributor A")
        menu_a = Menu.objects.create(restaurant=restaurant_a, distributor=distributor, status=MenuStatus.APPROVED)
        menu_b = Menu.objects.create(restaurant=restaurant_a, distributor=distributor, status=MenuStatus.DRAFT)
        category = MenuItemCategory.objects.get(name="Beverage")
        item1 = Item.objects.create(name="Item 1", category=category, price=10, distributor=distributor, description="Test")
        item2 = Item.objects.create(name="Item 2", category=category, price=15, distributor=distributor, description="Test")
        menu_item1 = MenuItem.objects.create(parent_menu=menu_a, item=item1)
        menu_item2 = MenuItem.objects.create(parent_menu=menu_b, item=item2)

        # Act
        result = customer_menu(restaurant_b)

        # Assert
        self.assertEqual(result, {})


class CalculatePriceTest(TestCase):

    def setUp(self):
        self.distributor = Distributor.objects.create(name="Distributor")
        self.restaurant = Restaurant.objects.create(name="Restaurant")
        self.item = Item.objects.create(name="Item", price=10, distributor=self.distributor, description="Test")
        self.menu = Menu.objects.create(
            restaurant=self.restaurant,
            distributor=self.distributor,
            status=MenuStatus.APPROVED
        )
        self.menu_item = MenuItem(id=1, parent_menu=self.menu, item=self.item, overridden_price=None,
                             percentage_adjustment=None, dollar_adjustment=None)

        super().setUp()

    def test_calculated_price_all_fields_null(self):
        expected_price = self.menu_item.item.price
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_overridden_price_not_null(self):
        self.menu_item.overridden_price = 20
        expected_price = self.menu_item.overridden_price
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_percentage_adjustment_not_null(self):
        self.menu_item.percentage_adjustment = 10.00
        expected_price = (self.menu_item.item.price + (self.menu_item.item.price * self.menu_item.percentage_adjustment)
                          / 100)
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_overridden_price_zero(self):
        self.menu_item.overridden_price = 0
        expected_price = self.menu_item.item.price
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_percentage_adjustment_zero(self):
        self.menu_item.percentage_adjustment = 0
        expected_price = self.menu_item.item.price
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_dollar_adjustment_zero(self):
        self.menu_item.dollar_adjustment = 0
        expected_price = self.menu_item.item.price
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_overridden_price_not_null_and_dollar_adjustment(self):
        self.menu_item.overridden_price = 20
        self.menu_item.dollar_adjustment = 10
        expected_price = self.menu_item.overridden_price + self.menu_item.dollar_adjustment
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_overridden_price_not_null_and_percentage_adjustment(self):
        self.menu_item.overridden_price = 20
        self.menu_item.percentage_adjustment = 10
        expected_price = (self.menu_item.overridden_price +
                          (self.menu_item.overridden_price * self.menu_item.percentage_adjustment) / 100)
        self.assertEqual(self.menu_item.calculated_price, expected_price)

    def test_calculated_price_overridden_price_not_null_and_percentage_adjustment_and_dollar_adjustment(self):
        self.menu_item.overridden_price = 20
        self.menu_item.percentage_adjustment = 10
        self.menu_item.dollar_adjustment = 10
        expected_price = (self.menu_item.overridden_price +
                          (self.menu_item.overridden_price * self.menu_item.percentage_adjustment) / 100 +
                          self.menu_item.dollar_adjustment)
        self.assertEqual(self.menu_item.calculated_price, expected_price)
