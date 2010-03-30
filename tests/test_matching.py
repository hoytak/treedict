#!/usr/bin/env python

# Copyright (c) 2009, Hoyt Koepke (hoytak@gmail.com)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     - Neither the name 'treedict' nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY Hoyt Koepke ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Hoyt Koepke BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import random, unittest, cPickle, collections
from treedict import TreeDict, getTree
import treedict
from copy import deepcopy, copy

from hashlib import md5
import random

from common import *

from treedict.treedict import _ldist as ldist

class TestMatching(unittest.TestCase):

    ################################################################################
    # Test match

    def testMatch_01(self):
        p = TreeDict()
        p.a = 1
        self.assert_(p.getClosestKey('a') == 'a')
        self.assert_(p.getClosestKey('a', 1) == ['a'])

    def testMatch_02(self):
        p = TreeDict()
        p.aa = 1
        p.bb = 1
        self.assert_(p.getClosestKey('a') == 'aa')
        self.assert_(p.getClosestKey('a',1) == ['aa'])
        
    def testMatch_03(self):
        p = TreeDict()
        p.set(a=1, b=1, c=1, d=1,e=1,f=1)
        self.assert_(p.getClosestKey('cc') == 'c')
        self.assert_(p.getClosestKey('cc', 1) == ['c'])

    def testMatch_04(self):
        p = TreeDict()
        p.a.b = 1
        p.a.a.b = 1
        p.a.a.a.c = 1
        self.assert_(p.getClosestKey('a') == 'a.b')
        self.assert_(p.getClosestKey('a', 1) == ['a.b'])

    def testMatch_05(self):
        p = TreeDict()
        p.a.b = 1
        p.a.a.b = 1
        p.a.a.a.c = 1
        self.assert_(p.getClosestKey('a.a.b') == 'a.a.b')
        self.assert_(p.getClosestKey('a.a.b',1) == ['a.a.b'])

    def testMatch_06(self):
        p = TreeDict()
        p.a.b = 1
        p.a.a.b = 1
        p.a.a.a.c = 1
        self.assert_(p.getClosestKey('a.ab') == 'a.a.b')
        self.assert_(p.getClosestKey('a.ab',1) == ['a.a.b'])

    def testMatch_07(self):
        p = TreeDict()
        p.a.b = 1
        p.a.a.b = 1
        p.a.a.a.c = 1
        self.assert_(p.getClosestKey('', 2) == ['a.b', 'a.a.b'])

    def testMatch_08(self):
        p = TreeDict()
        p.ab = 1
        p.a.b = 1
        p.a.ab = 1
        p.a.a.b = 1
        p.a.a.bc = 1
        p.a.a.a.c = 1

        self.assert_(p.getClosestKey('', 4) == ['ab', 'a.b', 'a.ab', 'a.a.b'])

    def testMatch_09(self):
        p = TreeDict()
        p.set(gambol = 2, bumble = 3)
        self.assert_(p.getClosestKey('gumbo') == 'gambol')
        self.assert_(p.getClosestKey('gumbo', 1) == ['gambol'])

    def testMatch_10(self):
        p = TreeDict()
        p.set(gambol = 2, bumble = 3, borkborkbork=None)
        self.assert_(p.getClosestKey('gumbo', 2) == ['gambol', 'bumble'])

    def testMatch_11(self):
        p = TreeDict()
        p.a.b = 1
        p.a.a.b = 1
        p.a.a.a.c = 1
        self.assert_(p.getClosestKey('', 200000) == ['a.b', 'a.a.b', 'a.a.a.c'])

    def testMatch_12_empty(self):
        p = TreeDict()
        self.assert_(p.getClosestKey('123221321321') is None)
        self.assert_(p.getClosestKey('123221321321', 1) == [])
        self.assert_(p.getClosestKey('123221321321', 10000) == [])

    def testMatch_13_empty(self):
        p = TreeDict()
        self.assert_(p.getClosestKey('') is None)
        self.assert_(p.getClosestKey('', 1) == [])
        self.assert_(p.getClosestKey('', 10000) == [])

    def testMatch_14_first(self):
        p = TreeDict()
        p.asdfdjdjd.eiudkdkdk = 1
        p.basdfdjdjd = 1
        
        self.assert_(p.getClosestKey('asdfdjdjd') == 'asdfdjdjd.eiudkdkdk')

    def testMatch_15_last(self):
        p = TreeDict()
        p.asdfdjdjd.eiudkdkdk = 1
        p.basdfdjdjd.eiudkddk = 1
        
        self.assert_(p.getClosestKey('asdfjd.eiudkdkdk') == 'asdfdjdjd.eiudkdkdk')

    def testMatch_16_first(self):
        p = TreeDict()
        p.asdfdjdjd.eiudkdkdk = 1
        p.basdfdjdjd.eiudkddk = 1
        p.a.b = None
        
        self.assert_(p.getClosestKey('asdfdjdjd', 2) == 
                     ['asdfdjdjd.eiudkdkdk', 'basdfdjdjd.eiudkddk'], p.getClosestKey('asdfdjdjd', 2))

    def testMatch_17_last(self):
        p = TreeDict()
        p.asdfdjdjd.eiudkdkdk = 1
        p.basdfdjdjd.eiudkddk = 1
        p.a.b = None
        
        self.assert_(p.getClosestKey('asdfjd.eiudkdkdk', 2) == 
                     ['asdfdjdjd.eiudkdkdk', 'basdfdjdjd.eiudkddk'])



class TestLevensteinDist(unittest.TestCase):
    def _test(self, s1, s2, v):
        d = ldist(s1,s2)
        msg = "dist(%s, %s) = %d, should be %d" % (s1, s2, d, v)
        self.assert_(d == v, msg)

    def test01(self): self._test("adresse", "address", 2)
    def test02(self): self._test("adresse", "addressee", 2)
    def test03(self): self._test("gambol", "gumbo", 2)
    def test04(self): self._test("gumbo", "gambol", 2)
    def test05(self): self._test("gumbo", "bumble", 3)
    def test06(self): self._test("qwertyuiop", "qwertyuiop", 0)
    def test07(self): self._test("qwertyuiopasdf", "qwertyuiopasdf", 0)
    def test08(self): self._test("", "", 0)
    def test09(self): self._test("1", "1", 0)
    def test10(self): self._test("1", "2", 1)
    def test11(self): self._test("adress", "address", 1)
    def test12(self): self._test("addresse", "address", 1)
    def test13(self): self._test("gambo", "gumbo", 1)
    def test14(self): self._test("ssss", "ssssssss", 4)
    def test15(self): self._test("ssssssss", "ssss", 4)


if __name__ == '__main__':
    unittest.main()

