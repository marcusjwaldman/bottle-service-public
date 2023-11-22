from enum import Enum


class BottleServiceAccountType(Enum):
    DISTRIBUTOR = 'distributor'
    RESTAURANT = 'restaurant'
    CUSTOMER = 'customer'
    ADMIN = 'admin'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    def equals_string(self, other):
        print(self)
        print(other)
        if self == other:
            return True
        if self.value == other:
            return True
        if self.name == other:
            return True
        if f'{self.__class__.__name__}.{self.name}' == other:
            return True
        return False

    @staticmethod
    def get_enum_from_string(string_to_match):
        for enum in BottleServiceAccountType:
            if enum.equals_string(string_to_match):
                return enum
        return None

    @staticmethod
    def get_name_from_string(string_to_match):
        for enum in BottleServiceAccountType:
            if enum.equals_string(string_to_match):
                return enum.name
        return None
