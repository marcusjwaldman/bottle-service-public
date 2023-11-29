from django.test import TestCase


from location.tools import GeoLocation
from unittest.mock import patch


class LocationTests(TestCase):

    @patch('location.tools.googlemaps.Client')
    def test_get_distance_time(self, mock_gmaps_client):
        origin_coords = (37.7749, -122.4194)  # San Francisco, CA
        destination_coords = (34.0522, -118.2437)  # Los Angeles, CA

        geoLocation = GeoLocation()
        mock_distance_matrix = mock_gmaps_client.return_value.distance_matrix
        mock_distance_matrix.return_value = {
            'status': 'OK',
            'rows': [
                {
                    'elements': [
                        {'distance': {'value': 1000}, 'duration': {'value': 300}},
                    ]
                }
            ]
        }
        driving_distance, driving_duration = geoLocation.get_distance_time(origin_coords, destination_coords, mode='driving')

        self.assertEqual(driving_distance, 1000)
        self.assertEqual(driving_duration, 300)

    @patch('location.tools.googlemaps.Client')
    def test_generate_from_address(self, mock_gmaps_client):
        address = '1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA'

        geoLocation = GeoLocation()
        mock_geo_matrix = mock_gmaps_client.return_value.geocode
        mock_geo_matrix.return_value = [{'geometry': {'location': {'lat': 37.7749, 'lng': -122.4194}}}]
        lat, lng = geoLocation.generate_from_address(address)

        self.assertEqual(lat, 37.7749)
        self.assertEqual(lng, -122.4194)
