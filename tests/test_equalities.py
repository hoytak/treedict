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

class TestEqualities(unittest.TestCase):

    def test_Equality(self):
        t1 = sample_tree()
        t2 = sample_tree()
 
        self.assert_(t1 == t2)

    def test_Inequality(self):
        t1 = sample_tree()
        t2 = sample_tree()

        t2.a.b.r.t = 1

        self.assert_(t1 != t2)

    def test_Equalityf(self):
        t1 = frozen_tree()
        t2 = frozen_tree()

        self.assert_(t1 == t2)

    def test_Equalityf2(self):
        t1 = sample_tree()
        t2 = sample_tree()

        t2.freeze()

        self.assert_(t1 == t2)
        

    def test_Equalityf3(self):
        t1 = sample_tree()
        t2 = sample_tree()

        t1.a.b.c.d = 3212
        t2.freeze()
        
        self.assert_(t1 != t2)

    def test_EqualitySubtree(self):
        t1 = TreeDict()
        t2 = TreeDict()
        
        t1.a = 1
        t2.a = 2
        t1.b.c.d = 1
        t2.b.c.d = 1

        self.assert_(t1.b == t2.b)
        self.assert_(t1 != t2)

    def testEqualityEmpty(self):
        self.assert_(TreeDict() == TreeDict())
        
    def testEqualityOneEmpty(self):
        p1 = TreeDict()
        p2 = TreeDict()
        p1.a = 1

        self.assert_(p1 != p2)

    def testEqualityWithDanglingNode_01(self):
        p1 = TreeDict()
        p2 = TreeDict()
        p1.a

        self.assert_(p1 == p2)


    def testEqualityWithDanglingNode_02(self):
        p1 = TreeDict()
        p2 = TreeDict()
        p1.a
        p2.a

        self.assert_(p1 == p2)

    def testEqualityWithDanglingNode_03(self):
        p1 = TreeDict()
        p2 = TreeDict()
        p1.a
        p2.b

        self.assert_(p1 == p2)

    def testEqualityWithDanglingNode_04(self):
        p1 = TreeDict()
        p2 = TreeDict()
        p1.a = 1
        p2.a

        self.assert_(p1 != p2)
