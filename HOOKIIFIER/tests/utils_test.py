#!/bin/env python

'''
   Created on Jun 12, 2015
   @author: s1m0n4
   @copyright: 2015 s1m0n4 for hookii.it
'''

import unittest 
import os
import sys
libs = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'))
sys.path.append(libs)
from utils import datetimestr_to_timestamp

class Utils(unittest.TestCase):

    def test_datetimestr_to_timestamp_none_arg(self):
        res = datetimestr_to_timestamp(None)
        self.assertEqual(res, 0)

    def test_datetimestr_to_timestamp_invalid_arg(self):
        res = datetimestr_to_timestamp("bla")
        self.assertEqual(res, 0)


if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(Utils)
#     unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()