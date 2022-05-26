import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.getcwd(), '..'))
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from client import create_presence, process_answer


class TestClass(unittest.TestCase):
    def test_def_presence(self):
        test = create_presence()
        test[TIME] = 1.1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_200_answer(self):
        self.assertEqual(process_answer({RESPONSE: 200}), '200 : OK')

    def test_400_answer(self):
        self.assertEqual(process_answer({RESPONSE: 400, ERROR: 'Bad Request'}), '400: Bad Request')

    def test_no_response(self):
        self.assertRaises(ValueError, process_answer, {ERROR: 'Bad Request'})

    def test_create_presence_with_account_name(self):
        self.assertEqual(create_presence('Roman')[USER][ACCOUNT_NAME], 'Roman')


if __name__ == '__main__':
    unittest.main()
