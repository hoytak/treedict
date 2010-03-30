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

class TestPruning(unittest.TestCase):

    def testpruning_01(self):
        p = TreeDict('prunetest')
        p.a.b.c = 123
        h1 = p.hash()

        self.assert_('a.b.c' in p)
        
        p.pop('a.b.c')

        self.assert_('a.b.c' not in p)

        h2 = p.hash()

        p.a.b.c = 123
        h3 = p.hash()

        self.assert_(h1 != h2)
        self.assert_(h1 == h3)

    def testpruning_02(self):
        p = TreeDict('prunetest')
        p.a.b.c = 123
        h1 = p.hash()

        self.assert_('a.b.c' in p)
        
        p.pop('a.b.c', prune_empty=True)

        self.assert_('a.b' not in p)

        h2 = p.hash()

        p.a.b.c = 123
        h3 = p.hash()

        self.assert_(h1 != h2)
        self.assert_(h1 == h3)

    def testpruning_03(self):
        p = TreeDict('prunetest')
        p.a.b.c = 123
        h1 = p.hash()

        self.assert_('a.b.c' in p)

        del p.a.b.c

        self.assert_('a.b.c' not in p)

        h2 = p.hash()

        p.a.b.c = 123
        h3 = p.hash()

        self.assert_(h1 != h2)
        self.assert_(h1 == h3)

    def testpruning_04(self):
        p1 = sample_tree()
        p1.testnode = 123

        p2 = deepcopy(p1)

        self.assert_(p1 == p2)

        p1.pop("testnode")

        self.assert_(p1 != p2)
        self.assert_('testnode' not in p1)

    def testpruning_05_silent(self):
        p1 = sample_tree()
        p1.testnode = 123

        p2 = deepcopy(p1)

        self.assert_(p1 == p2)

        self.assertRaises(KeyError, lambda: p1.pop("testnode_nonexistent"))
                          
        p1.pop("testnode_nonexistent", silent=True)

        self.assert_(p1 == p2)
        self.assert_('testnode' in p1)

        p1.pop("testnode", silent=True)

        self.assert_(p1 != p2)
        self.assert_('testnode' not in p1)

    def testpruning_06_silent_popitem(self):
        p1 = sample_tree()
        p1.testnode = 123

        p2 = deepcopy(p1)

        self.assert_(p1 == p2)

        self.assertRaises(KeyError, lambda: p1.popitem("testnode_nonexistent"))
                          
        p1.pop("testnode_nonexistent", silent=True)

        self.assert_(p1 == p2)
        self.assert_('testnode' in p1)

        p1.popitem("testnode", silent=True)

        self.assert_(p1 != p2)
        self.assert_('testnode' not in p1)

class TestDeletion(unittest.TestCase):

    def testDeletion_01(self):
        
        p = TreeDict()
        p.a = 1

        self.assert_('a' in p)

        del p['a']

        self.assert_('a' not in p)


    def testDeletion_02(self):
        
        p = TreeDict()
        p.a.b.c = 1

        self.assert_('a.b.c' in p)

        del p['a.b.c']

        self.assert_('a' in p)
        self.assert_('a.b' in p)
        self.assert_('a.b.c' not in p)

    def testDeletion_03_is_detached(self):
        p = TreeDict()
        p.makeBranch("a")
        a = p.a

        del p["a"]

        self.assert_(a.rootNode() is not p)
        self.assert_(a.parentNode() is None)
        
    



if __name__ == '__main__':
    unittest.main()

