#!/usr/bin/env python

# Copyright (c) 2009-2011, Hoyt Koepke (hoytak@gmail.com)
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
from itertools import chain

from hashlib import md5
import random

from common import *

class TestUpdate(unittest.TestCase):

    def checkUpdate(self, base_tree, update_tree, deep_copy,
                    check_function, overwrite, protect_structure):

        # checks it to make sure dict, iterkeys, and treedict all have the same behavior.

        p1 = base_tree.copy(deep = deep_copy)
        p2 = base_tree.copy(deep = deep_copy)
        p3 = base_tree.copy(deep = deep_copy)

        p1.update(update_tree.iteritems(), overwrite, protect_structure)
        check_function(p1)

        p2.update(dict(update_tree.iteritems()), overwrite, protect_structure)
        check_function(p2)

        prev_update_tree = update_tree.copy()

        p3.update(update_tree, overwrite, protect_structure)
        check_function(p3)

        self.assert_(prev_update_tree == update_tree)

    def checkUpdateBadStructure(self, base_tree, update_tree):

        # checks it to make sure dict, iterkeys, and treedict all have the same behavior.

        p1 = base_tree.copy()
        p2 = base_tree.copy()
        p3 = base_tree.copy()

        self.assertRaises(TypeError, lambda: p1.update(update_tree.iteritems(), True, True))
        self.assert_(p1 == base_tree)

        self.assertRaises(TypeError, lambda: p2.update(dict(update_tree.iteritems()), True, True))
        self.assert_(p2 == base_tree)

        prev_update_tree = update_tree.copy()

        self.assertRaises(TypeError, lambda: p3.update(update_tree, True, True))
        self.assert_(p3 == base_tree)

        self.assert_(prev_update_tree == update_tree)


    def testUpdate_01_basic_01(self):
        p = TreeDict(x = 1, y = 2)
        q = TreeDict(y = 3, z = 4)

        def check(r):
            self.assert_(r == TreeDict(x = 1, y = 3, z = 4))

        # This should be the same between these options
        self.checkUpdate(p, q, True, check, overwrite = True, protect_structure = False)
        self.checkUpdate(p, q, True, check, overwrite = True, protect_structure = True)

    def testUpdate_01_basic_02_no_overwrite(self):
        p = TreeDict(x = 1, y = 2)
        q = TreeDict(y = 3, z = 4)

        def check(r):
            self.assert_(r.y == 2)
            self.assert_(r == TreeDict(x = 1, y = 2, z = 4))

        self.checkUpdate(p, q, False, check, overwrite = False, protect_structure = False)
        self.checkUpdate(p, q, False, check, overwrite = False, protect_structure = True)

    def testUpdate_02_branches_01(self):

        p = TreeDict()
        p.a.x = 1
        p.a.y = 2

        q = TreeDict()
        q.a.y = 3
        q.a.z = 4

        def check(r):
            self.assert_(r.a.x == 1)
            self.assert_(r.a.y == 3)
            self.assert_(r.a.z == 4)

        self.checkUpdate(p, q, True, check, overwrite = True, protect_structure = False)
        self.checkUpdate(p, q, True, check, overwrite = True, protect_structure = True)

    def testUpdate_02_branches_02_no_overwrite(self):

        p = TreeDict()
        p.a.x = 1
        p.a.y = 2

        q = TreeDict()
        q.a.y = 3
        q.a.z = 4

        def check(r):
            self.assert_(r.a.x == 1)
            self.assert_(r.a.y == 2)
            self.assert_(r.a.z == 4)

        self.checkUpdate(p, q, True, check, overwrite = False, protect_structure = False)
        self.checkUpdate(p, q, True, check, overwrite = False, protect_structure = True)

    def testUpdate_03_StructurePreserving_01(self):

        p = TreeDict()
        p.a.x = 1
        p.a.y = 2

        q = TreeDict()
        q.a = 3

        def check(r):
            self.assert_(r == TreeDict(a = 3))

        self.checkUpdate(p, q, True, check, overwrite = True, protect_structure = False)

    def testUpdate_03_StructurePreserving_02_noOverwrite(self):

        p = TreeDict()
        p.a.x = 1
        p.a.y = 2

        ct = p.copy()

        q = TreeDict()
        q.a = 3

        def check(r):
            self.assert_(r == ct)

        self.checkUpdate(p, q, True, check, overwrite = False, protect_structure = False)
        self.checkUpdate(p, q, True, check, overwrite = False, protect_structure = True)

    def testUpdate_03_StructurePreserving_03_correctError(self):

        p = TreeDict()
        p.a.x = 1
        p.a.y = 2

        ct = p.copy()

        q = TreeDict()
        q.a = 3

        self.checkUpdateBadStructure(p, q)

    def testUpdate_04_StructurePreserving_01(self):

        p = TreeDict()
        p.a = 3

        q = TreeDict()
        q.a.x = 1
        q.a.y = 2

        ct = q.copy()

        def check(r):
            self.assert_(r == ct)

        self.checkUpdate(p, q, True, check, overwrite = True, protect_structure = False)

    def testUpdate_04_StructurePreserving_02_noOverwrite(self):

        p = TreeDict()
        p.a = 3

        q = TreeDict()
        q.a.x = 1
        q.a.y = 2

        ct = q.copy()

        def check(r):
            self.assert_(r == TreeDict(a = 3))

        self.checkUpdate(p, q, True, check, overwrite = False, protect_structure = False)
        self.checkUpdate(p, q, True, check, overwrite = False, protect_structure = True)

    ################################################################################
    # Check object preservation when we're not supposed to have copying -- toy case

    def checkUpdate_05_SameObjectPreserved_01_simple(self, overwrite, protect_structure):
        u = unique_object()
        p = TreeDict()
        q = TreeDict(x = u)

        def check(r):
            self.assert_(r.x is u)

        self.checkUpdate(p, q, False, check, overwrite, protect_structure)

    def testUpdate_05_SameObjectPreserved_01_simple_FF(self):
        self.checkUpdate_05_SameObjectPreserved_01_simple(False, False)

    def testUpdate_05_SameObjectPreserved_01_simple_FT(self):
        self.checkUpdate_05_SameObjectPreserved_01_simple(False, True)

    def testUpdate_05_SameObjectPreserved_01_simple_FF(self):
        self.checkUpdate_05_SameObjectPreserved_01_simple(True, False)

    def testUpdate_05_SameObjectPreserved_01_simple_FT(self):
        self.checkUpdate_05_SameObjectPreserved_01_simple(True, True)

    ################################################################################
    # Check object preservation when we're not supposed to have copying

    def checkUpdate_05_SameObjectPreserved_02_complex(self, overwrite, protect_structure):
        p = random_tree(0, 50)
        cp = p.copy()

        q = random_tree(0, 50)
        cq = q.copy()

        def check(r):
            for k, v in chain(cp.iteritems(), cq.iteritems()):
                self.assert_(r[k] is v)

        self.checkUpdate(p, q, False, check, overwrite, protect_structure)

    def testUpdate_05_SameObjectPreserved_02_complex_FF(self):
        self.checkUpdate_05_SameObjectPreserved_02_complex(False, False)

    def testUpdate_05_SameObjectPreserved_02_complex_FT(self):
        self.checkUpdate_05_SameObjectPreserved_02_complex(False, True)

    def testUpdate_05_SameObjectPreserved_02_complex_FF(self):
        self.checkUpdate_05_SameObjectPreserved_02_complex(True, False)

    def testUpdate_05_SameObjectPreserved_02_complex_FT(self):
        self.checkUpdate_05_SameObjectPreserved_02_complex(True, True)


    ################################################################################
    # Atomic stuff

    def testUpdate_06_atomic_01(self):

        p = TreeDict.fromkeys('abcdefghijklmnopqrstuvwxyz')
        q = TreeDict.fromkeys('abcdefghijklnopqrstuvwxyz')
        q.m.x = 1

        cp = p.copy()
        cq = q.copy()

        self.assertRaises(TypeError, lambda: p.update(q, protect_structure = True))

        self.assert_(cp == p)
        self.assert_(cq == q)

    ################################################################################
    # Proper attachments

    def checkUpdate_07_properAttaching(self, overwrite, protect_structure):
        p = random_tree(0, 50)
        cp = p.copy()

        q = random_tree(0, 50)
        cq = q.copy()

        def check(r):
            for k in chain(cp.iterkeys(recursive = True, branch_mode = 'only'),
                           cq.iterkeys(recursive = True, branch_mode = 'only')):

                self.assert_(r[k].rootNode() is r)

        self.checkUpdate(p, q, False, check, overwrite, protect_structure)

    def testUpdate_07_properAttaching_FF(self):
        self.checkUpdate_07_properAttaching(False, False)

    def testUpdate_07_properAttaching_FT(self):
        self.checkUpdate_07_properAttaching(False, True)

    def testUpdate_07_properAttaching_FF(self):
        self.checkUpdate_07_properAttaching(True, False)

    def testUpdate_07_properAttaching_FT(self):
        self.checkUpdate_07_properAttaching(True, True)


    ################################################################################
    # Whether Tree Values are properly handled

    def checkUpdate_08_TreeValuesProperlyHandled(self, deep_copy, overwrite, protect_structure):
        p = TreeDict()
        p.a = TreeDict(x = 1, y = 2)

        q = TreeDict()
        q.a.y = 3
        q.a.z = 4

        def check(r):
            self.assert_(r.a.x == 1)
            self.assert_(r.a.y == 3 if overwrite else 2)
            self.assert_(r.a.z == 4)

        self.checkUpdate(p, q, deep_copy, check, overwrite, protect_structure)

    def testUpdate_08_TreeValuesProperlyHandled_FFF(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(False, False, False)

    def testUpdate_08_TreeValuesProperlyHandled_FFT(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(False, False, True)

    def testUpdate_08_TreeValuesProperlyHandled_FTF(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(False, True, False)

    def testUpdate_08_TreeValuesProperlyHandled_FTT(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(False, True, True)

    def testUpdate_08_TreeValuesProperlyHandled_TFF(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(True, False, False)

    def testUpdate_08_TreeValuesProperlyHandled_TFT(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(True, False, True)

    def testUpdate_08_TreeValuesProperlyHandled_TTF(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(True, True, False)

    def testUpdate_08_TreeValuesProperlyHandled_TTT(self):
        self.checkUpdate_08_TreeValuesProperlyHandled(True, True, True)

    def checkUpdate_09_ProperParents(self, deep_copy, overwrite, preserve_structure):

        p = TreeDict()

        ab = p.a.b = unique_object()
        ac = p.a.c = unique_object()
        b  = p.b   = unique_object()

        p2 = TreeDict()

        p2.update(p)

        self.assert_(p.a is not p2.a)
        self.assert_(p.a.rootNode() is p)
        self.assert_(p.a.parentNode() is p)
        self.assert_(p2.a.rootNode() is p2)
        self.assert_(p2.a.parentNode() is p2)

        self.assert_(p.a.b == p2.a.b)
        self.assert_(p.a.b is p2.a.b)

        self.assert_(p.a.c == p2.a.c)
        self.assert_(p.a.c is p2.a.c)

        self.assert_(p == p2)

    def testUpdate_10_rewritingLocal(self):

        # This test solidifies the following behavior

        p = TreeDict()
        p.a = TreeDict()

        q = TreeDict()
        q.a.x = 1

        p.update(q)

        self.assert_(p.a.isRoot())
        self.assert_(p.a.x == 1)

    def testUpdate_12_Atomic_01(self):

        p = TreeDict()
        p.makeBranch('b')
        p.b.freeze()

        p_before = p.copy()

        p2 = TreeDict(a = 1)
        p2["b.a"] = 4

        self.assert_(p_before == p)

        self.assertRaises(TypeError, lambda: p.update(p2))

        self.assert_(p_before == p)

    def testUpdate_12_Atomic_01b_large(self):

        p = random_tree()

        # Freeze b so it causes an error
        p.makeBranch('b')
        p.b.freeze()

        p_before = p.copy()

        p2 = TreeDict.fromkeys('acdefghijklmnopqrstuvwxyz')
        p2.update(random_tree())
        p2["b.a"] = 4

        self.assert_(p_before == p)

        self.assertRaises(TypeError, lambda: p.update(p2))

        self.assert_(p_before == p)

    def testUpdate_12_Atomic_02(self):

        p = TreeDict()
        p.a   = 1
        p.c   = 2

        p2 = TreeDict()
        p2.a.x = 3
        p2.c   = 4

        p_before = p.copy()

        self.assert_(p == p_before)

        self.checkUpdateBadStructure(p, p2)

        self.assert_(p == p_before)

    ################################################################################
    # Making sure branch values are not wrongly attached

    def checkUpdate_14_branchValuesNotAttached_01(self, overwrite, protect_structure):
        p = TreeDict()

        ax = p.a.x = TreeDict()
        ay = p.a.y = unique_object()
        p.b = 2

        p2 = TreeDict()
        az = p2.a.z = TreeDict()

        def check(r):
            self.assert_(r.a.x is ax)
            self.assert_(r.a.x.isRoot())
            self.assert_(r.a.y is ay)
            self.assert_(r.a.z is az)
            self.assert_(r.a.z.isRoot())
            self.assert_(r.b == 2)

        self.checkUpdate(p2, p, False, check, overwrite, protect_structure)

    def testUpdate_14_branchValuesNotAttached_01_FF(self):
        self.checkUpdate_14_branchValuesNotAttached_01(False, False)

    def testUpdate_14_branchValuesNotAttached_01_FT(self):
        self.checkUpdate_14_branchValuesNotAttached_01(False, True)

    def testUpdate_14_branchValuesNotAttached_01_TF(self):
        self.checkUpdate_14_branchValuesNotAttached_01(True, False)

    def testUpdate_14_branchValuesNotAttached_01_TT(self):
        self.checkUpdate_14_branchValuesNotAttached_01(True, True)

    ################################################################################
    # Dangling nodes handled properly

    def checkUpdate_15_DanglingNodesAttached(self, overwrite, protect_structure):
        p = TreeDict()
        a = p.a

        q = TreeDict()
        q.a.x = 1

        p.update(q, overwrite=overwrite, protect_structure =protect_structure)

        self.assert_(p.a.x == 1)
        self.assert_(a is p.a)
        self.assert_(a.rootNode() is p)

    def testUpdate_15_DanglingNodesAttached_FF(self):
        self.checkUpdate_15_DanglingNodesAttached(False, False)

    def testUpdate_15_DanglingNodesAttached_FT(self):
        self.checkUpdate_15_DanglingNodesAttached(False, True)

    def testUpdate_15_DanglingNodesAttached_TF(self):
        self.checkUpdate_15_DanglingNodesAttached(True, False)

    def testUpdate_15_DanglingNodesAttached_TT(self):
        self.checkUpdate_15_DanglingNodesAttached(True, True)

    ########################################

    def testUpdate_16_DanglingNodesIgnored(self):
        p = TreeDict()
        p.a = 1

        q = TreeDict()
        q.a

        def check(r):
            self.assert_(r.a == 1)

        self.checkUpdate(p, q, False, check, overwrite=True, protect_structure=True)


    ######################################################################
    # Check whether structure is preserved in the tree on an update

    def testUpdate_WithFreezing_01(self):

        p = TreeDict()

        p.a.x = 1

        q = TreeDict()

        q.b = 2

        p.update(q)

        self.assert_(p.a.x == 1)
        self.assert_(p.b == 2)

    def testUpdate_WithFreezing_02(self):

        p = TreeDict()

        p.a.x = 1

        p.freeze()

        q = TreeDict()

        q.a.y = 2

        self.assertRaises(TypeError, lambda: p.update(q))

        self.assert_(p.a.x == 1)
        self.assert_('b.y' not in p)

    def testUpdate_WithFreezing_StructureOnly_01(self):

        p = TreeDict()

        p.a = 1
        p.freeze(structure_only = True)

        q = TreeDict()
        q.a = 2

        p.update(q)

        self.assert_(p.a == 2)

    def testUpdate_WithFreezing_StructureOnly_02(self):

        p = TreeDict()

        p.a = 1
        p.freeze(structure_only = True)

        q = TreeDict()
        q.a = 2
        q.b = 3

        self.assertRaises(TypeError, lambda: p.update(q))

        self.assert_(p.a == 1)
        self.assert_('b' not in p)

    def testUpdate_WithFreezing_StructureOnly_03(self):

        p = TreeDict()

        p.a.x = 1
        p.freeze(structure_only = True)

        q = TreeDict()
        q.a.x = 2
        q.b.x = 3

        self.assertRaises(TypeError, lambda: p.update(q))

        self.assert_(p.a.x == 1)
        self.assert_('b' not in p)


    def testUpdate_WithFreezing_StructureOnly_04(self):

        p = TreeDict()

        p.a.x = 1
        p.freeze('a', structure_only = True)

        q = TreeDict()
        q.a.x = 2
        q.b = 3

        p.update(q)

        self.assert_(p.a.x == 2)
        self.assert_(p.b == 3)

    def testUpdate_WithFreezing_ValuesOnly_01(self):

        p = TreeDict()

        p.a = 1
        p.freeze(values_only = True)

        q = TreeDict()
        q.b = 2

        p.update(q)

        self.assert_(p.a == 1)
        self.assert_(p.b == 2)

    def testUpdate_WithFreezing_ValuesOnly_02(self):

        p = TreeDict()

        p.a.b = 1
        p.freeze(values_only = True)

        q = TreeDict()
        q.a.c = 2

        p.update(q)

        self.assert_(p.a.b == 1)
        self.assert_(p.a.c == 2)

    def testUpdate_WithFreezing_ValuesOnly_03(self):

        p = TreeDict()

        p.b = 1
        p.freeze(values_only = True)

        q = TreeDict()
        q.b = 2

        self.assertRaises(TypeError, lambda: p.update(q) )

    def testUpdate_WithFreezing_ValuesOnly_04(self):

        p = TreeDict()

        p.a.b = 1
        p.freeze(values_only = True)

        q = TreeDict()
        q.a.b = 2

        self.assertRaises(TypeError, lambda: p.update(q) )


    def testUpdate_WithFreezing_ValuesOnly_05(self):

        p = TreeDict()

        p.a.b = 1
        p.a.c.d = 2
        p.freeze(values_only = True)

        q = TreeDict()
        q.a.c.e = 3

        p.update(q)

        self.assert_(p.a.b == 1)
        self.assert_(p.a.c.d == 2)
        self.assert_(p.a.c.e == 3)

    def testUpdate_WithFreezing_ValuesOnly_06(self):

        p = TreeDict()

        p.a.b.c = 1
        p.freeze(values_only = True)

        q = TreeDict()
        q.a.b = 2

        self.assertRaises(TypeError, lambda: p.update(q) )




if __name__ == '__main__':
    unittest.main()

