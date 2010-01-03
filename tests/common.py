"""
Just a bunch of functions common to the entire test suite
"""
import random, unittest, cPickle, collections
from treedict import TreeDict, getTree
import treedict
from copy import deepcopy, copy

from hashlib import md5
import base64, time


md5keyhash = md5(str(time.clock()))

def unique_name():
    md5keyhash.update(str(time.clock()))

    return 'u' + (''.join(c for c in base64.b64encode(md5keyhash.digest())
                          if c.isalnum()))[:6]

def empty_tree():
    return TreeDict(unique_name())

def sample_tree():
    p = TreeDict(unique_name())
    p.adsfff = 34
    p.bddkeed = 45
    p.cwqod.ada = "ads"
    p.cwqod.ddd = "232"

    p.asddfds.asdffds.asd
    p.single_dangling_node

    return p

def basic_walking_test():
    p = TreeDict()

    p.a.b.v = 1
    p.a.v = 1
    p.makeBranch("b")
    p.v = 1

    p.freeze()

    required_item_dict = { 
        (True, "none"): set([ ("a.b.v", 1), 
                              ("v",     1),       
                              ("a.v",   1) ]),

        (True, "all") : set([ ("a.b.v", 1), 
                              ("v",     1),       
                              ("a.v",   1),
                              ("a",     p.a),   
                              ("a.b",   p.a.b), 
                              ("b",     p.b)  ]),

        (True, "only"): set([ ("a",     p.a),   
                              ("a.b",   p.a.b), 
                              ("b",     p.b) ]),

        (False, "none"): set([("v",     1)  ]),

        (False, "all") : set([("v",     1), 
                              ("a",     p.a), 
                              ("b",     p.b)]),
        
        (False, "only"): set([ ("a",    p.a),   
                               ("b",    p.b) ])}
    
    return (p, required_item_dict)

def frozen_tree():
    p = sample_tree()
    p.freeze()
    return p

def random_node_list(seed, n, dp):
    random.seed(seed)

    idxlist = range(n)
    l = [unique_name() for i in idxlist]
    
    while idxlist:

        delstack = []

        for ii, i in enumerate(idxlist):
            if random.random() < dp:
                l[i] += '.' + unique_name()
            else:
                delstack.append(ii)

        for ii in reversed(delstack):
            del idxlist[ii]
            
    return l

class TestObject:
    def __init__(self, v1, v2, v3):
        self.v1 = v1 
        self.v2 = v2
        self.v3 = v3

test_object = TestObject("bork,", 123, "12321")
test_tuple = (1,324, TestObject(12321, "adsfs", 123))
test_list  = [1,324, TestObject(12321, "adsfs", 123)]
test_dict  = {1:2, "3323" : "dfas"} 


