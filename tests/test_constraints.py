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

from __future__ import division

import random, unittest, cPickle, collections
from treedict import TreeDict, getTree
import treedict
from copy import deepcopy, copy
from cPickle import dumps
from hashlib import md5
import random

from common import *

class TestConstraints(unittest.TestCase):
    def setUp(self):
        treedict.addConstraint("a_is_int", "a", lambda x: type(x) is int, "Not an integer.")
        treedict.addConstraint("a_in_125", "a", lambda x: x == 1 or x == 2 or x == 5, "Not 1,2,or 5.")
        treedict.addGlobalConstraint("in_134", set([1,3,4]), "Not 1, 3, or 4")
        treedict.addGlobalConstraint("l_in_134", [1,3,4], "Not 1, 3, or 4")
        treedict.addGlobalConstraint("in_134l", [1,3,4,[]], "Not 1, 3, 5 or []")
       

    # treedict.addConstraint("a_is_int", "a", lambda x: type(x) is int, "Not an integer.")
    def testConstraint_01_pos(self):
        p1 = getTree("a_is_int")
        p1.a = 15

    def testConstraint_01_neg1(self):
        def f():
            p1 = getTree("a_is_int")
            p1.a = 15.3

        self.assertRaises(ValueError, f)

    def testConstraint_01_neg2(self):
        def f():
            p1 = getTree("a_is_int")
            p1.a.b = 0

        self.assertRaises(ValueError, f)

    def testConstraint_01_only_for_getTree(self):
        p1 = TreeDict("a_is_int")
        p1.a = 15.3

    # treedict.addConstraint("a_in_125", "a", lambda x: x == 1 or x == 2 or x == 5, "Not 1,2,or 5.")
    def testConstraint_02_pos(self):
        p1 = getTree("a_in_125")
        p1.a = 5

    def testConstraint_02_neg1(self):
        def f():
            p1 = getTree("a_in_125")
            p1.a = 4

        self.assertRaises(ValueError, f)

    def testConstraint_02_neg2(self):
        def f():
            p1 = getTree("a_in_125")
            p1.a.b = 0

        self.assertRaises(ValueError, f)

    def testConstraint_02_neg3(self):
        def f():
            p1 = getTree("a_in_125")
            p1.a = None

        self.assertRaises(ValueError, f)

    # treedict.addGlobalConstraint("in_134", set(1,3,4), "Not 1, 3, or 4")
    def testConstraint_03_pos(self):
        p1 = getTree(unique_name())
        p1.in_134 = 4

    def testConstraint_03_neg1(self):
        def f():
            p1 = getTree(unique_name())
            p1.in_134 = 5

        self.assertRaises(ValueError, f)

    def testConstraint_03_neg2(self):
        def f():
            p1 = getTree(unique_name())
            p1.in_134.b = 123

        self.assertRaises(ValueError, f)

    #treedict.addGlobalConstraint("l_in_134", list(1,3,4), "Not 1, 3, or 4")
    def testConstraint_04_pos(self):
        p1 = getTree(unique_name())
        p1.l_in_134 = 4

    def testConstraint_04_neg1(self):
        def f():
            p1 = getTree(unique_name())
            p1.l_in_134 = 5

        self.assertRaises(ValueError, f)

    def testConstraint_04_neg2(self):
        def f():
            p1 = getTree(unique_name())
            p1.l_in_134.b = 123

        self.assertRaises(ValueError, f)

    # treedict.addGlobalConstraint("in_134l", list(1,3,4,[]), "Not 1, 3, 5 or []")
    def testConstraint_05_pos(self):
        p1 = getTree(unique_name())
        p1.in_134l = []

    def testConstraint_05_neg1(self):
        def f():
            p1 = getTree(unique_name())
            p1.in_134l = 5

        self.assertRaises(ValueError, f)

    def testConstraint_05_neg2(self):
        def f():
            p1 = getTree(unique_name())
            p1.in_134l.b = []

        self.assertRaises(ValueError, f)


    def testConstraint_06_afterwards_1(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        p[bn] = "borkbork"
        
        def f():
            treedict.addConstraint(tn, bn,["bork", "bork1"])

        self.assertRaises(ValueError, f)

    def testConstraint_06_afterwards_2(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        p[bn] = "bork"  # passes
        
        treedict.addConstraint(unique_name(), bn,["bork", "bork1"])
        

    def testConstraint_07_afterwards_global_1(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        p[bn] = "borkbork"
        
        def f():
            treedict.addGlobalConstraint(bn, ["bork", "bork1"])

        self.assertRaises(ValueError, f)

    def testConstraint_07_afterwards_global_2(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        p[bn] = "bork"
        
        treedict.addGlobalConstraint(bn, ["bork", "bork1"])

    def testConstraint_06_afterwards_1_copy(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        
        p[bn] = "bork"     # passes 
        q = p.copy(deep = True)
        q[bn] = "borkbork" # causes failure
        
        def f():
            treedict.addConstraint(tn, bn, ["bork", "bork1"])

        self.assertRaises(ValueError, f)

    def testConstraint_06_afterwards_2_copy(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        p[bn] = "bork"  # passes
        q = p.copy(deep = True)
        q[bn] = "bork1"  # passes

        treedict.addConstraint(tn, bn, ["bork", "bork1"])
        
    def testConstraint_06_afterwards_3_copy_large(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)

        for i in range(100):
            p[bn] = "bork"  # passes
            p = p.copy()

        p[bn] = "borkbork"  # fails

        def f():
            treedict.addConstraint(tn, bn, ["bork", "bork1"])

        self.assertRaises(ValueError, f)

    def testConstraint_07_afterwards_global_1_copy(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        b = p.copy()
        b[bn]= 2
        
        def f():
            treedict.addGlobalConstraint(bn, [1], "not 1")

        self.assertRaises(ValueError, f)

    def testConstraint_07_afterwards_global_1_copy_control(self):
        tn = unique_name()
        bn = unique_name()

        p = getTree(tn)
        b = p.copy()
        b[bn] = 1
        
        # Should be fine
        treedict.addGlobalConstraint(bn, [1], "not 1")
        

    def testConstraint_08_branch_copy_1(self):
        tn = unique_name()
        bn = unique_name()

        treedict.addConstraint(tn, 'a.b.c', [1], "not 1")
        
        p = getTree(tn)
        p.a.makeBranch('b')
        q = p.a.b.copy()

        def f():
            q.c = 2  # should be bad

        self.assertRaises(ValueError, f)

    def testConstraint_08_branch_copy_2(self):
        tn = unique_name()

        treedict.addConstraint(tn, 'a.b.c', [1], "not 1")
        
        p = getTree(tn)
        p.makeBranch('a.b')
        q = p.a.b.copy()

        def f():
            q.c = 2  # should be bad

        self.assertRaises(ValueError, f)


    def testConstraint_08_branch_copy_afterwards_1(self):
        tn = unique_name()

        p = getTree(tn)
        p.makeBranch('a18462.a1732643')
        q = p.a18462.copy()
        q.a1732643.a1232 = "borkbork"  # should be bad

        def f():
            treedict.addConstraint(tn, 'a18462.a1732643.a1232', ["bork"])
        
            
        self.assertRaises(ValueError, f)

    def testConstraint_08_branch_copy_afterwards_2(self):
        tn = unique_name()

        p = getTree(tn)
        p.makeBranch('a18462.a1732643')

        q = p.a18462.a1732643.copy()
        q.a1232 = "borkbork"  # should be bad

        def f():
            treedict.addConstraint(tn, 'a18462.a1732643.a1232', ["bork"])

        self.assertRaises(ValueError, f)


    def testConstraint_08_global_branch_copy_afterwards_1(self):
        bn = unique_name()

        p = getTree(unique_name())
        p.makeBranch(bn).makeBranch('a')

        q = p[bn].copy()
        q.a.b = "borkbork"  # should be bad

        def f():
            treedict.addGlobalConstraint(bn + '.a.b', ["bork"])
            
        self.assertRaises(ValueError, f)

    def testConstraint_08_global_branch_copy_afterwards_1_control(self):
        bn = unique_name()

        p = getTree(unique_name())
        p.makeBranch(bn).makeBranch('a')

        q = p[bn].copy()
        q.a.b = "bork"  # should be bad

        treedict.addGlobalConstraint(bn + '.a.b', ["bork"])

    # Test for tree names that look like branch names
    def testConstraint_09_branches_in_tree_names_01(self):
        tn = unique_name()
        tnb = tn + '.b'

        p = getTree(tnb)
        treedict.addConstraint(tn, 'b.a', [1], "not 1")

        # shouldn't throw
        p.a = 2
        
    # Test for tree names that look like branch names
    def testConstraint_09_branches_in_tree_names_02(self):
        tn = unique_name()

        p = getTree(tn)

        treedict.addConstraint(tn + '.b', 'a', [1], "not 1")

        # shouldn't throw
        p.b.a = 2
        
    # Test for tree names that look like branch names
    def testConstraint_09_branches_in_tree_names_03(self):
        tn = unique_name()
        tnb = tn + '.b'

        p = getTree(tnb)

        treedict.addConstraint(tnb, 'a', [1], "not 1")

        # should throw
        def f():
            p.a = 2

        self.assertRaises(ValueError, f)

    # Test for tree names that look like branch names
    def testConstraint_09_branches_in_tree_names_03_control(self):
        tn = unique_name()
        tnb = tn + '.b'
        p = getTree(tnb)

        treedict.addConstraint(tnb, 'a', [1], "not 1")

        # shouldn't throw
        p.a = 1

    def testConstraint_10_copying_01(self):

        tn, bn = unique_name(), unique_name()

        p1 = getTree(tn)
        p1.makeBranch(bn)

        p2 = getTree(bn)
        p1c = p1[bn].copy()

        treedict.addConstraint(tn, bn +'.a', [1], "not 1")
        
        # Should work
        p2.a = 2

        def f():
            # Should throw, cause it's part of p1's family
            p1c.a = 2

        self.assertRaises(ValueError, f)

        # Shouldn't throw, cause it passes
        p1c.a = 1

        
    def testConstraint_10_copying_02(self):
        tn, bn = unique_name(), unique_name()

        p1 = getTree(tn)
        p1c = p1.makeBranch(bn).copy()
        p2 = getTree(bn)
        
        treedict.addConstraint(bn, 'a', [1], "not 1")

        # Should work fine; not part of p2's family
        p1c.a = 2
        self.assert_(p1c.branchName() == bn)
        
        # Should throw, cause it's part of p2's family
        def f(): p2.a = 2

        self.assertRaises(ValueError, f)

        # Shouldn't throw, it passes
        p2.a = 1


    def testConstraint_11_copying_01_afterwards(self):

        tn, bn = unique_name(), unique_name()

        p1 = getTree(tn)
        p1.makeBranch(bn)

        p2 = getTree(bn)

        p1c = p1[bn].copy()

        treedict.addConstraint(tn, bn +'.a', [1], "not 1")
        
        # Should work
        p2.a = 2
        
        def f():
            # Should throw, cause it's part of p1's family
            p1c.a = 2

        self.assertRaises(ValueError, f)

        # Shouldn't throw, cause it passes
        p1c.a = 1

        
    def testConstraint_11_copying_02_aferwards(self):
        tn, bn = unique_name(), unique_name()

        p1 = getTree(tn)
        p1c = p1.makeBranch(bn).copy()
        p2 = getTree(bn)
        
        
        # Should work fine; not part of p2's family
        p1c.a = 2
        self.assert_(p1c.branchName() == bn)
        
        # Should cause throw, cause it's part of p2's family
        p2.a = 2
        
        def f(): treedict.addConstraint(bn, 'a', [1], "not 1")

        self.assertRaises(ValueError, f)

    def testConstraint_15_no_change_on_failure(self):
        tn = unique_name()
        
        p = getTree(tn)
        p.b   = 123
        p.c.b = 'bork'
        
        p1 = p.copy()

        treedict.addConstraint(tn, 'a.b.c.d', [1], "not 1")

        def f():
            p["a.b.c.d"] = 2
            
        self.assertRaises(ValueError, f)

        self.assert_(p == p1)
        
    def testConstraint_16_constraint_not_added_on_failure(self):
        tn = unique_name()
        
        p = getTree(tn)
        p["a.b.c.d"] = 2

        def f():
            treedict.addConstraint(tn, 'a.b.c.d', [1], "not 1")
            
        self.assertRaises(ValueError, f)

        # Should be fine still, as 
        p["a.b.c.d"] = 2

    def testConstraint_16_constraint_not_added_on_failure__control(self):
        tn = unique_name()
        
        p = getTree(tn)
        p["a.b.c.d"] = 1

        treedict.addConstraint(tn, 'a.b.c.d', [1], "not 1")
            
        # Should now throw, as the constraint is in place
        def f():
            p["a.b.c.d"] = 2

        self.assertRaises(ValueError, f)


    def testConstraint_17_global_constraint_not_added_on_failure(self):
        tn1 = unique_name()
        tn2 = unique_name()
        bn = unique_name()
        
        p1 = getTree(tn1)
        p1[bn] = 2

        p2 = getTree(tn2)

        def f():
            treedict.addGlobalConstraint(bn, [1], "not 1")
            
        self.assertRaises(ValueError, f)

        # Should be fine still, as the constraint should be backed out
        p2[bn] = 2


    def testConstraint_17_constraint_not_added_on_failure__control(self):
        tn1 = unique_name()
        tn2 = unique_name()
        bn = unique_name()
        
        p1 = getTree(tn1)
        p1[bn] = 1

        p2 = getTree(tn2)

        treedict.addGlobalConstraint(bn, [1], "not 1")
            
        # Should throw, as the constraint succeeded
        def f():
            p2[bn] = 2

        self.assertRaises(ValueError, f)

        # Control, should pass
        p2[bn] = 1


    def testConstraint_18_copying_original_tracks_constraints_01(self):

        tn = unique_name()
        bn = unique_name()
        
        p1 = getTree(tn)
        p2 = p1.copy()

        treedict.addConstraint(tn, bn, [1], "not 1")
            
        # Should throw
        def f():
            p2[bn] = 2

        self.assertRaises(ValueError, f)

        # Control, should pass
        p2[bn] = 1

    def testConstraint_18_copying_original_tracks_constraints_02(self):

        tn = unique_name()
        bn = unique_name()
        
        p = getTree(tn)
        p.a = 1
        p.b = 2

        for i in range(1000):
            p = p.copy(deep = True)

        treedict.addConstraint(tn, bn, [1], "not 1")
            
        # Should throw
        def f():
            p[bn] = 2

        self.assertRaises(ValueError, f)

        # control, should pass
        p[bn] = 1


    def testConstraint_18_copying_original_tracks_constraints_01_after(self):

        tn = unique_name()
        bn = unique_name()
        
        p1 = getTree(tn)
        p2 = p1.copy()

        p2[bn] = 2

        # Should throw
        def f():
            treedict.addConstraint(tn, bn, [1], "not 1")

        self.assertRaises(ValueError, f)

        # The control; should pass
        treedict.addConstraint(tn, bn, [2], "not 2")

    def testConstraint_18_copying_original_tracks_constraints_02_after(self):

        tn = unique_name()
        bn = unique_name()
        
        p = getTree(tn)
        p.a = 1
        p.b = 2

        for i in range(1000):
            p = p.copy(deep = True)

        p[bn] = 2
            
        # Should throw
        def f():
            treedict.addConstraint(tn, bn, [1], "not 1")

        self.assertRaises(ValueError, f)

        # The control; should pass
        treedict.addConstraint(tn, bn, [2], "not 2")

    def testConstraint_19_global__copying_original_tracks_constraints_01(self):

        tn = unique_name()
        bn = unique_name()
        
        p1 = getTree(tn)
        p2 = p1.copy()

        treedict.addGlobalConstraint(bn, [1], "not 1")

        # Should throw
        def f():
            p2[bn] = 2

        self.assertRaises(ValueError, f)

        # The control
        p2[bn] = 1

    def testConstraint_19_global__copying_original_tracks_constraints_02(self):

        tn = unique_name()
        bn = unique_name()
        
        p = getTree(tn)
        p.a = 1
        p.b = 2

        for i in range(1000):
            p = p.copy(deep = True)

        treedict.addGlobalConstraint(bn, [1], "not 1")
            
        # Should throw
        def f():
            p[bn] = 2

        self.assertRaises(ValueError, f)

        # The control
        p[bn] = 1

    def testConstraint_19_global__copying_original_tracks_constraints_01_after(self):

        tn = unique_name()
        bn = unique_name()
        
        p1 = getTree(tn)
        p2 = p1.copy()

        p2[bn] = 2

        # Should throw
        def f():
            treedict.addGlobalConstraint(bn, [1], "not 1")

        self.assertRaises(ValueError, f)

        # And the control
        treedict.addGlobalConstraint(bn, [2], "not 2")


    def testConstraint_19_global__copying_original_tracks_constraints_02_after(self):

        tn = unique_name()
        bn = unique_name()
        
        p = getTree(tn)
        p.a = 1
        p.b = 2

        for i in range(1000):
            p = p.copy(deep = True)

        p[bn] = 2
            
        # Should throw
        def f():
            treedict.addGlobalConstraint(bn, [1], "not 1")

        self.assertRaises(ValueError, f)

        # And the control
        treedict.addGlobalConstraint(bn, [2], "not 2")

    def testConstraint_20_global__branches_track_original__after(self):
        
        tn = unique_name()
        bn1 = unique_name()
        bn2 = unique_name()

        p = getTree(tn)

        p.makeBranch(bn1 + '.' + bn2)
        b1 = p[bn1].copy()
        b2 = b1[bn2].copy()
        
        b2.x = 1
        b1[bn2]['x'] = 2

        def f():
            treedict.addGlobalConstraint('%s.%s.x' % (bn1, bn2), [1], "not 1")

            
        self.assertRaises(ValueError, f)


    def testConstraint_21_global__branches_track_original_deep(self):
        n = 100
        tn = unique_name()
        bnl = [unique_name() for i in range(n)]
        p = getTree(tn)

        fullbn = '.'.join(bnl)

        p.makeBranch(fullbn)

        bl = [None]*n

        for i, bn in enumerate(bnl):
            bl[i] = (p if i == 0 else bl[i-1])[bn]

        treedict.addGlobalConstraint(fullbn + '.x', [1], "not 1")

        for i, b in enumerate(bnl[:-1]):

            def f():
                bl[i]['.'.join(bnl[i+1:]) + '.x'] = 2

            self.assertRaises(ValueError, f)

        for i, b in enumerate(bnl[:-1]):
            bl[i]['.'.join(bnl[i+1:]) + '.x'] = 1


    def testConstraint_21_global__branches_track_original_deep__after(self):
        n = 10
        tn = unique_name()
        bnl = [unique_name() for i in range(n)]
        p = getTree(tn)

        fullbn = '.'.join(bnl)

        p.makeBranch(fullbn)

        bl = [None]*n

        bcopy = [None]*n

        for i, bn in enumerate(bnl):
            bl[i] = (p if i == 0 else bl[i-1])[bn]

        def get_x_name(i):
            return '.'.join(bnl[i+1:] + ['x'])

        self.assert_(get_x_name(n-1) == 'x')
        self.assert_(get_x_name(n-2) == '%s.x' % bnl[-1])
        self.assert_(get_x_name(0) == '%s.x' % '.'.join(bnl[1:]))

        for i, b in enumerate(bnl):
            bcopy[i] = bl[i].copy()
            bcopy[i][get_x_name(i)] = 1

        n2 = n // 2

        bcopy[n2][get_x_name(n2)] = 2

        def f():
            treedict.addGlobalConstraint(fullbn + '.x', [1], "not 1")
            
        self.assertRaises(ValueError, f)
        

    def testConstraint_22_IntermediatesMustBeBranches_01(self):
        tn = unique_name()
        
        treedict.addConstraint(tn, 'a.b.c.d.v', [1], "not 1")

        p = treedict.getTree(tn)

        def f():
            p["a.b"] = 1

        self.assertRaises(ValueError, f)

        # control
        p.a.makeBranch("b")

    def testConstraint_22_IntermediatesMustBeBranches_02_after(self):
        tn = unique_name()
        
        p = treedict.getTree(tn)

        p["a.b"] = 1

        def f():
            treedict.addConstraint(tn, 'a.b.c.d.v', [1], "not 1")

        self.assertRaises(ValueError, f)

        # control
        treedict.addConstraint(tn, 'a.b', [1], "not 1")

    def testConstraint_22_IntermediatesMustBeBranches_03_global(self):
        tn = unique_name()
        bn = unique_name()
        
        treedict.addGlobalConstraint(bn + '.a.b.c.d.v', [1], "not 1")

        p = treedict.getTree(tn)

        def f():
            p[bn + ".a.b"] = 1

        self.assertRaises(ValueError, f)

        # control
        p.makeBranch(bn + ".a.b")

    def testConstraint_22_IntermediatesMustBeBranches_04_global_after(self):
        bn = unique_name()
        tn = unique_name()
        
        p = treedict.getTree(tn)

        p[bn + ".a.b"] = 1

        def f():
            treedict.addGlobalConstraint(bn + '.a.b.c.d.v', [1], "not 1")

        self.assertRaises(ValueError, f)

        treedict.addGlobalConstraint(bn + '.a.b', [1], "not 1")

    def testConstraint_23_IntermediatesMustBeBranches_copied_01(self):
        tn = unique_name()
        
        treedict.addConstraint(tn, 'a.b.c.d.v', [1], "not 1")

        pb = treedict.getTree(tn)

        pb.makeBranch('a.b')

        p = pb.a.b.copy()

        def f():
            p["c.d"] = 1

        self.assertRaises(ValueError, f)

        # control
        p.c.makeBranch("d")

    def testConstraint_23_IntermediatesMustBeBranches_copied_02_after(self):
        tn = unique_name()
        
        pb = treedict.getTree(tn)

        pb.makeBranch('a.b')
        p = pb.a.b.copy()

        p["c.d"] = 1

        def f():
            treedict.addConstraint(tn, 'a.b.c.d.v', [1], "not 1")
            
        self.assertRaises(ValueError, f)

        # control
        treedict.addConstraint(tn, 'a.b.c.d', [1], "not 1")

    def testConstraint_23_IntermediatesMustBeBranches_copied_03_global(self):
        tn = unique_name()
        bn = unique_name()
        
        treedict.addGlobalConstraint(bn + '.a.b.c.d.v', [1], "not 1")

        pb = treedict.getTree(tn)

        pb.makeBranch(bn)
        pb[bn].makeBranch('a.b')

        p = pb[bn].a.b.copy()

        def f():
            p["c.d"] = 1

        self.assertRaises(ValueError, f)

        # control
        p.c.makeBranch("d")

    def testConstraint_23_IntermediatesMustBeBranches_copied_04_global_after(self):
        tn = unique_name()
        bn = unique_name()
        
        pb = treedict.getTree(tn)

        pb.makeBranch(bn)
        pb[bn].makeBranch('a.b')

        p = pb[bn].a.b.copy()

        p["c.d"] = 1

        def f():
            treedict.addGlobalConstraint(bn + '.a.b.c.d.v', [1], "not 1")
            
        self.assertRaises(ValueError, f)

        # control
        treedict.addGlobalConstraint(bn + '.a.b.c.d', [1], "not 1")

    
    def testConstraint_24_CopyingBranchTracks(self):
        # A regression test

        tn = unique_name()

        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.b.c.d.v', [1], "not 1")

        p.a.b.c.d.v = 1
        
        pc = p.a.b.copy()
        
        # would raise an error earlier
        pc.a.b.v = 1

    ##################################################
    # Handling links -- kinda a pain

    def testConstraint_25_Links_01(self):
        tn = unique_name()
        p = treedict.getTree(tn)
        treedict.addConstraint(tn, 'a.b.link.v', [1], "not 1")

        p.d.v = 1
        p.a.b.link = p.d

        self.assert_(p.a.b.link.v == 1)


    def testConstraint_25_Links_02_bad_value(self):
        tn = unique_name()
        p = treedict.getTree(tn)
        treedict.addConstraint(tn, 'a.b.link.v', [1], "not 1")

        p.d.v = 2

        def f():
            p.a.b.link = p.d
        
        self.assertRaises(ValueError, f)


    def testConstraint_25_Links_03_set_in_linked_root(self):
        tn = unique_name()
        p = treedict.getTree(tn)
        treedict.addConstraint(tn, 'a.b.link.v', [1], "not 1")

        p.a.b.link = p.d

        def f():
            p.d.v = 1

        self.assertRaises(ValueError, f)

    def testConstraint_26_global_Links_01(self):
        tn = unique_name()
        bn = unique_name()

        link_key = bn + '.a.b.link'

        p = treedict.getTree(tn)
        treedict.addConstraint(tn, link_key + '.v', [1], "not 1")

        p[link_key] = p.d
        p.d.v = 1

        self.assert_(p[link_key].v == 1)

    def testConstraint_26_global_Links_02_bad_value(self):
        tn = unique_name()
        bn = unique_name()

        link_key = bn + '.a.b.link'

        p = treedict.getTree(tn)
        treedict.addConstraint(tn, link_key + '.v', [1], "not 1")

        p[link_key] = p.d

        def f():
            p.d.v = 2

        self.assertRaises(ValueError, f)

    def testConstraint_26_global_Links_03_set_in_linked_root(self):
        tn = unique_name()
        bn = unique_name()

        link_key = bn + '.a.b.link'

        p = treedict.getTree(tn)
        treedict.addConstraint(tn, link_key + '.v', [1], "not 1")

        p.d.v = 2

        def f():
            p[link_key] = p.d

        self.assertRaises(ValueError, f)

    def testConstraint_27_after_Links_01(self):
        tn = unique_name()
        p = treedict.getTree(tn)
        
        p.d.v = 1
        p.a.b.link = p.d

        treedict.addConstraint(tn, 'a.b.link.v', [1], "not 1")

        self.assert_(p.a.b.link.v == 1)


    def testConstraint_27_after_Links_02_bad_value(self):
        tn = unique_name()
        p = treedict.getTree(tn)
        
        p.a.b.link = p.d
        p.d.v = 2

        def f():
            treedict.addConstraint(tn, 'a.b.link.v', [1], "not 1")
        
        self.assertRaises(ValueError, f)

    def testConstraint_28_after_global_Links_01(self):
        tn = unique_name()
        bn = unique_name()

        link_key = bn + '.a.b.link'

        p = treedict.getTree(tn)

        p[link_key] = p.d
        p.d.v = 1

        treedict.addConstraint(tn, link_key + '.v', [1], "not 1")

        self.assert_(p[link_key].v == 1)

    def testConstraint_28_after_global_Links_02_bad_value(self):
        tn = unique_name()
        bn = unique_name()

        link_key = bn + '.a.b.link'

        p = treedict.getTree(tn)

        p[link_key] = p.d
        p.d.v = 2

        def f():
            treedict.addConstraint(tn, link_key + '.v', [1], "not 1")

        self.assertRaises(ValueError, f)


    def testConstraint_29_Links_deeper_reference(self):
        tn = unique_name()
        p = treedict.getTree(tn)
        treedict.addConstraint(tn, 'l1.v', [1], "not 1")

        p.l1 = p.l2
        p.l2 = p.l3
        p.l3 = p.l4
        p.l4 = p.l5
        p.l5 = p.l6
        p.l6 = p.l7

        p.l7.v = 1

        self.assert_(p.l1.v == 1)
        self.assert_(p.l2.v == 1)
        self.assert_(p.l3.v == 1)
        self.assert_(p.l4.v == 1)
        self.assert_(p.l5.v == 1)
        self.assert_(p.l6.v == 1)
        self.assert_(p.l7.v == 1)
        

    def testConstraint_30_Link_Conf_01(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.b.c', [1], "not 1")

        p.aa.a.bb.b.c = 2
        p.a = p.aa.a

        def f():
           p.a.b = p.a.bb.b 

        self.assertRaises(ValueError, f)


    def testConstraint_30_Link_Conf_02(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 2
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.c = p.aa.c

        def f():
            p.a = p.c

        self.assertRaises(ValueError, f)

    def testConstraint_30_Link_Conf_03(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 2
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.a = p.c

        def f():
            p.c = p.aa.c
            

        self.assertRaises(ValueError, f)

    def testConstraint_30_Link_Conf_04(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 2
        p.aa.bb.c = p.aa.bb.cc
        p.c = p.aa.c
        p.a = p.c

        def f():
            p.aa.c = p.aa.bb.c
            

        self.assertRaises(ValueError, f)

    def testConstraint_30_Link_Conf_05(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 2
        p.aa.c = p.aa.bb.c
        p.c = p.aa.c
        p.a = p.c

        def f():
            p.aa.bb.c = p.aa.bb.cc
            

        self.assertRaises(ValueError, f)

    def testConstraint_30_Link_Conf_06(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.c = p.aa.c
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.a = p.c

        def f():
            p.aa.bb.cc.dd.v = 2
            
        self.assertRaises(ValueError, f)

    def testConstraint_30_Link_Conf_01_control(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.b.c', [1], "not 1")

        p.aa.a.bb.b.c = 1
        p.a = p.aa.a

        def f():
           p.a.b = p.a.bb.b 


    def testConstraint_30_Link_Conf_02_control(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 1
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.c = p.aa.c

        def f():
            p.a = p.c

    def testConstraint_30_Link_Conf_03_control(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 1
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.a = p.c

        def f():
            p.c = p.aa.c
            

    def testConstraint_30_Link_Conf_04_control(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 1
        p.aa.bb.c = p.aa.bb.cc
        p.c = p.aa.c
        p.a = p.c

        def f():
            p.aa.c = p.aa.bb.c
            

    def testConstraint_30_Link_Conf_05_control(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.aa.bb.cc.dd.v = 1
        p.aa.c = p.aa.bb.c
        p.c = p.aa.c
        p.a = p.c

        def f():
            p.aa.bb.c = p.aa.bb.cc
            

    def testConstraint_30_Link_Conf_06_control(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)

        treedict.addConstraint(tn, 'a.v', [1], "not 1")

        p.c = p.aa.c
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.a = p.c

        def f():
            p.aa.bb.cc.dd.v = 1

    def testConstraint_30_Link_Conf_01_after(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)


        p.aa.a.bb.b.c = 2
        p.a.b = p.a.bb.b 
        p.a = p.aa.a

        def f():
            treedict.addConstraint(tn, 'a.b.c', [1], "not 1")

        self.assertRaises(ValueError, f)


    def testConstraint_30_Link_Conf_02_after(self):
        
        tn = unique_name()
        p = treedict.getTree(tn)
        
        p.aa.bb.cc.dd.v = 2
        p.aa.bb.c = p.aa.bb.cc
        p.aa.c = p.aa.bb.c
        p.a = p.c
        p.c = p.aa.c

        def f():
            treedict.addConstraint(tn, 'a.v', [1], "not 1")

        self.assertRaises(ValueError, f)


if __name__ == '__main__':
    unittest.main()

