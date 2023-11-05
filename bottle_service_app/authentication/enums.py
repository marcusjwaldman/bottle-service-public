from enum import Enum


class BottleServiceAccountType(Enum):
    DISTRIBUTOR = 'distributor'
    RESTAURANT = 'restaurant'
    CUSTOMER = 'customer'
    ADMIN = 'admin'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]