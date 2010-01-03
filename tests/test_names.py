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

from treedict.treedict import _ldist

from common import *

class TestNames(unittest.TestCase):
    def testRoot(self):
        p = TreeDict('a')
        self.assert_(p.branchName(add_tree_name=True) == 'a')
        self.assert_(p.treeName() == 'a')
        self.assert_(p.branchName() == '')

    def testBranchName01(self):
        p = TreeDict('a')
        b = p.makeBranch('b')

        self.assert_(b.branchName() == 'b', b.branchName())
        self.assert_(b.treeName() == 'a', b.treeName())
        self.assert_(b.branchName(add_path = True) == 'b', b.branchName(add_path = True))
        self.assert_(b.branchName(add_path = True, add_tree_name=True) == 'a.b',
                     b.branchName(add_path = True, add_tree_name=True))
        self.assert_(p._branchNameOf('b') == 'b', p._branchNameOf('b'))

    def testBranchNameEmptyTreeName(self):
        p = TreeDict('')
        b = p.makeBranch('b')

        self.assert_(b.branchName(add_path = True, add_tree_name=True) == '.b',
                     b.branchName(add_path = True, add_tree_name=True))
        self.assert_(b.treeName() == '', b.treeName())
        self.assert_(b.branchName(add_path = True) == 'b', b.branchName(add_path = True))
        self.assert_(p._branchNameOf('b') == 'b', p._branchNameOf('b'))

    def test_dotInTreeName(self):
        p = TreeDict('a.b')
        b = p.makeBranch('c')

        self.assert_(b.branchName(add_path = True, add_tree_name=True) == 'a.b.c',
                     b.branchName(add_path = True, add_tree_name=True))
        self.assert_(b.treeName() == 'a.b', b.treeName())
        self.assert_(b.branchName(add_path = True) == 'c', b.branchName(add_path = True))
        self.assert_(p._branchNameOf('c') == 'c', p._branchNameOf('c'))



if __name__ == '__main__':
    unittest.main()

