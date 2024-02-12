from django.db import models
from django.db.models import CheckConstraint, Q

from distributor.models import Distributor, LocomotionType
from restaurant.models import Restaurant
from django.core.exceptions import ValidationError

from schedule.models import create_new_weekly_schedule
# from schedule.utils import operation_daily_schedule


class PartnerStatus(models.Choices):
    MATCHED = 'matched'
    PENDING_DISTRIBUTOR_APPROVAL = 'pending_distributor'
    PENDING_RESTAURANT_APPROVAL = 'pending_restaurant'
    APPROVED = 'approved'
    REJECTED_BY_DISTRIBUTOR = 'rejected_by_distributor'
    REJECTED_BY_RESTAURANT = 'rejected_by_restaurant'


class Partners(models.Model):
    id = models.AutoField(primary_key=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=PartnerStatus.choices, default=PartnerStatus.MATCHED)
    locomotion = models.CharField(max_length=20, choices=LocomotionType.choices)
    minutes_distance = models.IntegerField()
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, null=True)
    # operational_schedule = models.ForeignKey('schedule.WeeklySchedule', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('distributor', 'restaurant')
        constraints = [
            CheckConstraint(
                check=Q(minutes_distance__gt=0),
                name='partner_minutes_distance_positive_constraint'
            )
        ]

    @property
    def status_enum(self):
        return PartnerStatus(self.status)

    # def update_operational_schedule(self):
    #     if self.distributor is None or self.restaurant is None:
    #         self.operational_schedule = None
    #     elif self.distributor.weekly_schedule is None or self.restaurant.weekly_schedule is None:
    #         self.operational_schedule = None
    #     else:
    #         self.operational_schedule = create_new_weekly_schedule()
    #         operation_daily_schedule(self.distributor.weekly_schedule.monday, self.restaurant.weekly_schedule.monday,
    #                                  self.operational_schedule.monday)
    #         self.operational_schedule.tuesday = operation_daily_schedule(self.distributor.weekly_schedule.tuesday,
    #                                                                     self.restaurant.weekly_schedule.tuesday)
    #         self.operational_schedule.wednesday = operation_daily_schedule(self.distributor.weekly_schedule.wednesday,
    #                                                                     self.restaurant.weekly_schedule.wednesday)
    #         self.operational_schedule.thursday = operation_daily_schedule(self.distributor.weekly_schedule.thursday,
    #                                                                     self.restaurant.weekly_schedule.thursday)
    #         self.operational_schedule.friday = operation_daily_schedule(self.distributor.weekly_schedule.friday,
    #                                                                     self.restaurant.weekly_schedule.friday)
    #         self.operational_schedule.saturday = operation_daily_schedule(self.distributor.weekly_schedule.saturday,
    #                                                                     self.restaurant.weekly_schedule.saturday)
    #         self.operational_schedule.sunday = operation_daily_schedule(self.distributor.weekly_schedule.sunday,
    #                                                                     self.restaurant.weekly_schedule.sunday)
    #
    #     return self.operational_schedule


class MenuStatus(models.Choices):
    DRAFT = 'draft'
    PENDING_RESTAURANT_APPROVAL = 'pending_restaurant'
    APPROVED = 'approved'
    REJECTED_BY_RESTAURANT = 'rejected_by_restaurant'
    ARCHIVED = 'archived'


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_minutes = models.IntegerField(null=True)
    status = models.CharField(max_length=30, choices=MenuStatus.choices, default=MenuStatus.DRAFT)
    # Future function to allow override distributor's schedule for menu
    # weekly_schedule = models.ForeignKey('WeeklySchedule', on_delete=models.CASCADE, null=True)
    paused = models.BooleanField(default=False)
    menu_items = models.ManyToManyField('MenuItem')

    def clean(self):
        if self.status == MenuStatus.APPROVED:
            # Check if there is another approved menu for the same distributor and restaurant
            existing_approved_menus = Menu.objects.filter(
                distributor=self.distributor,
                restaurant=self.restaurant,
                status=MenuStatus.APPROVED
            ).exclude(id=self.id)

            if existing_approved_menus.exists():
                raise ValidationError("Only one menu for the combination of distributor and restaurant can have the "
                                      "status 'Approved'.")

        super().clean()

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(delivery_minutes__gt=0) | Q(delivery_minutes__isnull=True),
                name='menu_delivery_minutes_positive_constraint'
            )
        ]

    @property
    def status_enum(self):
        return MenuStatus(self.status)


class MenuItemCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent_category = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    out_of_stock = models.BooleanField(default=False)
    distributor_notes = models.TextField(null=True)
    category = models.ForeignKey(MenuItemCategory, on_delete=models.CASCADE, null=True)
    # Future feature
    # photo = models.ImageField(upload_to='menu_items/', null=True, blank=True)

    class Meta:
        unique_together = ('distributor', 'name')
        constraints = [
            CheckConstraint(
                check=Q(price__gt=0),
                name='menu_item_price_positive_constraint'
            )
        ]


class MenuItem(models.Model):
    id = models.AutoField(primary_key=True)
    parent_menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    overridden_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    percentage_adjustment = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    dollar_adjustment = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        unique_together = ('parent_menu', 'item')

    @property
    def calculated_price(self):
        if self.overridden_price:
            price = self.overridden_price
        else:
            price = self.item.price

        if self.percentage_adjustment:
            percentage = self.percentage_adjustment
        else:
            percentage = 0
        if self.dollar_adjustment:
            dollar = self.dollar_adjustment
        else:
            dollar = 0

        calculated_price = price + (price * percentage) / 100 + dollar
        return calculated_price
