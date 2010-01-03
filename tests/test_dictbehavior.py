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

class TestDictBehavior(unittest.TestCase):

    ############################################################
    # Make sure it behaves like a dictionary.

    def testDictBehavior_01(self):
        p = sample_tree()
        v = 14528483
        p.a.b.c = v

        self.assert_(p["a.b.c"] is v)
        self.assert_(p.a["b.c"] is v)
        self.assert_(p.a.b["c"] is v)
        self.assert_(p["a"].b.c is v)
        self.assert_(p.a["b"]["c"] is v)
        self.assert_(p.get("a").b["c"] is v)

    def testDictBehavior_02(self):
        
        p = TreeDict()
        p.a = 123

        self.assert_( ("%(a)d" % p) == "123")

    def testDictBehavior_03(self):
        
        p = TreeDict()
        p.a.b.c = 123

        self.assert_( ("%(a.b.c)d" % p) == "123")

    def testDictBehavior_04(self):
        p = TreeDict()
        v = ("borkborkbork", 123)
        p["a"] = v

        self.assert_(p.a is v)

    def testDictBehavior_05(self):
        p = TreeDict()
        v = ("borkborkbork", 123)
        p["a.b.c"] = v

        self.assert_(p.a.b.c is v)

    def testDictBehavior_06_clear_01(self):
        p = TreeDict()

        p["a"] = 1
        
        self.assert_("a" in p)
        
        p.clear()
        
        self.assert_("a" not in p)
        self.assert_(len(p) == 0)

    def testDictBehavior_06_clear_02(self):
        p = sample_tree()
        p.clear()
        self.assert_(len(p) == 0)

    def testDictBehavior_07_FromKeys_01(self):
        p = TreeDict()
        d = {}

        key_iterable = ["alphabet"]

        self.assert_(p.fromkeys(key_iterable) == d.fromkeys(key_iterable))
        
    def testDictBehavior_07_FromKeys_02(self):
        p = TreeDict()
        d = {}
        v = ["asdfadsf"]

        key_iterable = ["alph", "bork"]
        
        self.assert_(p.fromkeys(key_iterable, v) == d.fromkeys(key_iterable, v))

    def testDictBehavior_08_equality_tests(self):
        p = TreeDict()

        p.v = 1
        p.a.b.c = 2
    
        self.assert_(p == {'v' : 1, "a.b.c" : 2})
        self.assert_(p != {'v' : 2, "a.b.c" : 2})
        self.assert_(p != {'v' : 1, "a.b.c" : None})


    def testDictBehavior_09_setdefault_01(self):

        p = sample_tree()
        
        d = dict(p.iteritems())
        
        self.assert_(p == d)

        p.setdefault('a')
        d.setdefault('a')

        self.assert_(p == d)
        
    def testDictBehavior_09_setdefault_02(self):

        p = sample_tree()
        
        d = dict(p.iteritems())
        
        self.assert_(p == d)

        p.setdefault('a', [123])
        d.setdefault('a', [123])

        self.assert_(p == d)

    def testDictBehavior_09_setdefault_03(self):

        p = TreeDict()
        p.a.aa.aaa.b = 123
        p.a.aa.aaa.c = 1324
        
        d = dict(p.iteritems())
        
        self.assert_(p == d)

        p.setdefault('a.aa.aaa.b', 1)
        d.setdefault('a.aa.aaa.b', 1)

        self.assert_(p == d)

    def testDictBehavior_09_setdefault_04(self):

        p = TreeDict()
        p.a = 123
        
        d = dict(p.iteritems())
        
        self.assert_(p == d)

        p.setdefault('a')
        d.setdefault('a')

        self.assert_(p == d)

    def testDictBehavior_09_setdefault_05(self):

        p = TreeDict()
        p.a = 123
        
        d = dict(p.iteritems())
        
        self.assert_(p == d)

        p.setdefault('a', 1)
        d.setdefault('a', 1)

        self.assert_(p == d)

    def testDictBehavior_10_straight_iteration(self):
        p = TreeDict()

        d = {'a.b.x' : 1, 'b.x' : 2, 'd.b.c' : 3}

        p.update(d)

        s1 = set([v for v in d])
        s2 = set([v for v in p])

        self.assert_(s1 == s2, (s1, s2))

if __name__ == '__main__':
    unittest.main()

