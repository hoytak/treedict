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


class TestBadValues(unittest.TestCase):
    def test_KeyNotEmpty(self):
        p = sample_tree()
        self.assertRaises(NameError, lambda: p.set("", 0))

    def test_KeyNotEmpty(self):
        p = sample_tree()
        self.assertRaises(NameError, lambda: p.set("", 0))

    def test_KeyAttributeName(self):
        p = sample_tree()
        self.assertRaises(NameError, lambda: p.set("0393", 0))

    def test_GetBadName_01(self):
        p = sample_tree()
        self.assert_(KeyError, lambda: p.get("0393"))

    def test_GetBadName_02(self):
        p = sample_tree()
        self.assert_(KeyError, lambda: p.get("0393.a.b.c"))

    def test_GetBadName_03(self):
        p = sample_tree()
        self.assert_(KeyError, lambda: p.get("0393.a.b.c"))

    def test_getattr_BadName_01(self):  # ??????
        p = sample_tree()
        self.assert_(KeyError, lambda: p.a_nonexistant)


    def testAttackWithNone_prune(self):
        p = TreeDict()
        self.assertRaises(TypeError, lambda: p.prune(None))

    def testAttackWithNone_attach(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.attach(None))

    def testAttackWithNone_equals(self):
        p = sample_tree()
        self.assert_(p != None)

    def testAttackWithNone_getClosest(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.getClosest(None))

    def testAttackWithNone_branch(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.makeBranch(None))

    def testAttackWithNone_fullNameOf(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.fullNameOf(None))

    def testAttackWithNone_hash(self):
        p = sample_tree()
        self.assertRaises(TypeError, lambda: p.hash(keys=[None]))

    def testBadKey_01_hash(self):
        p = sample_tree()
        self.assertRaises(KeyError, lambda: p.hash(key="keynothere"))

    def testBadKey_02_hash(self):
        p = sample_tree()
        self.assertRaises(KeyError, lambda: p.hash(keys=["keynothere"]))

if __name__ == '__main__':
    unittest.main()

