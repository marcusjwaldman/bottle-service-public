import googlemaps
from django.conf import settings


class GeoLocation:

    modes = {
        'driving': 'driving',
        'walking': 'walking',
        'bicycling': 'bicycling',
    }

    def __init__(self):
        self.gmaps = googlemaps.Client(key=settings.MAP_API_KEY)

    def generate_from_address(self, address):
        geocode_result = self.gmaps.geocode(address)

        # Extract latitude and longitude from the result
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            latitude = location['lat']
            longitude = location['lng']
        else:
            raise Exception('Invalid address')
        return latitude, longitude

    def get_distance_time(self, origin, destination, mode='driving'):

        try:
            response = self.gmaps.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=mode,
            )

            if response['status'] == 'OK':
                element = response['rows'][0]['elements'][0]
                distance_meters = element['distance']['value']
                duration_seconds = element['duration']['value']
                return distance_meters, duration_seconds
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None
