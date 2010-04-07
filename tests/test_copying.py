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

class TestCopying(unittest.TestCase):

    ############################################################
    # Copying the tree

    def testCopying_01(self):
        p1 = TreeDict('root')
        p1.a = 123

        p2 = copy(p1)

        self.assert_(p1 == p2)
        self.assert_(p1.hash() == p2.hash())
        
    def testCopying_01d(self):
        p1 = TreeDict('root')
        p1.a = 123

        p2 = deepcopy(p1)

        self.assert_(p1 == p2)
        self.assert_(p1.hash() == p2.hash())

    def testCopying_02_dangling(self):
        p1 = TreeDict('root')
        p1.a

        p2 = copy(p1)

        self.assert_(p1 == p2)
        self.assert_(p1.hash() == p2.hash())

    def testCopying_02d_dangling(self):
        p1 = TreeDict('root')
        p1.a

        p2 = deepcopy(p1)

        self.assert_(p1 == p2)
        self.assert_(p1.hash() == p2.hash())

    def testCopying_03_Dangling_AttributeError(self):
        
        p = TreeDict()

        def f():
            p.a.b.copy()

        self.assertRaises(AttributeError, f)

    def testCopying_04_dangling_AttributeError_correct_node(self):
        
        p = TreeDict()
        ae_msg = ''

        try:
            p.aduvulksjucmfiddkjdo.b.copy()
        except AttributeError, ae:
            ae_msg = str(ae)

        # Make sure it propegates up so the error message is sent from
        # the root dangling node.
        self.assert_('aduvulksjucmfiddkjdo' in ae_msg)


    def testCopying_05(self):
        
        p = TreeDict('root')
        b = p.makeBranch('b').copy()

        self.assert_(p.b.branchName() == 'b', p.b.branchName())
        self.assert_(b.branchName(add_tree_name = True) == 'b', b.branchName(add_tree_name = True))
        self.assert_(p.b.branchName(add_path = True, add_tree_name = True) == 'root.b',
                     p.b.branchName(add_path = True, add_tree_name = True))

    def testCopying_05b(self):
        
        p = TreeDict('root')
        b = copy(p.makeBranch('b'))

        self.assert_(p.b.branchName() == 'b', p.b.branchName())
        self.assert_(b.branchName(add_tree_name = True) == 'b', b.branchName(add_tree_name = True))
        self.assert_(p.b.branchName(add_path = True, add_tree_name = True) == 'root.b',
                     p.b.branchName(add_path = True, add_tree_name = True))

    def testCopying_05c(self):
        
        p = TreeDict('root')
        b = deepcopy(p.makeBranch('b'))

        self.assert_(p.b.branchName() == 'b', p.b.branchName())
        self.assert_(b.branchName(add_tree_name = True) == 'b', b.branchName(add_tree_name = True))
        self.assert_(p.b.branchName(add_path = True, add_tree_name = True) == 'root.b',
                     p.b.branchName(add_path = True, add_tree_name = True))

    def testCopying_05b_central_system(self):
        # This test constrains the central system to have the same
        # name system as regular trees (I was tempted to do it
        # otherwise to make the constraints of copied branches
        # easier.)

        p = getTree('tc_root')
        b = p.makeBranch('b').copy()
    
        self.assert_(b.branchName(add_tree_name = True) == 'b', b.branchName(add_tree_name = True))
        self.assert_(p.b.branchName(add_path = True, add_tree_name = True) == 'tc_root.b',
                     p.b.branchName(add_path = True, add_tree_name = True))

    def testCopying_05b_central_system(self):
        # This test constrains the central system to have the same
        # name system as regular trees (I was tempted to do it
        # otherwise to make the constraints of copied branches
        # easier.)

        p = getTree('tc_root')
        b = p.makeBranch('b').copy()
    
        self.assert_(b.branchName(add_tree_name = True) == 'b', b.branchName(add_tree_name = True))
        self.assert_(p.b.branchName(add_path = True, add_tree_name = True) == 'tc_root.b',
                     p.b.branchName(add_path = True, add_tree_name = True))

    def testCopying_05b_central_system(self):
        # This test constrains the central system to have the same
        # name system as regular trees (I was tempted to do it
        # otherwise to make the constraints of copied branches
        # easier.)

        p = getTree('tc_root')
        b = p.makeBranch('b').copy()
    
        self.assert_(b.branchName(add_tree_name = True) == 'b', b.branchName(add_tree_name = True))
        self.assert_(p.b.branchName(add_path = True, add_tree_name = True) == 'tc_root.b',
                     p.b.branchName(add_path = True, add_tree_name = True))

    def testCopying_06_setting_linked_branch_02_copy(self):
        p = TreeDict()

        p.a = p.defs.a1

        p.defs.a1.v = 1

        p2 = p.copy()

        p2.defs.a1.v = 2

        self.assert_(p.a.v == 1)
        self.assert_(p2.a.v == 2)

    def testCopying_06_setting_linked_branch_04_deepcopy_func(self):
        p = TreeDict()

        p.a = p.defs.a1

        p.defs.a1.v = 1

        p2 = deepcopy(p)  # only difference from above

        p2.defs.a1.v = 2

        self.assert_(p.a.v == 1)
        self.assert_(p2.a.v == 2)

    def testCopying_07_unfrozen(self):
        p = TreeDict()

        p.x = 1
        p.b.c.x = 2
        p.b.c.y = 1

        p.freeze()

        self.assert_(p.isFrozen())
        self.assert_(p.b.isFrozen())
        self.assert_(p.b.c.isFrozen())

        p2 = p.copy()

        self.assert_(not p2.isFrozen())
        self.assert_(not p2.b.isFrozen())
        self.assert_(not p2.b.c.isFrozen())
        
        p3 = copy(p)
        
        self.assert_(not p3.isFrozen())
        self.assert_(not p3.b.isFrozen())
        self.assert_(not p3.b.c.isFrozen())


    def testImport_01(self):

        p = TreeDict()

        p.a.b = 1
        p.a.c = 2
        p.b   = [1,2,3]

        p2 = TreeDict()
        p2.importFrom(p)

        self.assert_(p.a.b is p2.a.b)
        self.assert_(p.a.c is p2.a.c)
        self.assert_(p.b is p2.b)

        self.assert_(p == p2)

    def testImport_02_deepcopy(self):

        p = TreeDict()

        p.a.b = 1
        p.a.c = 2
        p.b   = [1,2,3]

        p2 = TreeDict()
        p2.importFrom(p, copy_deep = True)

        self.assert_(p.a.b == p2.a.b)
        self.assert_(p.a.c == p2.a.c)
        self.assert_(p.b == p2.b)
        self.assert_(p.b is not p2.b)

        self.assert_(p == p2)

    def testImport_03_local_values_preserved(self):

        p = TreeDict()

        p.a.b = 1
        p.a.c = 2
        p.b   = [1,2,3]

        p2 = TreeDict()
        p2.c  = [1,2]
        p2.importFrom(p)

        self.assert_(p.a.b is p2.a.b)
        self.assert_(p.a.c is p2.a.c)
        self.assert_(p.b is p2.b)
        self.assert_(p2.c == [1,2])

        self.assert_(p != p2)

    def testImport_04_keep_local(self):

        p = TreeDict()

        p.a.b = 1
        p.a.c = 2
        p.b   = [1,2,3]

        p2 = TreeDict()
        p2.b  = [1,2]
        p2.importFrom(p, overwrite_existing = False)

        self.assert_(p.a.b == p2.a.b)
        self.assert_(p.a.c == p2.a.c)
        self.assert_(p.b == [1,2,3])
        self.assert_(p2.b == [1,2])

        self.assert_(p != p2)
        

    def testImport_05_keep_local__local_values_preserved(self):

        p = TreeDict()

        p.a.b = 1
        p.a.c = 2
        p.b   = [1,2,3]

        p2 = TreeDict()
        p2.b  = [1,2]
        p2.c  = [1]
        p2.importFrom(p, overwrite_existing = False)

        self.assert_(p.a.b == p2.a.b)
        self.assert_(p.a.c == p2.a.c)
        self.assert_(p.b == [1,2,3])
        self.assert_(p2.b == [1,2])
        self.assert_(p2.c == [1])

        self.assert_(p != p2)

    # Also need tests covering cases where flags are cleared on copied
    # nodes

    # Also need to add tests for copying with links and that the
    # proper link-parental relations are preserved in copying.

if __name__ == '__main__':
    unittest.main()

