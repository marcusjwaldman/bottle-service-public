from django.test import TestCase
from bottle_service_app.tools import split_string


class ToolsTests(TestCase):

    def test_create_list(self):
        test_string = "a, b, c"
        test_list = ["a", "b", "c"]
        self.assertEqual(split_string(test_string), test_list)


    def test_create_list_single(self):
        test_string = "a"
        test_list = ["a"]
        self.assertEqual(split_string(test_string), test_list)


    def test_create_list_empty(self):
        test_string = ""
        test_list = []
        self.assertEqual(split_string(test_string), test_list)



    def test_create_list_none(self):
        test_string = None
        with self.assertRaises(ValueError):
            split_string(test_string)

