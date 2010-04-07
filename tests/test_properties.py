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

class TestProperties(unittest.TestCase):

    def testIsDangling_01(self):
        p1 = TreeDict()
        p1.a

        self.assert_(p1.a.isDangling())

    def testIsDangling_02(self):
        p1 = TreeDict()
        p1.a.b

        self.assert_(p1.a.isDangling())
        
    def testIsDangling_03(self):
        p1 = TreeDict()
        p1.a.b = 1

        self.assert_(not p1.a.isDangling())

    def testIsDangling_04(self):
        p1 = sample_tree()
        p1.a

        self.assert_(p1.a.isDangling())

    def testIsDangling_05(self):
        p1 = sample_tree()
        p1.a.b

        self.assert_(p1.a.isDangling())

    def testIsDangling_05b(self):
        p1 = sample_tree()
        p1.a
        p1.a.b

        self.assert_(p1.a.isDangling())
        
    def testIsDangling_06(self):
        p1 = sample_tree()
        p1.a.b = 1

        self.assert_(not p1.a.isDangling())

    def testisEmpty_01(self):
        p = TreeDict('emptytest')
        self.assert_(p.isEmpty())

    def testisEmpty_02(self):
        p = TreeDict('emptytest')
        p.a.b = 2
        self.assert_(not p.isEmpty())
        self.assert_(not p.a.isEmpty())
        
    def testisEmpty_03_key_deletion(self):
        p = TreeDict('emptytest')
        p.a = 2
        del p.a
        self.assert_(p.isEmpty())

    def testisEmpty_04_dangling_nodes(self):
        p = TreeDict()
        p.a
        self.assert_(p.isEmpty())


    def testMutability_01(self):
        p1 = TreeDict('root')

        p1.a = (13, (123, 32))
        p1.b = 123
        p1.c.a = 145
        p1.c.b = "1231321321231321"

        self.assert_(p1.isMutable())

        p1.freeze()

        self.assert_(not p1.isMutable())

        
    def testMutability_02(self):
        p1 = TreeDict('root')

        p1.a = (13, (123, 32))
        p1.b = 123
        p1.c.a = 145
        p1.c.b = "1231321321231321"
        p1.c.c = {}

        self.assert_(p1.isMutable())

        p1.freeze()

        self.assert_(p1.isMutable())
        
    def testMutability_03(self):
        # Makes sure that stored branches are handled correctly
        
        p1 = TreeDict('root')
        
        p1.a = (13, (123, 32))
        p1.b = 123
        p1.c.a = 145
        p1.c.b = "1231321321231321"
        
        p2 = TreeDict('node')

        p2.a = 432

        p1.node = p2

        self.assert_(p1.isMutable())

        p1.freeze()
        
        self.assert_(p1.isMutable())

        p2.freeze()
        
        self.assert_(not p1.isMutable())
        
    def testFreezingValues_01(self):
        p1 = TreeDict('root')
        
        p1.a = (13, (123, 32))
        p1.b = 123
        p1.c.a = 145
        p1.c.b = "1231321321231321"
      
        p1.freeze("a")
        self.assertRaises(TypeError, lambda: p1.freeze("b", quiet=False))
        p1.freeze("b", quiet=True)

        p1.freeze("c", quiet=False)

        self.assert_(p1.c.isFrozen())

    ################################################################################
    # Sizing

    def testSize_01_empty(self):
        p = TreeDict()

        print p.makeReport()
        
        self.assert_(len(p) == 0, len(p))
        self.assert_(p.size() == 0, p.size())
        self.assert_(p.size(recursive = False) == 0)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 0)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 0)
        
    def testSize_02_dangling(self):
        p = TreeDict()
        p.a
        self.assert_(len(p) == 0)
        self.assert_(p.size() == 0)
        self.assert_(p.size(recursive = False) == 0)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 0)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 0)
        

    def testSize_03_dangling(self):
        p = TreeDict()

        p.makeBranch("a")
        p.a.b

        self.assert_(len(p) == 0)
        self.assert_(p.size() == 0)
        self.assert_(p.size(recursive = False) == 0)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 1)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 1)

    def testSize_03b_dangling(self):
        p = TreeDict()
        p.a.b
        self.assert_(len(p) == 0)
        self.assert_(p.size() == 0)
        self.assert_(p.size(recursive = False) == 0)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 0)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 0)
    
    def testSize_04_dangling(self):
        p = TreeDict()
        p.a.v = 1
        p.a.b
        self.assert_(len(p) == 1)
        self.assert_(p.size() == 1)
        self.assert_(p.size(recursive = False) == 0)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 1)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 1)

    def testSize_05_dangling(self):
        p = TreeDict()
        p.a.b.c.d.e
        p.a.b.c = 1

        self.assert_(len(p) == 1)
        self.assert_(p.size() == 1)
        self.assert_(p.size(recursive = False) == 0)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 1)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 1)

    def testSize_06(self):
        p = TreeDict()

        p.a = 1
        p.b.c = 2
        p.b.d = 3

        self.assert_(len(p) == 3)
        self.assert_(p.size() == 3)
        self.assert_(p.size(recursive = False) == 1)
        self.assert_(p.size(recursive = False, branch_mode = "all") == 2)
        self.assert_(p.size(recursive = False, branch_mode = "only") == 1)

    def testSize_07_large_recursive(self):
        n = 500

        p = TreeDict()
        kl = random_node_list(0, n, 0.75)

        for i, k in enumerate(kl):
            p.set(k, i)

        n_root_leaves = len([k for k in kl if '.' not in k])

        self.assert_(len(p) == n)
        self.assert_(p.size() == n)
        self.assert_(p.size(recursive = False) == n_root_leaves)
        self.assert_(p.size(recursive = False, branch_mode = "all") == n)
        self.assert_(p.size(recursive = False, branch_mode = "only") == n - n_root_leaves)

    def _checkAllSize(self, p, test, rid):
        self.assert_(p.size(*test) == len(rid[test]))

    def testSize_08_basic_walking_test__rn(self):

        p, rid = basic_walking_test()
        test = (True, "none")
        self._checkAllSize(p, test, rid)

    def testSize_08_basic_walking_test__ra(self):

        p, rid = basic_walking_test()
        test = (True, "all")
        self._checkAllSize(p, test, rid)

    def testSize_08_basic_walking_test__ro(self):

        p, rid = basic_walking_test()
        test = (True, "only")
        self._checkAllSize(p, test, rid)

    def testSize_08_basic_walking_test__fn(self):

        p, rid = basic_walking_test()
        test = (False, "none")
        self._checkAllSize(p, test, rid)

    def testSize_08_basic_walking_test__fa(self):

        p, rid = basic_walking_test()
        test = (False, "all")
        self._checkAllSize(p, test, rid)

    def testSize_08_basic_walking_test__fo(self):

        p, rid = basic_walking_test()
        test = (False, "only")
        self._checkAllSize(p, test, rid)

if __name__ == '__main__':
    unittest.main()

