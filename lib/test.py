# coding=utf-8
import unittest

from .project import (
    get_number_input,
    user_input,
    match_pn,
    change_point_func,
    get_request,
)


class MatchPnTest(unittest.TestCase):
    def setUp(self):
        self.success_pn_01 = "18201237029"
        self.success_pn_02 = "13555555555"
        self.error_pn_01 = "1234"
        self.error_pn_02 = "this is a error pn"

    def test_correct_pn(self):
        self.assertTrue(match_pn(self.success_pn_01))
        self.assertTrue(match_pn(self.success_pn_02))

    def test_error_pn(self):
        self.assertFalse(match_pn(self.error_pn_01))
        self.assertFalse(match_pn(self.error_pn_02))


if __name__ == '__main__':
    unittest.main()
