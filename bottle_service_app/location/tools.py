class GeoLocation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return str([self.latitude, self.longitude])

    @staticmethod
    def generate_from_address(address):
        return GeoLocation(0, 0)
