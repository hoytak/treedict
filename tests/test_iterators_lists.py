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

from hashlib import md5
import random

from common import *

class TestIteratorsLists(unittest.TestCase):


    ################################################################################
    # Now iterators

    def testIterators_01_flat(self):
        p = TreeDict()
        items = [('a', 1), ('b', 2), ('c', 3)]

        p.set(**dict(items))
 
        self.assert_(set(p.iterkeys())   == set([k for k, v in items]))
        self.assert_(set(p.itervalues()) == set([v for k, v in items]))
        self.assert_(set(p.iteritems())  == set(items))
        
        
    def testIterators_02_recursive(self):
        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        self.assert_(set(p.iterkeys())   == set([k for k, v in items]))
        self.assert_(set(p.itervalues()) == set([v for k, v in items]))
        self.assert_(set(p.iteritems())  == set(items))
        

    def testIterators_03_nonrecursive_skipbranches(self):
        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        non_recursive = [(k,v) for k, v in items
                         if '.' not in k]

        self.assert_(set(p.iterkeys(recursive=False)) 
                         == set([k for k, v in non_recursive]))
        self.assert_(set(p.itervalues(recursive=False))
                         == set([v for k, v in non_recursive]))
        self.assert_(set(p.iteritems(recursive=False))
                         == set(non_recursive))

    def testIterators_04_nonrecursive_withbranches(self):
        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        nrwb  = [(k, p.get(k)) for k in ['a', 'b', 'c', 'aa']]

        p.freeze()

        self.assert_(set(p.iterkeys(recursive=False, branch_mode = "all"))
                     == set([k for k, v in nrwb]))
        self.assert_(set(p.itervalues(recursive=False, branch_mode = "all"))
                     == set([v for k, v in nrwb]))
        self.assert_(set(p.iteritems(recursive=False, branch_mode = "all"))
                     == set(nrwb))
 
    def testIterators_05_branches(self):
        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        bl  = [(k, p.get(k)) for k in ['a', 'aa']]

        p.freeze()

        self.assert_(set(p.itervalues(False, branch_mode = "only")) == set([v for k, v in bl]))
        self.assert_(set(p.iterkeys(False, branch_mode = "only")) == set([k for k, v in bl]))
        self.assert_(set(p.iteritems(False, branch_mode = "only")) == set(bl))


    def testIterators_06_large_recursive(self):
        n = 500

        p = TreeDict()
        kl = random_node_list(0, n, 0.75)

        for i, k in enumerate(kl):
            p.set(k, i)

        self.assert_(set(p.iterkeys()) == set(kl))
        self.assert_(set(p.itervalues()) == set(range(n)))

    def _checkAllIterators(self, p, test, rid):

        s1 = set(l for l in p.iterkeys(*test))
        self.assert_(s1 == set(k for k,v in rid[test]), str(s1))

        s2 = set(l for l in p.iteritems(*test))
        self.assert_(s2 == rid[test], str(s2))

        s3 = set(l for l in p.itervalues(*test))
        self.assert_(s3 == set(v for k,v in rid[test]), str(s3))

    def testIterators_07_empty_rn(self):
        
        p = TreeDict()
        self.assert_([l for l in p.iterkeys(True, "none")] == [])
        self.assert_([l for l in p.iteritems(True, "none")] == [])
        self.assert_([l for l in p.itervalues(True, "none")] == [])

    def testIterators_07_empty_ra(self):
        
        p = TreeDict()
        self.assert_([l for l in p.iterkeys(True, "all")] == [])
        self.assert_([l for l in p.iteritems(True, "all")] == [])
        self.assert_([l for l in p.itervalues(True, "all")] == [])

    def testIterators_07_empty_ro(self):
        
        p = TreeDict()
        self.assert_([l for l in p.iterkeys(True, "only")] == [])
        self.assert_([l for l in p.iteritems(True, "only")] == [])
        self.assert_([l for l in p.itervalues(True, "only")] == [])

    def testIterators_07_empty_fn(self):
        
        p = TreeDict()
        self.assert_([l for l in p.iterkeys(False, "none")] == [])
        self.assert_([l for l in p.iteritems(False, "none")] == [])
        self.assert_([l for l in p.itervalues(False, "none")] == [])

    def testIterators_07_empty_fa(self):
        
        p = TreeDict()
        self.assert_([l for l in p.iterkeys(False, "all")] == [])
        self.assert_([l for l in p.iteritems(False, "all")] == [])
        self.assert_([l for l in p.itervalues(False, "all")] == [])

    def testIterators_07_empty_fo(self):
        
        p = TreeDict()
        self.assert_([l for l in p.iterkeys(False, "only")] == [])
        self.assert_([l for l in p.iteritems(False, "only")] == [])
        self.assert_([l for l in p.itervalues(False, "only")] == [])


    ############################################################
    # Make sure it handles everything okay

    def testIterators_08_basic_walking_test__rn(self):

        p, rid = basic_walking_test()
        test = (True, "none")
        self._checkAllIterators(p, test, rid)

    def testIterators_08_basic_walking_test__ra(self):

        p, rid = basic_walking_test()
        test = (True, "all")
        self._checkAllIterators(p, test, rid)

    def testIterators_08_basic_walking_test__ro(self):

        p, rid = basic_walking_test()
        test = (True, "only")
        self._checkAllIterators(p, test, rid)

    def testIterators_08_basic_walking_test__fn(self):

        p, rid = basic_walking_test()
        test = (False, "none")
        self._checkAllIterators(p, test, rid)

    def testIterators_08_basic_walking_test__fa(self):

        p, rid = basic_walking_test()
        test = (False, "all")
        self._checkAllIterators(p, test, rid)

    def testIterators_08_basic_walking_test__fo(self):

        p, rid = basic_walking_test()
        test = (False, "only")
        self._checkAllIterators(p, test, rid)


    def testIterators_09_BadParameters_01(self):
        self.assertRaises(TypeError, lambda: TreeDict().iterkeys(branch_mode = "bork"))
        self.assertRaises(TypeError, lambda: TreeDict().iteritems(branch_mode = "bork"))
        self.assertRaises(TypeError, lambda: TreeDict().itervalues(branch_mode = "bork"))

    def testIterators_09_BadParameters_02(self):
        self.assertRaises(TypeError, lambda: TreeDict().itervalues(branch_mode = 1))
        self.assertRaises(TypeError, lambda: TreeDict().iteritems(branch_mode = 1))
        self.assertRaises(TypeError, lambda: TreeDict().itervalues(branch_mode = 1))


    def _check_RTE(self, keys, recursive, branch_mode, mode):

        p = TreeDict()

        for k in keys:
            p[k] = 1
            
        # Get a list of what will occur next 
        key_list = p.keys(recursive, branch_mode)

        def test_it(action, isokay = False):
            for ret_mode in ["keys", "items"]:
        
                def f():
                    n = p.size(recursive, branch_mode)

                    if ret_mode == "keys":
                        kiter = p.iterkeys(recursive, branch_mode)
                        for i, t in enumerate(kiter):
                            action(i, n, t)

                    if ret_mode == "items":
                        iiter = p.iteritems(recursive, branch_mode)
                        for i, (t,v) in enumerate(iiter):
                            action(i, n, t)

                if isokay:
                    f()
                else:
                    if p.size(recursive, branch_mode) != 0:
                        self.assertRaises(RuntimeError, f)
            
        if mode == "delete_all":
            def action(i,n,t):
                del p[t]

            test_it(action)

        if mode == "delete_last":
            def action(i,n,t):
                if i == n-1:
                    del p[t]

            test_it(action, True)

        if mode == "insert_each":
            def action(i,n,t):
                tn = unique_name()
                p[tn] = 1

            test_it(action)

        if mode == "insert_last":
            def action(i,n,t):
                if i == n-1:
                    tn = unique_name()
                    p[tn] = 1

            test_it(action, True)
            
        if mode == "insert_middle":
            def action(i,n,t):
                if i >= n // 2:
                    tn = unique_name()
                    p[tn] = 1

            test_it(action)

        if mode == "attach_branch":
            np = TreeDict(unique_name())
            np.a.b.c = 1
        
            def action(i,n,t):
                if i == n//2:
                    p.attach(np)
                    
            test_it(action)

        if mode == "attach_recursive":
            np = TreeDict(unique_name())
            np.a.b.c = 1
            p.attach(np)

            def action(i,n,t):
                if i == n//2:
                    p.attach(recursive=True)

            test_it(action)

        if mode == "pop":
            def action(i,n,t):
                if i == n//2:
                    p.pop(key_list[i+1])

            test_it(action)

        if mode == "clear":
            def action(i,n,t):
                if i == n//2:
                    p.clear()
            test_it(action)

        if mode == "freeze":
            # should not raise error
            def action(i,n,t):
                if i == n//2:
                    p.freeze()
            test_it(action, True)

        if mode == "copy":
            # should not raise error
            def action(i,n,t):
                if i == n//2:
                    pn = p.copy()
            test_it(action, True)

        if mode == "branch":
            def action(i,n,t):
                if i == n//2:
                    b = p.makeBranch(unique_name())
            test_it(action)

        if mode == "size_called":
            # should not raise error
            def action(i,n,t):
                if i == n//2:
                    s = p.size()
            test_it(action, True)

        if mode == "nested_iter":

            # should not raise error
            def action(i,n,t):
                if i == n//2:
                    for k in p.iterkeys():
                        for v in p.itervalues():
                            pass
                            
            test_it(action, True)

            # Now verify all are okay
            #print "p._iteratorRefCount() =", p._iteratorRefCount()
            p.asdfasdfafds = None

        if mode == "nested_iter_bad":
            # should not raise error
            def action(i,n,t):
                if i == n//2:
                    for k in p.iterkeys():
                        for v in p.itervalues():
                            pass

                    del p[key_list[i+1]]  # Make sure the flag is not turned off

            test_it(action)

            # Now verify all are okay
            #print "p._iteratorRefCount() =", p._iteratorRefCount()
            p.asdfasdfafds = None


        if mode == "nested_iter_bad_later":
            # should not raise error
            def action(i,n,t):
                if i == 0:
                    for k in p.iterkeys():
                        for v in p.itervalues():
                            pass
                else:
                    del p[t]  # Make sure the flag is not turned off

            test_it(action)

        if mode == "nested_list":
            # should not raise error
            def action(i,n,t):
                if i == n//2:
                    p.keys()
                            
            test_it(action, True)

        if mode == "nested_list_bad":
            def action(i,n,t):
                assert key_list[i] == t
                
                if i == n//2:
                    k = p.keys()

                    del p[key_list[i+1]]  # Make sure the flag is not turned off

            test_it(action)

        if mode == "nested_list_bad_later":
            def action(i,n,t):
                if i == 0:
                    k = p.keys()
                else:
                    del p[t]  # Make sure the flag is not turned off

            test_it(action)

        if mode == "action_on_subbranches_okay":
            tn = unique_name()

            p[tn +'.a'] = 1
            p[tn +'.b'] = 1
            p[tn +'.c'] = 1

            has_seen_tn = [False]

            def action(i,n,t):
                if i == 0: 
                    has_seen_tn[0] = False

                if t.startswith(tn):
                    has_seen_tn[0] = True

                if (not t.startswith(tn)) and has_seen_tn[0]:
                    p[tn].pop('a')
                    p[tn].a = 1

            test_it(action, True)

        if mode == "action_on_subbranches_okay_control":
            tn = unique_name()

            p[tn +'.a'] = 1
            p[tn +'.b'] = 1
            p[tn +'.c'] = 1

            def action(i,n,t):
                if t.startswith(tn):
                    p[tn].pop('a')
                    p[tn].a = 1

            test_it(action)


    # Tests for the simpler cases
    def testIterators_10_ChangeRaisesRuntimeError_a_01(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "delete_all")
    def testIterators_10_ChangeRaisesRuntimeError_a_02(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "delete_last")
    def testIterators_10_ChangeRaisesRuntimeError_a_03(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "insert_each")
    def testIterators_10_ChangeRaisesRuntimeError_a_04(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "insert_last")
    def testIterators_10_ChangeRaisesRuntimeError_a_05(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "insert_middle")
    def testIterators_10_ChangeRaisesRuntimeError_a_06(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "attach_branch")
    def testIterators_10_ChangeRaisesRuntimeError_a_07(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "attach_recursive")
    def testIterators_10_ChangeRaisesRuntimeError_a_08(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "pop")
    def testIterators_10_ChangeRaisesRuntimeError_a_09(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "clear")
    def testIterators_10_ChangeRaisesRuntimeError_a_10(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "freeze")
    def testIterators_10_ChangeRaisesRuntimeError_a_11(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "copy")
    def testIterators_10_ChangeRaisesRuntimeError_a_12(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "branch")
    def testIterators_10_ChangeRaisesRuntimeError_a_13(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "size_called")
    def testIterators_10_ChangeRaisesRuntimeError_a_14(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "nested_iter")
    def testIterators_10_ChangeRaisesRuntimeError_a_15(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "nested_iter_bad")
    def testIterators_10_ChangeRaisesRuntimeError_a_16(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "nested_iter_bad_later")
    def testIterators_10_ChangeRaisesRuntimeError_a_17(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "nested_list")
    def testIterators_10_ChangeRaisesRuntimeError_a_18(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "nested_list_bad")
    def testIterators_10_ChangeRaisesRuntimeError_a_19(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "nested_list_bad_later")
    def testIterators_10_ChangeRaisesRuntimeError_a_20(self):
        self._check_RTE(['a', 'b', 'c'], False, "all", "action_on_subbranches_okay")


    # Tests for the much more complex cases

    big_key_list = random_node_list(10, 100, 0.5)
    def testIterators_11_ChangeRaisesRuntimeError_a_01(self):
        self._check_RTE(self.big_key_list, False, "all", "delete_all")
    def testIterators_11_ChangeRaisesRuntimeError_a_02(self):
        self._check_RTE(self.big_key_list, False, "all", "delete_last")
    def testIterators_11_ChangeRaisesRuntimeError_a_03(self):
        self._check_RTE(self.big_key_list, False, "all", "insert_each")
    def testIterators_11_ChangeRaisesRuntimeError_a_04(self):
        self._check_RTE(self.big_key_list, False, "all", "insert_last")
    def testIterators_11_ChangeRaisesRuntimeError_a_05(self):
        self._check_RTE(self.big_key_list, False, "all", "insert_middle")
    def testIterators_11_ChangeRaisesRuntimeError_a_06(self):
        self._check_RTE(self.big_key_list, False, "all", "attach_branch")
    def testIterators_11_ChangeRaisesRuntimeError_a_07(self):
        self._check_RTE(self.big_key_list, False, "all", "attach_recursive")
    def testIterators_11_ChangeRaisesRuntimeError_a_08(self):
        self._check_RTE(self.big_key_list, False, "all", "pop")
    def testIterators_11_ChangeRaisesRuntimeError_a_09(self):
        self._check_RTE(self.big_key_list, False, "all", "clear")
    def testIterators_11_ChangeRaisesRuntimeError_a_10(self):
        self._check_RTE(self.big_key_list, False, "all", "freeze")
    def testIterators_11_ChangeRaisesRuntimeError_a_11(self):
        self._check_RTE(self.big_key_list, False, "all", "copy")
    def testIterators_11_ChangeRaisesRuntimeError_a_12(self):
        self._check_RTE(self.big_key_list, False, "all", "branch")
    def testIterators_11_ChangeRaisesRuntimeError_a_13(self):
        self._check_RTE(self.big_key_list, False, "all", "size_called")
    def testIterators_11_ChangeRaisesRuntimeError_a_14(self):
        self._check_RTE(self.big_key_list, False, "all", "nested_iter")
    def testIterators_11_ChangeRaisesRuntimeError_a_15(self):
        self._check_RTE(self.big_key_list, False, "all", "nested_iter_bad")
    def testIterators_11_ChangeRaisesRuntimeError_a_16(self):
        self._check_RTE(self.big_key_list, False, "all", "nested_iter_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_a_17(self):
        self._check_RTE(self.big_key_list, False, "all", "nested_list")
    def testIterators_11_ChangeRaisesRuntimeError_a_18(self):
        self._check_RTE(self.big_key_list, False, "all", "nested_list_bad")
    def testIterators_11_ChangeRaisesRuntimeError_a_19(self):
        self._check_RTE(self.big_key_list, False, "all", "nested_list_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_a_20(self):
        self._check_RTE(self.big_key_list, False, "all", "action_on_subbranches_okay")

    # different recursive modes
    def testIterators_11_ChangeRaisesRuntimeError_b_01(self):
        self._check_RTE(self.big_key_list, True, "all", "delete_all")
    def testIterators_11_ChangeRaisesRuntimeError_b_02(self):
        self._check_RTE(self.big_key_list, True, "all", "delete_last")
    def testIterators_11_ChangeRaisesRuntimeError_b_03(self):
        self._check_RTE(self.big_key_list, True, "all", "insert_each")
    def testIterators_11_ChangeRaisesRuntimeError_b_04(self):
        self._check_RTE(self.big_key_list, True, "all", "insert_last")
    def testIterators_11_ChangeRaisesRuntimeError_b_05(self):
        self._check_RTE(self.big_key_list, True, "all", "insert_middle")
    def testIterators_11_ChangeRaisesRuntimeError_b_06(self):
        self._check_RTE(self.big_key_list, True, "all", "attach_branch")
    def testIterators_11_ChangeRaisesRuntimeError_b_07(self):
        self._check_RTE(self.big_key_list, True, "all", "attach_recursive")
    def testIterators_11_ChangeRaisesRuntimeError_b_08(self):
        self._check_RTE(self.big_key_list, True, "all", "pop")
    def testIterators_11_ChangeRaisesRuntimeError_b_09(self):
        self._check_RTE(self.big_key_list, True, "all", "clear")
    def testIterators_11_ChangeRaisesRuntimeError_b_10(self):
        self._check_RTE(self.big_key_list, True, "all", "freeze")
    def testIterators_11_ChangeRaisesRuntimeError_b_11(self):
        self._check_RTE(self.big_key_list, True, "all", "copy")
    def testIterators_11_ChangeRaisesRuntimeError_b_12(self):
        self._check_RTE(self.big_key_list, True, "all", "branch")
    def testIterators_11_ChangeRaisesRuntimeError_b_13(self):
        self._check_RTE(self.big_key_list, True, "all", "size_called")
    def testIterators_11_ChangeRaisesRuntimeError_b_14(self):
        self._check_RTE(self.big_key_list, True, "all", "nested_iter")
    def testIterators_11_ChangeRaisesRuntimeError_b_15(self):
        self._check_RTE(self.big_key_list, True, "all", "nested_iter_bad")
    def testIterators_11_ChangeRaisesRuntimeError_b_16(self):
        self._check_RTE(self.big_key_list, True, "all", "nested_iter_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_b_17(self):
        self._check_RTE(self.big_key_list, True, "all", "nested_list")
    def testIterators_11_ChangeRaisesRuntimeError_b_18(self):
        self._check_RTE(self.big_key_list, True, "all", "nested_list_bad")
    def testIterators_11_ChangeRaisesRuntimeError_b_19(self):
        self._check_RTE(self.big_key_list, True, "all", "nested_list_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_b_20(self):
        self._check_RTE(self.big_key_list, True, "all", "action_on_subbranches_okay")
    def testIterators_11_ChangeRaisesRuntimeError_b_21(self):
        self._check_RTE(self.big_key_list, True, "all", "action_on_subbranches_okay_control")

    # Testing different combinations; easy to do here, but maybe overkill
    def testIterators_11_ChangeRaisesRuntimeError_c_01(self):
        self._check_RTE(self.big_key_list, False, "only", "delete_all")
    def testIterators_11_ChangeRaisesRuntimeError_c_02(self):
        self._check_RTE(self.big_key_list, False, "only", "delete_last")
    def testIterators_11_ChangeRaisesRuntimeError_c_03(self):
        self._check_RTE(self.big_key_list, False, "only", "insert_each")
    def testIterators_11_ChangeRaisesRuntimeError_c_04(self):
        self._check_RTE(self.big_key_list, False, "only", "insert_last")
    def testIterators_11_ChangeRaisesRuntimeError_c_05(self):
        self._check_RTE(self.big_key_list, False, "only", "insert_middle")
    def testIterators_11_ChangeRaisesRuntimeError_c_06(self):
        self._check_RTE(self.big_key_list, False, "only", "attach_branch")
    def testIterators_11_ChangeRaisesRuntimeError_c_07(self):
        self._check_RTE(self.big_key_list, False, "only", "attach_recursive")
    def testIterators_11_ChangeRaisesRuntimeError_c_08(self):
        self._check_RTE(self.big_key_list, False, "only", "pop")
    def testIterators_11_ChangeRaisesRuntimeError_c_09(self):
        self._check_RTE(self.big_key_list, False, "only", "clear")
    def testIterators_11_ChangeRaisesRuntimeError_c_10(self):
        self._check_RTE(self.big_key_list, False, "only", "freeze")
    def testIterators_11_ChangeRaisesRuntimeError_c_11(self):
        self._check_RTE(self.big_key_list, False, "only", "copy")
    def testIterators_11_ChangeRaisesRuntimeError_c_12(self):
        self._check_RTE(self.big_key_list, False, "only", "branch")
    def testIterators_11_ChangeRaisesRuntimeError_c_13(self):
        self._check_RTE(self.big_key_list, False, "only", "size_called")
    def testIterators_11_ChangeRaisesRuntimeError_c_14(self):
        self._check_RTE(self.big_key_list, False, "only", "nested_iter")
    def testIterators_11_ChangeRaisesRuntimeError_c_15(self):
        self._check_RTE(self.big_key_list, False, "only", "nested_iter_bad")
    def testIterators_11_ChangeRaisesRuntimeError_c_16(self):
        self._check_RTE(self.big_key_list, False, "only", "nested_iter_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_c_17(self):
        self._check_RTE(self.big_key_list, False, "only", "nested_list")
    def testIterators_11_ChangeRaisesRuntimeError_c_18(self):
        self._check_RTE(self.big_key_list, False, "only", "nested_list_bad")
    def testIterators_11_ChangeRaisesRuntimeError_c_19(self):
        self._check_RTE(self.big_key_list, False, "only", "nested_list_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_c_20(self):
        self._check_RTE(self.big_key_list, False, "only", "action_on_subbranches_okay")

    # different recursive modes
    def testIterators_11_ChangeRaisesRuntimeError_d_01(self):
        self._check_RTE(self.big_key_list, True, "only", "delete_all")
    def testIterators_11_ChangeRaisesRuntimeError_d_02(self):
        self._check_RTE(self.big_key_list, True, "only", "delete_last")
    def testIterators_11_ChangeRaisesRuntimeError_d_03(self):
        self._check_RTE(self.big_key_list, True, "only", "insert_each")
    def testIterators_11_ChangeRaisesRuntimeError_d_04(self):
        self._check_RTE(self.big_key_list, True, "only", "insert_last")
    def testIterators_11_ChangeRaisesRuntimeError_d_05(self):
        self._check_RTE(self.big_key_list, True, "only", "insert_middle")
    def testIterators_11_ChangeRaisesRuntimeError_d_06(self):
        self._check_RTE(self.big_key_list, True, "only", "attach_branch")
    def testIterators_11_ChangeRaisesRuntimeError_d_07(self):
        self._check_RTE(self.big_key_list, True, "only", "attach_recursive")
    def testIterators_11_ChangeRaisesRuntimeError_d_08(self):
        self._check_RTE(self.big_key_list, True, "only", "pop")
    def testIterators_11_ChangeRaisesRuntimeError_d_09(self):
        self._check_RTE(self.big_key_list, True, "only", "clear")
    def testIterators_11_ChangeRaisesRuntimeError_d_10(self):
        self._check_RTE(self.big_key_list, True, "only", "freeze")
    def testIterators_11_ChangeRaisesRuntimeError_d_11(self):
        self._check_RTE(self.big_key_list, True, "only", "copy")
    def testIterators_11_ChangeRaisesRuntimeError_d_12(self):
        self._check_RTE(self.big_key_list, True, "only", "branch")
    def testIterators_11_ChangeRaisesRuntimeError_d_13(self):
        self._check_RTE(self.big_key_list, True, "only", "size_called")
    def testIterators_11_ChangeRaisesRuntimeError_d_14(self):
        self._check_RTE(self.big_key_list, True, "only", "nested_iter")
    def testIterators_11_ChangeRaisesRuntimeError_d_15(self):
        self._check_RTE(self.big_key_list, True, "only", "nested_iter_bad")
    def testIterators_11_ChangeRaisesRuntimeError_d_16(self):
        self._check_RTE(self.big_key_list, True, "only", "nested_iter_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_d_17(self):
        self._check_RTE(self.big_key_list, True, "only", "nested_list")
    def testIterators_11_ChangeRaisesRuntimeError_d_18(self):
        self._check_RTE(self.big_key_list, True, "only", "nested_list_bad")
    def testIterators_11_ChangeRaisesRuntimeError_d_19(self):
        self._check_RTE(self.big_key_list, True, "only", "nested_list_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_d_20(self):
        self._check_RTE(self.big_key_list, True, "only", "action_on_subbranches_okay")


    # Testing different combinations; easy to do here, but maybe overkill
    def testIterators_11_ChangeRaisesRuntimeError_e_01(self):
        self._check_RTE(self.big_key_list, False, "none", "delete_all")
    def testIterators_11_ChangeRaisesRuntimeError_e_02(self):
        self._check_RTE(self.big_key_list, False, "none", "delete_last")
    def testIterators_11_ChangeRaisesRuntimeError_e_03(self):
        self._check_RTE(self.big_key_list, False, "none", "insert_each")
    def testIterators_11_ChangeRaisesRuntimeError_e_04(self):
        self._check_RTE(self.big_key_list, False, "none", "insert_last")
    def testIterators_11_ChangeRaisesRuntimeError_e_05(self):
        self._check_RTE(self.big_key_list, False, "none", "insert_middle")
    def testIterators_11_ChangeRaisesRuntimeError_e_06(self):
        self._check_RTE(self.big_key_list, False, "none", "attach_branch")
    def testIterators_11_ChangeRaisesRuntimeError_e_07(self):
        self._check_RTE(self.big_key_list, False, "none", "attach_recursive")
    def testIterators_11_ChangeRaisesRuntimeError_e_08(self):
        self._check_RTE(self.big_key_list, False, "none", "pop")
    def testIterators_11_ChangeRaisesRuntimeError_e_09(self):
        self._check_RTE(self.big_key_list, False, "none", "clear")
    def testIterators_11_ChangeRaisesRuntimeError_e_10(self):
        self._check_RTE(self.big_key_list, False, "none", "freeze")
    def testIterators_11_ChangeRaisesRuntimeError_e_11(self):
        self._check_RTE(self.big_key_list, False, "none", "copy")
    def testIterators_11_ChangeRaisesRuntimeError_e_12(self):
        self._check_RTE(self.big_key_list, False, "none", "branch")
    def testIterators_11_ChangeRaisesRuntimeError_e_13(self):
        self._check_RTE(self.big_key_list, False, "none", "size_called")
    def testIterators_11_ChangeRaisesRuntimeError_e_14(self):
        self._check_RTE(self.big_key_list, False, "none", "nested_iter")
    def testIterators_11_ChangeRaisesRuntimeError_e_15(self):
        self._check_RTE(self.big_key_list, False, "none", "nested_iter_bad")
    def testIterators_11_ChangeRaisesRuntimeError_e_16(self):
        self._check_RTE(self.big_key_list, False, "none", "nested_iter_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_e_17(self):
        self._check_RTE(self.big_key_list, False, "none", "nested_list")
    def testIterators_11_ChangeRaisesRuntimeError_e_18(self):
        self._check_RTE(self.big_key_list, False, "none", "nested_list_bad")
    def testIterators_11_ChangeRaisesRuntimeError_e_19(self):
        self._check_RTE(self.big_key_list, False, "none", "nested_list_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_e_20(self):
        self._check_RTE(self.big_key_list, False, "none", "action_on_subbranches_okay")

    # different recursive modes
    def testIterators_11_ChangeRaisesRuntimeError_f_01(self):
        self._check_RTE(self.big_key_list, True, "none", "delete_all")
    def testIterators_11_ChangeRaisesRuntimeError_f_02(self):
        self._check_RTE(self.big_key_list, True, "none", "delete_last")
    def testIterators_11_ChangeRaisesRuntimeError_f_03(self):
        self._check_RTE(self.big_key_list, True, "none", "insert_each")
    def testIterators_11_ChangeRaisesRuntimeError_f_04(self):
        self._check_RTE(self.big_key_list, True, "none", "insert_last")
    #def testIterators_11_ChangeRaisesRuntimeError_f_05(self):
    #    self._check_RTE(self.big_key_list, True, "none", "insert_middle")
    # Disabled cause it's stupid there
    def testIterators_11_ChangeRaisesRuntimeError_f_06(self):
        self._check_RTE(self.big_key_list, True, "none", "attach_branch")
    def testIterators_11_ChangeRaisesRuntimeError_f_07(self):
        self._check_RTE(self.big_key_list, True, "none", "attach_recursive")
    def testIterators_11_ChangeRaisesRuntimeError_f_08(self):
        self._check_RTE(self.big_key_list, True, "none", "pop")
    def testIterators_11_ChangeRaisesRuntimeError_f_09(self):
        self._check_RTE(self.big_key_list, True, "none", "clear")
    def testIterators_11_ChangeRaisesRuntimeError_f_10(self):
        self._check_RTE(self.big_key_list, True, "none", "freeze")
    def testIterators_11_ChangeRaisesRuntimeError_f_11(self):
        self._check_RTE(self.big_key_list, True, "none", "copy")
    def testIterators_11_ChangeRaisesRuntimeError_f_12(self):
        self._check_RTE(self.big_key_list, True, "none", "branch")
    def testIterators_11_ChangeRaisesRuntimeError_f_13(self):
        self._check_RTE(self.big_key_list, True, "none", "size_called")
    def testIterators_11_ChangeRaisesRuntimeError_f_14(self):
        self._check_RTE(self.big_key_list, True, "none", "nested_iter")
    def testIterators_11_ChangeRaisesRuntimeError_f_15(self):
        self._check_RTE(self.big_key_list, True, "none", "nested_iter_bad")
    def testIterators_11_ChangeRaisesRuntimeError_f_16(self):
        self._check_RTE(self.big_key_list, True, "none", "nested_iter_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_f_17(self):
        self._check_RTE(self.big_key_list, True, "none", "nested_list")
    def testIterators_11_ChangeRaisesRuntimeError_f_18(self):
        self._check_RTE(self.big_key_list, True, "none", "nested_list_bad")
    def testIterators_11_ChangeRaisesRuntimeError_f_19(self):
        self._check_RTE(self.big_key_list, True, "none", "nested_list_bad_later")
    def testIterators_11_ChangeRaisesRuntimeError_f_20(self):
        self._check_RTE(self.big_key_list, True, "none", "action_on_subbranches_okay")

    # Need to add tests for trees changing on operations that fail b/c
    # of iterator locking?


    def testIterators_12_Deletion(self):
        p = TreeDict()

        p.a = 1
        p.b = 2
        p.c = 3
        p.d = 4 
        p.e = 5

        it = p.iterkeys()
        
        self.assertRaises(RuntimeError, lambda: p.pop('a'))
        it.next()
        self.assertRaises(RuntimeError, lambda: p.pop('a'))
        
        del it

        p.pop('a')


    def testIterators_13_Large(self):

        n_iter = 300
        n_node = 300

        tml = random_node_list(122, n_node, 0.75)

        random.seed(0)

        p = TreeDict()
        
        p.update(dict((t, 1) for t in tml))

        # set up a list of iterators
        def newIter():
            recursive = random.random() < 0.7
            brv = random.random()
            if 0 <= brv <= 0.33:
                branch_mode = "all"
            elif 0.33 < brv <= 0.66:
                branch_mode = "only"
            else:
                branch_mode = "none"

            irv = random.random()
            if 0 <= brv <= 0.33:
                return p.iterkeys(recursive, branch_mode)
            elif 0.33 < brv <= 0.66:
                return p.itervalues(recursive, branch_mode)
            else:
                return p.iteritems(recursive, branch_mode)

        iter_list = [newIter() for i in xrange(n_iter)]

        while len(iter_list) > 0:

            del_queue = []

            for i, it in enumerate(iter_list):
                try:
                    it.next()
                except StopIteration:
                    self.assert_(p._iteratorRefCount() <= len(iter_list))
                    del_queue.append(i)

            for i in sorted(del_queue, reverse=True):
                del iter_list[i]

        # Now make sure that everything is cool
        self.assert_(p._iteratorRefCount() == 0, p._iteratorRefCount())

        for tm in tml:
            p.pop(tm)


    ########################################
    # The corresponding tests for values

    def testItemlists_01_flat(self):
        p = TreeDict()
        items = [('a', 1), ('b', 2), ('c', 3)]

        p.set(**dict(items))
 
        self.assert_(set(p.keys())   == set([k for k, v in items]))
        self.assert_(set(p.values()) == set([v for k, v in items]))
        self.assert_(set(p.items())  == set(items))
        
        
    def testItemlists_02_recursive(self):

        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        self.assert_(set(p.keys())   == set([k for k, v in items]))
        self.assert_(set(p.values()) == set([v for k, v in items]))
        self.assert_(set(p.items())  == set(items))
        

    def testItemlists_03_nonrecursive_skipbranches(self):

        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        non_recursive = [(k,v) for k, v in items
                         if '.' not in k]

        self.assert_(set(p.keys(recursive=False)) 
                         == set([k for k, v in non_recursive]))
        self.assert_(set(p.values(recursive=False))
                         == set([v for k, v in non_recursive]))
        self.assert_(set(p.items(recursive=False))
                         == set(non_recursive))

    def testItemlists_04_nonrecursive_withbranches(self):

        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        nrwb  = [(k, p.get(k)) for k in ['a', 'b', 'c', 'aa']]

        p.freeze()

        self.assert_(set(p.keys(recursive=False, branch_mode = "all"))
                     == set([k for k, v in nrwb]))
        self.assert_(set(p.values(recursive=False, branch_mode = "all"))
                     == set([v for k, v in nrwb]))
        self.assert_(set(p.items(recursive=False, branch_mode = "all"))
                     == set(nrwb))
 
    def testItemlists_05_branches(self):

        p = TreeDict()
        items = [('a.v', 1), ('b', 2), ('c', 3), ('aa.b.c.d.e', 4)]

        p.set(**dict(items))

        bl  = [(k, p.get(k)) for k in ['a', 'aa']]

        p.freeze()

        self.assert_(set(p.values(False, "only")) == set([v for k, v in bl]))
        self.assert_(set(p.keys(False, "only")) == set([k for k, v in bl]))
        self.assert_(set(p.items(False, "only")) == set(bl))

    def testItemLists_06_single_deep(self):
        depth = 500
        p = TreeDict()

        pt = p
        for i in range(depth-1):
            pt = pt.a

        pt.a = 1

        self.assert_(p.keys() == ['.'.join(['a']*depth)])
        self.assert_(p.values() == [1])

    def testItemLists_07_empty_rn(self):
        
        p = TreeDict()
        self.assert_(p.keys(True, "none") == [])
        self.assert_(p.items(True, "none") == [])
        self.assert_(p.values(True, "none") == [])

    def testItemLists_07_empty_ra(self):
        
        p = TreeDict()
        self.assert_(p.keys(True, "all") == [])
        self.assert_(p.items(True, "all") == [])
        self.assert_(p.values(True, "all") == [])

    def testItemLists_07_empty_ro(self):
        
        p = TreeDict()
        self.assert_(p.keys(True, "only") == [])
        self.assert_(p.items(True, "only") == [])
        self.assert_(p.values(True, "only") == [])

    def testItemLists_07_empty_fn(self):
        
        p = TreeDict()
        self.assert_(p.keys(False, "none") == [])
        self.assert_(p.items(False, "none") == [])
        self.assert_(p.values(False, "none") == [])

    def testItemLists_07_empty_fa(self):
        
        p = TreeDict()
        self.assert_(p.keys(False, "all") == [])
        self.assert_(p.items(False, "all") == [])
        self.assert_(p.values(False, "all") == [])

    def testItemLists_07_empty_fo(self):
        
        p = TreeDict()
        self.assert_(p.keys(False, "only") == [])
        self.assert_(p.items(False, "only") == [])
        self.assert_(p.values(False, "only") == [])


    def _checkAllItemLists(self, p, test, rid):

        self.assert_(set(l for l in p.keys(*test)) 
                     == set(k for k,v in rid[test]))

        self.assert_(set(l for l in p.items(*test))
                     == rid[test])

        self.assert_(set(l for l in p.values(*test))
                     == set(v for k,v in rid[test]))


    def testItemLists_08_basic_walking_test__rn(self):

        p, rid = basic_walking_test()
        test = (True, "none")
        self._checkAllItemLists(p, test, rid)

    def testItemLists_08_basic_walking_test__ra(self):

        p, rid = basic_walking_test()
        test = (True, "all")
        self._checkAllItemLists(p, test, rid)

    def testItemLists_08_basic_walking_test__ro(self):

        p, rid = basic_walking_test()
        test = (True, "only")
        self._checkAllItemLists(p, test, rid)

    def testItemLists_08_basic_walking_test__fn(self):

        p, rid = basic_walking_test()
        test = (False, "none")
        self._checkAllItemLists(p, test, rid)

    def testItemLists_08_basic_walking_test__fa(self):

        p, rid = basic_walking_test()
        test = (False, "all")
        self._checkAllItemLists(p, test, rid)

    def testItemLists_08_basic_walking_test__fo(self):

        p, rid = basic_walking_test()
        test = (False, "only")
        self._checkAllItemLists(p, test, rid)

    def testItemLists_09_BadParameters_01(self):
        self.assertRaises(TypeError, lambda: TreeDict().keys(branch_mode = "bork"))
        self.assertRaises(TypeError, lambda: TreeDict().items(branch_mode = "bork"))
        self.assertRaises(TypeError, lambda: TreeDict().values(branch_mode = "bork"))

    def testItemLists_09_BadParameters_02(self):
        self.assertRaises(TypeError, lambda: TreeDict().values(branch_mode = 1))
        self.assertRaises(TypeError, lambda: TreeDict().items(branch_mode = 1))
        self.assertRaises(TypeError, lambda: TreeDict().values(branch_mode = 1))



if __name__ == '__main__':
    unittest.main()

