# -*- coding: utf-8 -*-

'''
   Created on Jun 12, 2015
   @author: s1m0n4
   @copyright: 2015 s1m0n4 for hookii.it
'''

import time
import os
import sys
libs = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(libs)


def datetimestr_to_timestamp(dtstr):
    dtstruct = None
    try:
        dtstruct = time.strptime(dtstr, "%Y-%m-%d %H:%M:%S")
        return time.mktime(dtstruct)
    except Exception:
        return 0