# coding=utf-8
import unittest

from .project import (
    match_pn,
    format_datetime,
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


class FormatDatetime(unittest.TestCase):
    def setUp(self):
        self.success_datetime_01 = "2019-10-10"
        self.success_datetime_02 = "1999-10-01"
        self.error_datetime_01 = "1999-88-55"
        self.error_datetime_02 = "this is a error datetime"

    def test_corresc_datetime(self):
        self.assertTrue(format_datetime(self.success_datetime_01))
        self.assertTrue(format_datetime(self.success_datetime_02))

    def test_error_datetime(self):
        self.assertFalse(format_datetime(self.error_datetime_01))
        self.assertFalse(format_datetime(self.error_datetime_02))


if __name__ == '__main__':
    unittest.main()
