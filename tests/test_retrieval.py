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

from hashlib import md5
import random

from treedict.treedict import _ldist

from common import *

class TestRetrieval(unittest.TestCase):
       
    def test_existance_01(self):
        p = sample_tree()
        self.assert_("123" not in p)
        self.assert_(not p.has_key("123"))

    def test_existance_02(self):
        p = sample_tree()
        self.assert_(123 not in p)
        self.assert_(not p.has_key(123))

    def test_existance_03(self):
        p = sample_tree()
        self.assert_(None not in p)
        self.assert_(not p.has_key(None))

    def test_existance_04(self):
        p = sample_tree()
        self.assert_("si3dkdkdmmd" not in p)
        self.assert_(not p.has_key("si3dkdkdmmd"))

    def test_existance_05(self):
        p = sample_tree()
        self.assert_(p not in p)
        self.assert_(not p.has_key(p))


    def test_existance_06_dangling_node(self):
        p = TreeDict('roor')
        p.a

        self.assert_('a' not in p)

    def test_existance_06b_dangling_node(self):
        p = TreeDict('roor')

        p.b = 123
        p.a

        self.assert_('b' in p)
        self.assert_('a' not in p)

    def test_existance_06c_dangling_node(self):
        p = TreeDict('roor')

        p.b = 123
        p.a
        p.aa.b.c
        p.bb.c.d = None

        self.assert_('a' not in p)
        self.assert_('b' in p)
        self.assert_('aa' not in p)
        self.assert_('bb' in p)

    def testExistanceThroughLink(self):
        p = TreeDict()
        p.a.b.link = p.d
        p.d.v = 1
        
        self.assert_('a.b.link.v' in p)
            
    def testContains_01(self):
        p1 = TreeDict()
        p1.a.b = 123
        
        self.assert_('a' in p1)
        self.assert_('a.b' in p1)
        self.assert_('b' not in p1)
        self.assert_('b' in p1.a)


    def testContains_02(self):
        p1 = TreeDict()
        p1.a.b = 123
        p1.d
        
        self.assert_('a' in p1)
        self.assert_('a.b' in p1)
        self.assert_('d' not in p1)

    def testForwardReference(self):
        p = TreeDict('test')

        p.a.b.c = p.d.e.f

        p.d.e.f.g = 10

        self.assert_(p.a.b.c.g == 10)

    def testDefaultValue_01(self):
        p = TreeDict()
        p.a.b = 123

        self.assert_(p.get('a.b') == 123)
        self.assert_(p.get('a.b', default_value = 1) == 123)
        self.assert_(p.get('a.c', default_value = 1) == 1)
        self.assert_(p.get('a.c', default_value = None) is None)        


    def testRetrieve_01_NonExistantBranchFromFrozenTree(self):
        p = TreeDict()
        p.a.b.c = 1
        p.freeze()

        self.assert_(p.a.b.c == 1)

        self.assertRaises(AttributeError, lambda: p.a.d)

    def testRetrieve_02_NonExistantBranchFromFrozenTree_control(self):
        p = TreeDict()
        p.a.b.c = 1
        # control; no freeze

        self.assert_(p.a.b.c == 1)
        
        p.a.d

    def testRetrieve_03_ThroughLink(self):
        p = TreeDict()
        p.a.b.link = p.d
        p.d.v = 1

        self.assert_(p["a.b.link.v"] == 1)
        self.assert_(p.get("a.b.link.v") == 1)

    def testRetrieve_04_ThroughMultipleLinks(self):
        p = TreeDict()

        p.l7.v = 1

        p.l6 = p.l7
        p.l5 = p.l6
        p.l4 = p.l5
        p.l3 = p.l4
        p.l2 = p.l3
        p.l1 = p.l2

        self.assert_(p.l7.v == 1)
        self.assert_(p.l6.v == 1)
        self.assert_(p.l5.v == 1)
        self.assert_(p.l4.v == 1)
        self.assert_(p.l3.v == 1)
        self.assert_(p.l2.v == 1)
        self.assert_(p.l1.v == 1)

    def testNonexistantValues_01(self):

        p = TreeDict()
        self.assertRaises(KeyError, lambda: p["a"])

    def testNonexistantValues_02(self):

        p = TreeDict()
        self.assertRaises(KeyError, lambda: p[0])

    def testNonexistantValues_03(self):

        p = TreeDict()
        self.assertRaises(KeyError, lambda: p[None])

    def testNonexistantValues_04(self):

        p = TreeDict()
        p.freeze()
        self.assertRaises(AttributeError, lambda: p.a)

    ##################################################
    # Some of the format specifying stuff

    def testConvertTo_01(self):
        
        t = TreeDict()
        t.z = 3
        t.a.x = 1
        t.a.y = 2

        # Test default
        self.assert_(t.convertTo() == t.convertTo('nested_dict'))
        
        self.assert_(t.convertTo() == {'a' : {'x' : 1, 'y' : 2}, 'z' : 3})

    def testConvertTo_02(self):

        t = random_tree(200)
        d = t.convertTo('nested_dict')
        t2 = TreeDict.fromdict(d, expand_nested = True)
        self.assert_(t == t2)

    def testConvertTo_03_self_linked_01(self):

        t = TreeDict()
        t.makeBranch('b')
        t.a.b = t.b
        t.b.a = t.a

        d = t.convertTo('nested_dict')

        self.assert_(type(d['a']) is dict)
        self.assert_(type(d['b']) is dict)
        
        self.assert_(d['a']['b'] is d['b'])
        self.assert_(d['b']['a'] is d['a'])

    def testConvertTo_03_self_linked_02(self):

        t = random_selflinked_tree(0, 1)
        d = t.convertTo('nested_dict')
        t2 = TreeDict.fromdict(d, expand_nested = True)

        t.attach(recursive = True)
        t2.attach(recursive = True)

        self.assert_(t == t2)

    def testConvertTo_04_root_linked_01(self):

        t = TreeDict()
        t.a = t

        d = t.convertTo('nested_dict')

        self.assert_(d['a'] is d)

    def testConvertTo_04_root_linked_02(self):

        t = TreeDict()
        t.a.b.c = t
        t.a.b.x = t.a

        d = t.convertTo('nested_dict')

        self.assert_(d['a']['b']['c'] is d)
        self.assert_(d['a']['b']['x'] is d['a'])


    def testConvertTo_05_only_local_as_values_01(self):

        t = TreeDict()

        t.x.y = 1
        t.a.b.c = 1
        t.a.b.d = t.a.b
        t.a.b.xl = t.x
        t.a.xl = t.x

        d = t.a.convertTo('nested_dict', convert_values = False)
        
        self.assert_(type(d['b']['d']) is dict)
        self.assert_(type(d['b']) is dict)
        self.assert_(d['b'] is d['b']['d'])
        self.assert_(d['b']['c'] == 1)

        # TreeDict values are only converted if they are a branch somewhere in the 
        self.assert_(type(d['b']['xl']) is TreeDict)
        self.assert_(type(d['xl']) is TreeDict)
        self.assert_(d['xl'] is d['b']['xl'])

    def testConvertTo_05_only_local_as_values_01_control(self):

        t = TreeDict()

        t.x.y = 1
        t.a.b.c = 1
        t.a.b.d = t.a.b
        t.a.b.xl = t.x
        t.a.xl = t.x

        d = t.a.convertTo('nested_dict', convert_values = True)
        
        self.assert_(type(d['b']['d']) is dict)
        self.assert_(type(d['b']) is dict)
        self.assert_(d['b'] is d['b']['d'])
        self.assert_(d['b']['c'] == 1)

        # TreeDict values are only converted if they are a branch somewhere in the 
        self.assert_(type(d['b']['xl']) is dict)
        self.assert_(type(d['xl']) is dict)
        self.assert_(d['xl'] is d['b']['xl'])

    def testConvertTo_05_only_local_as_values_02(self):

        t = TreeDict()

        t.x.y = 1
        t.a.b.c = 1

        a_refs = random_node_list(0, 100, 0.5)
        x_refs = random_node_list(1, 100, 0.5)

        for n in a_refs:
            t.a[n] = t.a.b

        for n in x_refs:
            t.a[n] = t.x

        d = t.a.convertTo('nested_dict', convert_values = False)

        def get_value(d, n):
            for n in n.split('.'):
                d = d[n]
            return d
            
        for n in a_refs:
            self.assert_(type(get_value(d, n)) is dict)
            self.assert_(get_value(d, n) is d['b'])

        for n in x_refs:
            self.assert_(type(get_value(d, n)) is TreeDict)
            self.assert_(get_value(d, n) is t.x)


    def testConvertTo_06_prune_empty_01(self):

        t = TreeDict()

        t.makeBranch('a')

        d = t.convertTo('nested_dict', prune_empty = True)

        self.assert_(d == {})

    def testConvertTo_06_prune_empty_02(self):

        t = TreeDict()

        t.a.x = 1
        t.a.makeBranch('b')

        d = t.convertTo('nested_dict', prune_empty = False)

        self.assert_(d == {'a' : {'x' : 1, 'b' : {} } } )
        
        d2 = t.convertTo('nested_dict', prune_empty = True)

        self.assert_(d2 == {'a' : {'x' : 1 } } )
        

    def testConvertTo_07_lists(self):
        t = TreeDict()

        t.a.b = [1, TreeDict(x = 1)]

        d = t.convertTo('nested_dict', expand_lists = False)

        self.assert_(d == {'a' : {'b' : [1, TreeDict(x = 1)]}})
        
        d2 = t.convertTo('nested_dict', expand_lists = True)

        self.assert_(d2 == {'a' : {'b' : [1, {'x' : 1} ]}})

    def testConvertTo_08_self_referencing_lists(self):
        t = TreeDict()

        t.a = [t]

        d = t.convertTo('nested_dict', expand_lists = False)

        self.assert_(d['a'][0] is t)

        d2 = t.convertTo('nested_dict', expand_lists = True)

        self.assert_(d2['a'][0] is d2)




if __name__ == '__main__':
    unittest.main()

