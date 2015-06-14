#!/bin/env python
# -*- coding: utf-8 -*-
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
from utils import *

class Utils(unittest.TestCase):

    def test_datetimestr_to_timestamp_none_arg(self):
        res = datetimestr_to_timestamp(None)
        self.assertEqual(res, 0)

    def test_datetimestr_to_timestamp_invalid_arg(self):
        res = datetimestr_to_timestamp("bla")
        self.assertEqual(res, 0)
        
    def test_datetimestr_to_timestamp_ok(self):
        res = datetimestr_to_timestamp("2015-06-12 23:08:00")
        expected = 1434143280
        self.assertEqual(res, expected)
    
    def test_normalized_nickname_none(self):
        res = normalized_nickname(None)
        self.assertIsNone(res)
    
    def test_normalized_nickname_empty(self):
        res = normalized_nickname("     ")
        self.assertIsNone(res)
    
    def test_normalized_nickname_nonasciichars(self):
        res = normalized_nickname("Erni ♖")
        self.assertEqual(res, "Erni♖_")
        #print "Erni ♖ normalized nickname is: %s" % res
    
    def test_read_file_none(self):
        self.assertIsNone(read_file(None))
        
    def test_read_non_existing_file(self):
        self.assertIsNone(read_file("bla"))
    
    def test_read_file_ok(self):
        expected = "Can you read it?"
        fpath = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', "test.txt"))
        self.assertEqual(read_file(fpath), expected)

if __name__ == "__main__":
#     suite = unittest.TestLoader().loadTestsFromTestCase(Utils)
#     unittest.TextTestRunner(verbosity=2).run(suite)
    unittest.main()