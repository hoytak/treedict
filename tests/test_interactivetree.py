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

class TestInteractiveTreeDict(unittest.TestCase):

    
    ############################################################
    # For the interactive parameter tree

    def testInteractiveTree_01(self):
        p = sample_tree()
        v = ("borkborkbork", 123)
        p.a.b.c = v

        self.assert_(p.interactiveTree().a.b.c is v)
        
    def testInteractiveTree_03(self):
        p = sample_tree()

        self.assert_(p.interactiveTree().treeDict() is p)

    def testInteractiveTree_04_pickling(self):
        p = sample_tree()

        s = cPickle.dumps(p.interactiveTree(), protocol=0)
        ipt = cPickle.loads(s)

        self.assert_(ipt.treeDict() == p)
        self.assert_(p.interactiveTree() == ipt)

    def testInteractiveTree_05_setattr(self):
        p = sample_tree()
        
        v1 = [123,123,123]
        v2 = [321,321,321]

        p.a.b.c = v1
        
        pi = p.interactiveTree()
        
        self.assert_(p.a.b.c is v1)
        self.assert_(pi.a.b.c is v1)

        pi.a.b.c = v2
        
        self.assert_(p.a.b.c is v2)
        self.assert_(pi.a.b.c is v2)
    

if __name__ == '__main__':
    unittest.main()

