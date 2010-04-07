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

# Cython imports
from name_matching cimport name_match_distance, editDistance
from minsmaxes cimport min2, max2, max2_long, min2_long
from membuffers cimport size_t_v, new_size_t_v, free_size_t_v

# python imports.
import copy as copy_module
import cPickle
import hashlib
import warnings
import re
import inspect
import base64
import heapq
import time

################################################################################
# Some preliminary debug stuff

DEF RUN_ASSERTS = False

################################################################################
# Early bindings to avoid unneeded lookups in the c code

cdef object md5 = hashlib.md5
cdef object dumps = cPickle.dumps
cdef object PicklingError = cPickle.PicklingError
cdef object copy_f = copy_module.copy
cdef object deepcopy_f = copy_module.deepcopy
cdef object b64encode = base64.b64encode

cdef object heappop     = heapq.heappop
cdef object heappush    = heapq.heappush
cdef object heapreplace = heapq.heapreplace

cdef object strfind     = str.find
cdef object strrfind    = str.rfind
cdef object strlower    = str.lower
cdef object strsplit    = str.split

cdef class TreeDict(object) 
cdef class TreeDictIterator(object)
cdef class _PTreeNode(object)

################################################################################
# Needed python C-API stuff

cdef extern from "Python.h":
    ctypedef void PyObject

    PyObject* PyIter_Next(PyObject*)
    bint PyDict_Next(dict p, Py_ssize_t *ppos, PyObject **pkey, PyObject **pvalue)

    PyObject* PyList_New(Py_ssize_t)
    void PyList_SET_ITEM(list l, Py_ssize_t index, PyObject *item)
    void Py_INCREF(PyObject *item)

    void* PyMem_Malloc(size_t n)
    void* PyMem_Realloc(void *p, size_t n)
    void PyMem_Free(void *p)

################################################################################
# Commonly used dictionary keys, instantiated once here for speed

cdef str s_IterReferenceCount = "IteratorReferenceCount"
cdef str s_registration_tree_name = "_registration_tree_name"
cdef str s_registration_branch_name = "_registration_branch_name"
cdef str s_dangling_node_dependents = "_dangling_node_dependents"
cdef str s_cached_hash = "_cached_hash"
cdef str s_auth_key = "_auth_key"
cdef str s_hit_flag = "_hit_flag"
cdef str s_immutable_items_hash = "_immutable_items_hash"

################################################################################
# Special, faster constructor method for use in this file

cdef extern from "py_new_wrapper.h":
    cdef TreeDict createBlankTreeDict "PY_NEW" (object t)

cdef inline TreeDict newTreeDict(str name, bint registered):
    cdef TreeDict p = createBlankTreeDict(TreeDict)
    p._run__cinit__()
    p._run__init__(name)

    if registered:
        p._setRegistered()

    return p

cdef extern from "py_new_wrapper.h":
    cdef TreeDictIterator createBlankTreeDictIterator "PY_NEW" (object t)

cdef inline TreeDictIterator newTreeDictIterator(
    TreeDict p, bint _recursive, int _branch_mode, int _itertype):

    cdef TreeDictIterator pti = createBlankTreeDictIterator(TreeDictIterator)
    pti._init(p, _recursive, _branch_mode, _itertype)
    return pti


################################################################################
# A few global helper functions dealing with name checking

cdef object _string_name_validator = re.compile(r'\A[a-zA-Z_]\w*\Z')
cdef object _string_name_validator_match = _string_name_validator.match

cdef inline checkKeyNotNone(str n):
    if n is None:
        raise TypeError("Expected string or unicode for name, got NoneType.")

cdef inline checkNameValidity(str n):
    checkKeyNotNone(n)

    if not isValidName(n):
        raise NameError("'%s' not a valid branch name." % n)
    
cdef inline bint isValidName(str n):

    if n is None: 
        return False

    return (_string_name_validator_match(n) is not None)

cdef inline str catNames(str s1, str s2):
    if len(s1) == 0:
        return s2
    elif len(s2) == 0:
        return s1
    else:
        return s1 + '.' + s2
    

################################################################################
# A unique value that never needs to be stored in a node.

cdef class _NoDefault(object): pass

################################################################################
# A dictionary that holds instances of certain trees so modules can
# request them by name using getTree()

cdef dict _tree_lookup_dict = {}

cdef inline registerTree(TreeDict tree):
    registerTreeByName(tree._branchName(False, True), tree)

cdef inline registerTreeByName(str name, TreeDict tree):
    _tree_lookup_dict[name] = tree

cpdef TreeDict getTree(str name):
    """
    Retrieves or creates a parameter tree with the given name.  This
    is the recommended way to create a new treedict instance if it is
    used to hold global parameter settings.  Creating the tree this
    way allows other modules to also access the same tree through this
    method -- if the tree already exists in the global tree registry,
    the same tree is returned.

    A tree is considered 'registered' and can be retrieved in this way
    if and only if it is instantiated through this function.

    *NOTE: This module may be removed in the future do to the 'only
    one way to do things' aspect of pythonicity.  A similar example is
    found in the logging module, but the main use cases I can think of
    -- globally defined parameters -- can be done using the module
    system.  Feedback on this is welcome; for now, I'll leave it in - HK.*
    """

    checkKeyNotNone(name)

    cdef TreeDict t

    try:
        return _tree_lookup_dict[name]
    except KeyError:
        t = newTreeDict(name, True)
        registerTree(t)
        return t

cpdef bint treeExists(str name):
    """
    Returns True if a registered tree with name `name` exists, and
    False otherwise.

    *NOTE: This module may be removed in the future do to the 'only
    one way to do things' aspect of pythonicity.  A similar example is
    found in the logging module, but the main use cases I can think of
    -- globally defined parameters -- can be done using the module
    system.  Feedback on this is welcome; for now, I'll leave it in - HK.*
    """
        
    return name in _tree_lookup_dict

################################################################################
# A class to hold values in the tree.  It also contains information on
# how they behave regarding equality testing, etc.; i.e. it stores
# type information along with the node. Most of the hashing
# functionality happens here.

class HashError(ValueError): pass

########################################
# First -- hashing functionality
cdef _runValueHash(hf, value):
    if type(value) is dict:
        hf("$$$DICT")
        for k, v in sorted((<dict>value).iteritems()):
            _runValueHash(hf, k)
            hf(":")
            _runValueHash(hf, v)

    elif type(value) is set:
        hf("$$$SET")
        for v in sorted(value):
            _runValueHash(hf, v)

    elif type(value) is list:
        hf("$$$LIST")
        for v in (<list>value):
            _runValueHash(hf, v)

    elif type(value) is tuple:
        hf("$$$TUPLE")
        for v in (<tuple>value):
            _runValueHash(hf, v)
            
    elif type(value) is TreeDict:
        hf( (<TreeDict>value)._self_hash() )
        
    else:
        try:
            hf(dumps(value, protocol=2))
        except PicklingError:
            raise HashError

################################################################################
# Flags and such; trying to be as scaleable

####################
# Tree properties

ctypedef unsigned long int flagtype

DEF f_is_frozen            = 1
DEF f_is_dangling          = 2
DEF f_is_detached_dangling = 4  # for during an atomic set operation
DEF f_is_registered        = 8
DEF f_one_iterators_referencing = 16
DEF f_many_iterators_referencing = 32
DEF f_is_already_copied    = 64

DEF f_newbranch_propegating_flags = (f_is_frozen | f_is_registered)
DEF f_copybranch_propegating_flags = (f_is_dangling)

# Error checking 
DEF f_getattr_called   = 1024

####################
# Getting / retrieving

# Create the node if the desired node isn't there.
DEF f_create_if_needed = 16

# If dangling nodes can be returned in the operation
DEF f_dangling_okay    = 32

# If the operation will not leave any dangling nodes or intermediate
# objects around; optimizes some of the setting and getting
DEF f_atomic_set       = 64

# If we're just doing a dry run with no changes to the tree
DEF f_dry_run          = 128

DEF f_create_dangling  = 256

DEF f_already_dryset   = 512

DEF f_ignore_nonbranches = 1024

DEF f_allFlags         = (2**31 - 1)


cdef inline void _setFlagOn(flagtype *f, flagtype flag):
    f[0] |= flag

cdef inline void _setFlagOff(flagtype *f, flagtype flag):
    f[0] &= (f_allFlags - flag)

cdef inline void _setFlag(flagtype *f, flagtype flag, bint on):
    if on: _setFlagOn(f, flag)
    else:  _setFlagOff(f, flag)

cdef inline bint _flagOn(flagtype *f, flagtype flag):
    return (f[0] & flag) != 0


########################################
# Typing stuff

# In the list below; simple means that repr(v) is adequate for
# hashing; otherwise pickling is required for hash checks

DEF t_Mutable_Simple    = 0
DEF t_Mutable_Complex   = 1
DEF t_Immutable_Simple  = 2
DEF t_Immutable_Complex = 3
DEF t_Tree              = 4
DEF t_Branch            = 5
DEF t_Unknown           = -1

cdef dict _fast_type_determination = {

    # Immutable Types
    int     : t_Immutable_Simple,
    long    : t_Immutable_Simple,
    str     : t_Immutable_Simple,
    bool    : t_Immutable_Simple,
    unicode : t_Immutable_Simple,
    complex : t_Immutable_Simple,
    float   : t_Immutable_Simple,
    str     : t_Immutable_Simple,

    # Mutable Types
    list      : t_Mutable_Complex,
    dict      : t_Mutable_Complex,
    set       : t_Mutable_Complex
    }

cdef inline int itemType(v):
    cdef object t = type(v)

    try:
        return _fast_type_determination[t]
    except KeyError:
        pass

    try:
        hash(v)
    except TypeError:
        return t_Mutable_Complex

    return t_Immutable_Complex    

########################################

# Now a class for holding the nodes.  Queries relating to item
# properties should be implemented as methods relating to this

DEF _orderNodeNotKnown      = 0
DEF _orderNodeStartingValue = 0
cdef size_t _orderNodeMaxNum = <size_t>( (<double>2)**(8*sizeof(size_t) - 1)) - 2 

cdef class _PTreeNode(object):
    cdef object    _v
    cdef int       _t
    cdef size_t    _order_position
    cdef dict      _aux_dict

    cdef _set_it(self, TreeDict node, v, size_t _order_position):
        
        self._v = v

        if type(v) is TreeDict:
            if (<TreeDict>v).parentNode() is node:
                self._t = t_Branch
            else:
                self._t = t_Tree
        else:
            self._t = itemType(v)

        self._aux_dict = {}
        self._order_position = _order_position

    cdef value(self):
        return self._v

    cdef orderPosition(self):
        return self._order_position

    cdef setOrderPostion(self, size_t op):
        self._order_position = op

    cdef int type(self):
        return self._t

    # Basically there are three classes; trees, mutable local types,
    # and immutable local types

    cdef bint isMutable(self):
        return (self._t == t_Mutable_Simple
                or self._t == t_Mutable_Complex)

    cdef bint isImmutable(self):
        return (self._t == t_Immutable_Simple
                or self._t == t_Immutable_Complex)

    cdef bint isBranch(self):
        return self._t == t_Branch

    cdef bint isNonBranchTree(self):
        return self._t == t_Tree

    cdef bint isDanglingBranch(self):
        return self.isBranch() and (<TreeDict>self._v).isDangling()

    cdef bint isTree(self):
        return self.isBranch() or self.isNonBranchTree()

    cdef bint isDanglingTree(self):
        return self.isTree() and (<TreeDict>self._v).isDangling()

    cdef TreeDict tree(self):
        if RUN_ASSERTS:
            assert self.isTree()

        return (<TreeDict>self._v)

    cdef bint isChildOf(self, TreeDict parent):
        if RUN_ASSERTS:
            assert self.isTree()
        
        return (<TreeDict>self._v).parentNode() is parent

    cdef str fullHash(self):
        h = md5()
        hf = getattr(h, 'update')
        self.runFullHash(hf)
        return h.digest()

    cdef runFullHash(self, hf):
        cdef TreeDict p
        
        if self._t == t_Tree or self._t == t_Branch:
            p = (<TreeDict>self._v)
            if not p.isDangling():
                p._runFullHash(hf)
        elif self._t == t_Mutable_Simple:
            hf(repr(self._v))
        elif self._t == t_Mutable_Complex:
            _runValueHash(hf, self._v)
        elif self._t == t_Immutable_Simple or self._t == t_Immutable_Complex:
            self.runImmutableHash(hf)

    cdef runImmutableHash(self, hf):
        # Only update it if the item is in the immutable
        
        if self._t == t_Immutable_Simple:
            hf(repr(self._v))
        elif self._t == t_Immutable_Complex:
            hf(self._immutableHash())
    
    cdef str _immutableHash(self):
        if s_cached_hash not in self._aux_dict:
            ch = md5(dumps(self._v, protocol=2)).digest()
            self._aux_dict[s_cached_hash] = ch
            return ch
        else:
            return self._aux_dict[s_cached_hash]
        
    cdef bint isEqual(self, _PTreeNode pn):
        if self._t != pn._t:
            return False

        if self._t == t_Tree or self._t == t_Branch:
            return (<TreeDict>self._v)._isEqual(<TreeDict>pn._v)
        else:
            return self._v == pn._v

    def __reduce__(self):
        return (_PTreeNode_unpickler,
                (self._v, self._t, self._order_position) )

########################################
# Stuff for fast node creation

cdef extern from "py_new_wrapper.h":
    cdef _PTreeNode createPTreeNode "PY_NEW" (object t)

cdef inline _PTreeNode newPTreeNode(TreeDict node, value, size_t order_pos):
    cdef _PTreeNode pn = createPTreeNode(_PTreeNode)
    pn._set_it(node, value, order_pos)
    return pn

def _PTreeNode_unpickler(value, int t, size_t order_pos):
    return newPTreeNodeExact(value, t, order_pos)

cdef inline newPTreeNodeExact(value, int t, size_t order_pos):
    
    cdef _PTreeNode pn = createPTreeNode(_PTreeNode)
    pn._v = value
    pn._t = t
    pn._order_position = order_pos
    pn._aux_dict = {}
    return pn


################################################################################
# Special functions and a corresponding dictionary for use within the tree

class _SpecialFunctionNotAvailable(Exception): pass

def _special_hash(TreeDict p):
    return p._self_hash()

def _special_parent(TreeDict p): 
    if p.isRoot():
        raise _SpecialFunctionNotAvailable

    return p.parentNode()

def _special_root(TreeDict p):
    return p.rootNode()

cdef dict _special_functions = { 
    "$hash"     : _special_hash,
    "@"         : _special_parent,
    "@@"        : _special_root }

################################################################################
# Iterator Container

DEF i_Items  = 1
DEF i_Keys   = 2
DEF i_Values = 3

DEF i_BranchMode_All = 1
DEF i_BranchMode_None = 2
DEF i_BranchMode_Only = 3

cdef dict _branch_mode_lookup = {
    'all'    : i_BranchMode_All,
    'only'   : i_BranchMode_Only,
    'none'   : i_BranchMode_None}

cdef object _branch_mode_error_msg = "branch_mode must be one of 'all', 'only' or 'none'"

cdef class TreeDictIterator(object):
    cdef bint _recursive

    cdef int _branch_mode
    cdef int _itertype
    
    cdef list _key_stack

    cdef Py_ssize_t* _pos_array
    cdef size_t _pos_array_size

    cdef TreeDict _cur_pt
    cdef size_t _cur_depth

    cdef str        _last_key, _current_key
    cdef _PTreeNode _last_pn
    cdef object _next_return_value

    cdef bint _base_treedict_referenced
    cdef bint _stop_on_next
    cdef bint _first_iter_run_yet

    def __cinit__(self):
        self._pos_array = NULL

    def __dealloc__(self):
        if self._pos_array != NULL:
            PyMem_Free(self._pos_array)

        if self._stop_on_next:
            return
        else:
            while self.goDownStack(): 
                pass

            self._decRefToCurTree(0)

            if RUN_ASSERTS:
                assert not self._base_treedict_referenced

    cdef void _init(self, TreeDict p, bint _recursive, 
                    int _branch_mode, int _itertype):

        self._recursive   = _recursive
        self._branch_mode = _branch_mode
        self._itertype    = _itertype

        # Allocate space for the position stack
        self._pos_array_size = 16
        self._pos_array = <Py_ssize_t*> PyMem_Malloc(self._pos_array_size*sizeof(Py_ssize_t*))

        if self._pos_array == NULL: 
            raise MemoryError

        self._cur_pt = p
        self._incRefToCurTree(0)

        self._pos_array[0] = 0
        self._key_stack    = []

        self._cur_depth    = 0

        self._last_key     = None
        self._current_key  = None
        self._last_pn      = None

        # This is what will be returned; we keep one step ahead so the
        # lock on the TreeDict is released on the final iteration.
        self._next_return_value  = None
        self._stop_on_next = False
        self._first_iter_run_yet = False

    cdef void _ensurePosArraySized(self, size_t n):
        if self._pos_array_size <= n:
            self._pos_array_size = n + (n >> 1)
            self._pos_array = <Py_ssize_t*>PyMem_Realloc(self._pos_array, self._pos_array_size*sizeof(Py_ssize_t*))

    def __iter__(self):
        return self

    def __next__(self):
        # Iterator interface for these functions
        return self._next()

    cdef _next(self):
        
        if self._stop_on_next:
            if RUN_ASSERTS:
                assert not self._base_treedict_referenced

            raise StopIteration

        r = self._next_return_value

        if self._loadNext():
            self._next_return_value = self._currentRetValue()
        else:
            if RUN_ASSERTS:
                assert not self._base_treedict_referenced

            self._stop_on_next = True            

        if not self._first_iter_run_yet:
            self._first_iter_run_yet = True
            return self._next()
        else:
            return r

    cdef bint _loadNext(self):

        cdef PyObject *k_obj, *pn_obj
        cdef bint iter_going

        while True:
            iter_going = PyDict_Next(self._cur_pt._param_dict, &self._pos_array[self._cur_depth], &k_obj, &pn_obj)

            if not iter_going:
                if not self.goDownStack():
                    self._last_key = None
                    self._last_pn  = None

                    self._decRefToCurTree(0)
                    return False
                else:
                    continue
            else:
                self._last_key = (<str>k_obj)
                self._last_pn  = (<_PTreeNode>pn_obj)

            if self._last_pn.isBranch():
                if self._last_pn.isDanglingBranch():
                    continue

                if self._branch_mode != i_BranchMode_None:

                    self._setCurrentKey()  # Call before the recursion

                    if self._recursive:
                        self.goUpStack(self._last_key, self._last_pn.tree())

                    return True

                else:
                    if self._recursive:
                        self.goUpStack(self._last_key, self._last_pn.tree())

                    continue

            elif self._branch_mode == i_BranchMode_Only:
                continue
            
            self._setCurrentKey()
            return True
    
    cdef void goUpStack(self, str k, TreeDict p):
        self._cur_depth += 1
        
        self._ensurePosArraySized(self._cur_depth)
        self._pos_array[self._cur_depth] = 0
        self._cur_pt = p
        self._incRefToCurTree(self._cur_depth)
        self._key_stack.append(self._fullKey(k))
        
    cdef bint goDownStack(self):

        if self._cur_depth == 0:
            if RUN_ASSERTS:
                assert len(self._key_stack) == 0

            # Asking to go down stack when we're on the only one
            return False

        if RUN_ASSERTS:
            assert self._cur_pt is not None
            assert len(self._key_stack) != 0
        
        self._decRefToCurTree(self._cur_depth)
        self._cur_depth -= 1
        self._cur_pt = self._cur_pt.parentNode()
        self._key_stack.pop()

        return True

    # Split these two next steps so that we can handle going up a
    # branch and also returning that branch
    cdef str currentKey(self):
        return self._current_key
        
    cdef void _setCurrentKey(self):
        self._current_key = self._fullKey(self._last_key)

    cdef void _decRefToCurTree(self, size_t depth):
        if depth == 0:
            if self._base_treedict_referenced:
                self._cur_pt.iteratorDecRef()

            self._base_treedict_referenced = False
        else:
            self._cur_pt.iteratorDecRef()

    cdef void _incRefToCurTree(self, size_t depth):
        self._cur_pt.iteratorIncRef()

        if depth == 0:
            self._base_treedict_referenced = True
    
    cdef _PTreeNode currentPTreeNode(self):
        return self._last_pn

    cdef _currentRetValue(self):
        if self._last_key is None or self._last_pn is None:
            return None

        if self._itertype == i_Keys:
            return self.currentKey()
        elif self._itertype == i_Values:
            return self.currentPTreeNode().value()
        elif self._itertype == i_Items:
            return (self.currentKey(), self.currentPTreeNode().value())

    cdef str _fullKey(self, str k):
        if len(self._key_stack) == 0:
            return k
        else:
            return (<str>self._key_stack[-1]) + '.' + k


################################################################################
# Now the actual parameter tree structure

cdef class TreeDict(object):

    cdef:
        dict _param_dict
        list _branches
        
        TreeDict _parent
        
        str _name
        
        flagtype _flags
        
        size_t _n_mutable, _next_item_order_position, _n_dangling

        dict _aux_dict 

        object __weakref__
    
    def __cinit__(self):
        self._run__cinit__()

    cdef _run__cinit__(self):
        
        # Split this off so the new style constructor can use them
        self._param_dict = {}
        self._aux_dict = {}
        self._branches = []
    
        self._flags = 0
    
        self._n_mutable = 0
        self._n_dangling = 0
        self._next_item_order_position = _orderNodeStartingValue

    def __init__(self, str tree_name = 'root', **kwargs):
        self._run__init__(tree_name)
        
        if len(kwargs) != 0:
            self._setAll(None, kwargs, False)

    cdef _run__init__(self, str name):

        # Split this off so the new style constructor can use it
        self._name = name
    
    cdef _setRegistered(self):

        if RUN_ASSERTS: 
            assert not treeExists(self._name)

        self._setRegisteredFlag(True)

    ################################################################################
    # Parameters for manipulating the values

    def __setattr__(self, str k, v):
        self._setLocal(k, v, 0)

    def __setitem__(self, str k, v):
        self.set(k, v)

    def update(self, d):
        """
        Updates the current TreeDict instance with another set of
        values. `d` may be either a dictionary or another TreeDict
        instance.

        Note: Unlike the update method of dict, this method may fail
        and raise an exception.  This can occur either because one or
        more of the keys in `d` is not a valid key name (only occurs
        if `d` is a dict), or if all/part of the tree being updated is
        frozen.  If this happens, no changes are made to the tree
        (i.e, this method is atomic).
        """

        if type(d) is dict:
            self._setAll(None, d, False)
        elif type(d) is TreeDict:
            self._update(d)
        else:
            self._setAll(None, dict(d), False)

    cdef _update(self, TreeDict p):

        cdef str k 
        cdef _PTreeNode pn, pn2

        for k, pn in p._param_dict.iteritems():
            if pn.isBranch() and not pn.isDanglingTree():

                try:
                    pn2 = self._param_dict[k]
                    
                    if pn2.isBranch():
                        pn2.tree()._update(pn.tree())
                    else:
                        self._cut(k)
                        self._attach(pn.tree(), k, True)
                except KeyError:
                    self._attach(pn.tree(), k, True)

            else:
                self._setLocal(k, pn.value(), 0)


    def setFromString(self, str key, str value, dict extra_variables = {}):
        """
        A convenience function for setting arguments from sources in
        which a python type or expression is embedded inside a string
        (e.g. arguments given on the command line).

        For example::

          p.setFromString('a', '(1,2,3)')

        would set ``p.a`` to ``(1,2,3)``, a python tuple.

        Internally, this is done by trying to evaluate `value` as a
        python string, and returning a simple string if an error
        occurs.  `extra_variables` is passed to ``eval()`` to provide
        additional variables for evaluating the string.  Users wanting
        more sophistication should avoid this method.

        Returns True if the value was translated successfully and
        False otherwise.

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.setFromString('x', '1')
            True
            >>> t.setFromString('y', '(1,2,["abc",None])') 
            True
            >>> t.setFromString('z', '{"abc" : 1}')
            True
            >>> print t.makeReport()
            x = 1
            y = (1, 2, ['abc', None])
            z = {'abc': 1}
        
        """

        try:
            v = eval(value.strip(), extra_variables)
            ret_status = True
        except Exception:
            v = value
            ret_status = False

        self._set(key, v, False)

        return ret_status

    @classmethod
    def fromkeys(cls, key_iterable, value = None):
        """
        Creates a new TreeDict instance populated by setting the keys
        in `key_iterable` to `value`, which defaults to None.

        This behavior is analagous to the fromkeys() method of dict.

        Example 1::

            >>> from treedict import TreeDict
            >>> t = TreeDict.fromkeys(['a', 'b', 'c'])
            >>> print t.makeReport()
            a = None
            c = None
            b = None

        Example 2::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict.fromkeys('abc', 'abc')
            >>> print t.makeReport()
            a = 'abc'
            c = 'abc'
            b = 'abc'
        """

        cdef TreeDict p = newTreeDict(None, False)
        
        try:
            p._setAll(None, dict.fromkeys(key_iterable, value), False)
            return p
        except Exception, e:
            raise e

    def setdefault(self, str key, value = None):
        """
        If `key` does not exist, sets `key` eqaul to `value`, which
        defaults to None.  Returns `value` if `key` was changed;
        otherwise returns the original value.

        This behavior is analagous to the setdefault() method of dict.

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict(x = 1)
            >>> print t.makeReport()
            x = 1
            >>> t.setdefault('x', 2)
            1
            >>> t.setdefault('y', 2)
            2
            >>> print t.makeReport()
            x = 1
            y = 2
          
        """

        if not self._exists(key, False):
            self._set(key, value, False)
            return value
        else:
            return self._get(key, False)

    def set(self, *args, **kwargs):
        """
        Sets the value of a particular key or set of keys.

        In the case of name conflicts, keyword arguments take
        precedence over all others, and key-value pairs given later in
        the args list take precedence over earlier values.

        In the case of an error or exception on any set of keys, none
        of the arguments are set.

        Examples::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.set("x", 1)
            >>> t.set(z = 3)
            >>> t.set("ya", 2, "yb", 2, yc = 3)
            >>> t.set("a.b.c.v", 1)
            >>> print t.makeReport()
            x       = 1
            z       = 3
            ya      = 2
            yb      = 2
            yc      = 3
            a.b.c.v = 1
            
        Setting values in groups is all or nothing::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.set("x", 1)
            >>> print t.makeReport()
            x = 1
            >>> t.set("a", 3, "b", 4, "1badvalue", 5)
            Traceback (most recent call last):
             File "<stdin>", line 1, in <module>
             File "treedict.pyx", line 967, in treedict.treedict.TreeDict.set (treedict/treedict.c:8318)
            NameError: '1badvalue' not a valid branch name.
            >>> print t.makeReport()
            x = 1
        """

        try:
            self._setAll(args, kwargs, False)
        except Exception, e:
            raise e

    def dryset(self, *args, **kwargs):
        """
        Same as `set()`, and will raise the same exceptions on
        failure, but doesn't actually change the tree in any way.
        Useful for ensuring that a set of arguments is valid and won't
        raise an exception.  
        """

        try:
            self._setAll(args, kwargs, True)
        except Exception, e:
            raise e

    cdef _setAll(self, tuple args, dict kwargs, bint dry_run):

        # Sets major functionality for the set function.
        
        cdef size_t n_args = len(args) if args is not None else 0

        if ((<int>(n_args)) % 2) != 0:
            raise TypeError("Even number of non-keyword arguments expected.")

        cdef size_t n_argsets = n_args / 2

        cdef size_t i
        
        # important to preserve order
        cdef list key_list = [None]*n_argsets
        cdef list val_list = [None]*n_argsets

        for i from 0 <= i < n_argsets:
            k = args[2*i]

            if not type(k) is str:
                raise TypeError("Name argument (%d, '%s') not string." % (i, repr(k)))

            if len(<str>k) == 0:
                raise NameError("Name argument (%d) empty string." % i)

            v = args[2*i + 1]

            key_list[i] = k
            val_list[i] = v
            
            # test it 
            self._dryset(<str>k, v)

        for k, v in kwargs.iteritems():
            if not type(k) is str:
                raise TypeError("Name argument '%s' not string." % repr(k))

            self._dryset(<str>k, v)

        # Now everything has been tested; go ahead and set it if need be
        if not dry_run:
            for i from 0 <= i < n_argsets:
                self._set(<str>key_list[i], val_list[i], True)

            for k, v in kwargs.iteritems():
                self._set(<str>k, v, True)

    cdef _set(self, str k, value, bint already_checked):
        self._set_master_function(k, value, False, True)

    cdef _dryset(self, str k, value):
        # doesn't actually change anything, but raises any exceptions
        # that would be raised if it was set
        self._set_master_function(k, value, True, False)


    cdef _set_master_function(self, str k, value, bint dry_run, bint already_checked):
        
        cdef flagtype gsp = (f_dangling_okay 
                             | f_create_if_needed 
                             | f_atomic_set
                             | (f_dry_run if dry_run else 0)
                             | (f_already_dryset if already_checked else 0))

        cdef int rpos = strrfind(k, '.')

        if rpos != -1:
            self._getBranch(k[:rpos], gsp | f_ignore_nonbranches)._setLocal(k[rpos+1:], value, gsp)
        else:
            self._setLocal(k, value, gsp)

    cdef _ensureWriteable(self, str k):
        if self.isFrozen():
            if k is not None:
                raise TypeError("%s frozen; cannot modify '%s'" % (self._branchName(False, True), k))
            else:
                raise TypeError("%s frozen; cannot modify." % self._branchName(False, True))

        if self.isIterReferenced():
            raise RuntimeError("%s cannot be changed while being iterated over." % self._branchName(False, True))
        

    cdef _setLocal(self, str k, v, flagtype gsp):
        # All set operations should go through this function.

        if RUN_ASSERTS:
            checkKeyNotNone(k)

        if not (gsp & f_already_dryset): # Skip things we've already checked
            self._ensureWriteable(k)
            
            # Check the name
            checkNameValidity(k)
            
        # Possible (extremely rare) bug: I chose to put this before
        # the cutting to make sure dry_run ensured things would
        # work. However, it will now throw, even if it could work, if
        # there are the maximum number of nodes present and one is
        # replaced.  But that won't happen often, if ever.
        self._checkNodeAvailability()

        if (gsp & f_dry_run):
            return

        cdef _PTreeNode lpn, new_pn
                
        ########################################
        # Now go through the above

        if self._existsLocal(k, True):
            # Most common case, # 1 above
            lpn = self._getLocalPTNode(k)
            self._keyDeleted(k, lpn)

            new_pn = newPTreeNode(self, v, lpn.orderPosition())
            self._param_dict[k] = new_pn
            self._keyInserted(k, new_pn)

        else:
            new_pn = newPTreeNode(self, v, self._getNextOrderValue())
            self._param_dict[k] = new_pn
            self._keyInserted(k, new_pn)

    ########################################
    # Code to deal with ordering of node values

    cdef _checkNodeAvailability(self):
        if self._next_item_order_position >= _orderNodeMaxNum - 1:
            # Need to rework the nodes; raises exception if there's a
            # problem
            self._reworkOrderValues()

    cdef size_t _getNextOrderValue(self):
        cdef size_t ret = self._next_item_order_position
        self._next_item_order_position += 1
        return ret
                
    cdef _reworkOrderValues(self):
        cdef _PTreeNode pn

        cdef list vl = sorted([pn.orderPosition()
                               for pn in self._param_dict.itervalues()])

        if len(vl) > _orderNodeMaxNum:
            raise OverflowError("Maximum number of branches/leaves (%d) exceeded."
                                % str(_orderNodeMaxNum))

        cdef dict tr_dict = dict([(p, np+1) for np, p in enumerate(vl)])
        
        for pn in self._param_dict.itervalues():
            pn.setOrderPostion(tr_dict[pn.orderPosition()])

        self._next_item_order_position = len(vl) + 2
        
    ################################################################################
    # Methods that freeze the state of the tree

    cpdef freeze(self, str branch=None, bint quiet = True):
        """
        Freezes the tree and all branches so no further manipulations
        can happen.  The tree cannot be unfrozen except by creating an
        unfrozen copy of that tree.  If the tree does not contain
        mutable values, it can then be used as a key in a dictionary.

        If `branch` is given, then only that branch (and all
        sub-branches) are frozen.

        If `quiet` is True, then no error is raised if `branch` refers
        to a value instead of a branch.  Otherwise, a TypeError
        exception is raised. This parameter is ignored if `branch` is
        None.

        Note: TreeDict values stored in the tree as values -- not as
        branches -- are not affected by this freezing operation.
        """

        if branch is None:
            self._freeze_tree()
        else:
            b = self.get(branch)

            if not type(b) is TreeDict:
                if not quiet:
                    raise TypeError("Cannot freeze non-branch value at key '%s'" % branch)
                else:
                    return

            (<TreeDict>b)._freeze_tree()


    cdef _freeze_tree(self):
            self._setFrozen(True)

            for b in self._branches:
                (<TreeDict>b)._freeze_tree()

    ################################################################################
    # Methods for deleting / pruning the tree
                
    def __delattr__(self, str k):
        self._prune(k, False)

    def __delitem__(self, k):
        if type(k) is not str:
            raise KeyError(k)

        self._prune(k, False)
    
    cdef _cut(self, str k):

        cdef TreeDict p

        self._ensureWriteable(k)

        # Legit if this raises an error
        cdef _PTreeNode pn = self._param_dict.pop(k)
    
        self._keyDeleted(k, pn)

        if pn.isBranch():
            p = pn.tree()

            # One of the concerns here is how items are viewed by
            # other references after dropping them here.  
            p._setDangling(False)
            p._setDetachedDangling(False)
            p._resetParentNode(None)

        return pn.value()

    def clear(self, branch_mode = 'all'):
        """
        Clears branches and/or values from the current tree.

        If branch_mode is 'all' (default), all nodes and values
        current tree are cleared.

        If branch_mode is 'only', only the branches are cleared out
        and the values are left.

        If branch_mode is 'none', the branches are left, but all the
        values are cleared.

        Example::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict() ; t.set('a.b', 1, 'b.c', 2, x = 1, y = 2)
            >>> print t.makeReport()
            a.b = 1
            b.c = 2
            y   = 2
            x   = 1
            >>> t1 = t.copy() ; t2 = t.copy()
            >>> t.clear()
            >>> t.isEmpty()
            True
            >>> 
            >>> t1.clear(branch_mode = 'none')
            >>> print t1.makeReport()
            a.b = 1
            b.c = 2
            >>> 
            >>> t2.clear(branch_mode = 'only')
            >>> print t2.makeReport()
            y = 2
            x = 1
        """

        cdef int b_mode = self._getBranchMode(branch_mode)
        cdef _PTreeNode pn

        # Check if it's a dangling node; this is bad

        if self.isDangling():
            self._raiseErrorAtFirstNonDanglingBranch(True)

        # First check if it's frozen or can't be written
        self._ensureWriteable(None)

        if b_mode == i_BranchMode_All:
            self._param_dict.clear()
            self._branches = []
            self._n_dangling = 0
            self._n_mutable = 0
            self._next_item_order_position = _orderNodeStartingValue
        else:
            for k, pn in self._param_dict.items():
                if b_mode == i_BranchMode_Only:
                    if pn.isBranch():
                        self._cut(k)
                elif b_mode == i_BranchMode_None:
                    if not pn.isBranch():
                        self._cut(k)

    ################################################################################
    # Some methods for raising attribute errors at the proper time

    cdef _raiseAttributeError(self, str key):
        raise AttributeError("branch/value/method '%s' does not exist in tree/branch '%s'." % (key, self._branchName(False, True)))

    cdef _raiseErrorAtFirstNonDanglingBranch(self, bint raise_attribute_error):
        cdef TreeDict p = self.parentNode()

        if RUN_ASSERTS:
            assert p is not None

        if not p.isDangling():
            if self.isDangling():
                if raise_attribute_error:
                    p._raiseAttributeError(self._name)
                else:
                    raise KeyError(self._name)
        else:
            p._raiseErrorAtFirstNonDanglingBranch(raise_attribute_error)
            

    ################################################################################
    # Detaching and attaching

    def pop(self, str key = None, bint prune_empty = False, bint silent = False):
        """
        Detach branch/value `key`, and returns the associated value.

        If `key` is None (default), detach self from parent and return
        self.

        A TypeError is raised if called on the root node with no name.

        If `prune_empty` is True, and a branch with multiple nodes is
        given as the key, then all empty branches in the path are also
        pruned.

        If `silent` is True, then no error is raised if the key is not
        present.

        The pruned branch / value is returned (or None if `silent` is
        True and the key does not exist).

        This method is analogous to the `pop` method for dicts (with
        extra options).


        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.b.c.d.e.y = 2
            >>> t.b.c.d.e.pop('y')
            2
            >>> "b.c.d.e.y" in t
            False
            >>> "b.c.d.e" in t
            True
            >>> t.b.c.d.e.pop()
            TreeDict <e>
            >>> "b.c.d.e" in t
            False
            >>> "b.c.d" in t
            True
            >>> t.b.c.d.pop(prune_empty = True)
            TreeDict <d>
            >>> "b.c.d" in t
            False
            >>> "b.c" in t
            True
            >>> t.isEmpty()
            False
            >>> t.pop('nothere')
            Traceback (most recent call last):
             File "<stdin>", line 1, in <module>
             File "treedict.pyx", line 1365, in treedict.treedict.TreeDict.pop (treedict/treedict.c:11193)
            KeyError: 'nothere'
            >>> t.pop('nothere', silent=True)
            >>> 
        
        """

        try:
            return self._pop(key, False, prune_empty)
        except KeyError, ke:
            if silent:
                return None
            else:
                raise ke

    def popitem(self, str key = None, bint prune_empty = False, bint silent = False):
        """
        Same as :meth:`pop()`, except return the pair (`key`, value)
        instead of just the value.

        If `key` is None or not given, detach self from parent and
        return the pair (name, self), where name is the name of this
        branch.  

        A TypeError is raised if called on the root node with no name.

        If `prune_empty` is True, and a branch with multiple nodes is
        given as the key, then all empty branches in the path are also
        pruned.

        If `silent` is True, then no error is raised if the key is not
        present.

        The pruned branch / value is returned (or None if `silent` is
        True and the key does not exist).

        This method is analogous to the `popitem` method for dicts (with
        extra options).
        """

        try:
            return self._pop(key, True, prune_empty)
        except KeyError, ke:
            if silent:
                return None
            else:
                raise ke
    
    cdef _pop(self, str name, bint return_item_pair, bint prune_empty):

        cdef TreeDict p 
        
        if name is None:
            if self.isDangling():
                self._raiseErrorAtFirstNonDanglingBranch(True)

            p = self.parentNode()

            if p is None:
                raise TypeError("Cannot detach root node.")
            
            p._prune(self._name, False)

            if return_item_pair:
                return (self._name, self)
            else:
                return self

        else:
            return self._prune(name, prune_empty)

    cdef _prune(self, str k, bint aggressive):

        checkKeyNotNone(k)

        cdef int rpos = strrfind(k, '.')
        cdef str kl
        cdef TreeDict bottom, b, p

        cdef flagtype gsp = f_dangling_okay

        if rpos != -1:

            b = self._getBranch(k[:rpos], gsp)

            if b is None:
                raise KeyError(k)

            kl = k[rpos+1:]
        else:
            b = self
            kl = k

        # The False/True here controls whether it's okay to prune a
        # dangling node
        if not b._existsLocal(kl, True):
            raise KeyError(k)

        v = b._cut(kl)

        if aggressive:
            bottom = self._getBottomNode(k)

            while b is not bottom and not b.isRoot() and b.isEmpty():
                p = b.parentNode()
                p._cut(b._name)
                b = p

        return v

    def attach(self, tree_or_node = None, str name = None,
               bint copy = True, bint recursive = False):
        """
        Attaches a parameter tree 'p' to node `name`.  If `p` is the
        root node of a tree, then the exact object is attached in;
        otherwise, `copy` must be True.  If `name` is None, the tree's
        name is used; if this is not a valid node name, then an
        exception is raised.

        If `recursive` is true, then `tree_or_node` and `alt_name`
        must be None (default), Attach then goes through the tree,
        attaching all the TreeDict nodes that are not part of this
        tree.  If `force_copy` is True, then all TreeDicts not already
        part of this tree are copied in; otherwise, only those that
        are not a root node are copied in.

        Example 1::

            >>> from treedict import TreeDict
            >>> t = TreeDict('root')
            >>> t1 = TreeDict('t1')
            >>> t.attach(t1, name = "new_t1", copy = False)
            >>> t1.rootNode()
            TreeDict <root>
            >>> t.new_t1 is t1
            True

        Example 2::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict('root')
            >>> t1 = TreeDict('t1')
            >>> t.attach(t1, copy = True)
            >>> t1.rootNode()
            TreeDict <t1>
            >>> t.t1 is t1
            False
            >>> t.t1.rootNode()
            TreeDict <root>

        Example 3::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict('root')
            >>> t1 = TreeDict('t1', x1 = 1, y1 = 2)
            >>> t2 = TreeDict('t2', x2 = 10, y2 = 20)
            >>> t.a = 1
            >>> t.t1 = t1
            >>> t.attach(t2)
            >>> print t.makeReport()
            a     = 1
            t1    = TreeDict <t1>
            t2.x2 = 10
            t2.y2 = 20
            >>> t.attach(recursive = True)
            >>> print t.makeReport()
            a     = 1
            t1.y1 = 2
            t1.x1 = 1
            t2.x2 = 10
            t2.y2 = 20
            
        """

        if recursive:
            if tree_or_node is not None or name is not None:
                raise TypeError("Setting recursive option requires 'tree_or_node' and 'alt_name' to be None (default).")

            self._recursiveAttach(copy)
            
            return
            
        if tree_or_node is None:
            raise TypeError("String or TreeDict expected for tree_or_node parameter, got NoneType.")

        if type(tree_or_node) is TreeDict:
            self._attach(<TreeDict>tree_or_node, name, copy)
        elif type(tree_or_node) is str:
            p = self.get(tree_or_node)
            if type(p) is not TreeDict:
                raise TypeError("Attempting to attach non-tree node '%s'." % name)
            self._attach(<TreeDict>p, name, copy)
        else:
            raise TypeError("Argument tree_or_node must be a TreeDict or name of existing treedict.")

    
    cdef _attach(self, TreeDict tree, str name, bint copy):

        if tree is None:
            raise TypeError("TreeDict instance expected, got NoneType.")

        cdef TreeDict b
        cdef str attach_name

        # Get the base node to attach into
        if name is None:
            name        = tree._name
            attach_name = tree._name

            if not isValidName(name):
                raise NameError(("Name of tree to be attached in ('%s') " 
                                 "not valid branch name, so alternate name must be given." )
                                % name)
            b = self
        else:
            b = self._getBaseOf(name, (f_dangling_okay | f_create_if_needed | f_atomic_set))
            attach_name = self._shortKeyName(name)

        # Need to do some gymnastics as the dry_run may fail if the
        # name is bad, so set it to the new one, but make sure we set
        # it back when we're done checking.

        cdef str old_name = tree._name
        tree._name = attach_name

        try:
            b._setLocalBranch(tree, f_dry_run)

            if not copy and tree._inPathToRoot(b) or b._inPathToRoot(tree):
                raise ValueError("Attaching to a child or parent node forbidden.")

            if not copy and tree.rootNode() is b.rootNode():
                raise ValueError("Attaching a tree with same root requires copy.")

            if not copy and tree._parent is not None:
                raise ValueError("Tree to be attached (%s) must be copied or be a root tree."
                                 % name)
        finally:
            tree._name = old_name

        if copy:
            tree = tree._copy(False, False)
            
        tree._name = attach_name
        tree._resetParentNode(b)
        b._setLocalBranch(tree, f_already_dryset)


    cdef _recursiveAttach(self, bint copy):

        self._ensureWriteable(None)

        cdef _PTreeNode pn

        for k, pn in self._param_dict.iteritems():
            if pn.isTree():
                pn.tree()._recursiveAttach(copy)
            if pn.isNonBranchTree():
                self._attach(pn.tree(), k, copy)
                
    
    cdef bint _inPathToRoot(self, TreeDict p):
        if self.isRoot():
            return (self is p)
        else:
            if self is p:
                return True
            else:
                return self._parent._inPathToRoot(p)

    cdef void _resetParentNode(self, TreeDict new_parent):
        self._parent = new_parent

    cdef str _shortKeyName(self, str key):
        """
        Returns the name of the object, just not within.
        """
        
        cdef int pos = strrfind(key, '.')
        if pos == -1:
            return key
        else:
            return key[pos+1:]
        
    ################################################################################
    # Methods that manage the flags

    # Freezing
    cpdef bint isFrozen(self):
        """
        Returns True if the current branch is frozen, and False
        otherwise. Like a tuple or other immutable python containers,
        the structure and values in a frozen tree cannot be changed.
        """
        
        return _flagOn(&self._flags, f_is_frozen)

    cdef void _setFrozen(self, bint frozen):
        _setFlag(&self._flags, f_is_frozen, frozen)

    # Dangling
    cpdef bint isDangling(self):
        """
        Returns True if this branch was created implicitly and is
        still dangling, and False otherwise.  Example:

          >>> t = TreeDict()
          >>> b = t.a
          >>> t.a.isDangling()
          True
          >>> t.a.v = 1
          >>> t.a.isDangling()
          False
        """
        return _flagOn(&self._flags, f_is_dangling)

    cdef void _setDangling(self, bint dangling):
        _setFlag(&self._flags, f_is_dangling, dangling)

    # Detached Dangling
    cpdef bint _isDetachedDangling(self):
        return _flagOn(&self._flags, f_is_detached_dangling)

    cdef void _setDetachedDangling(self, bint dangling):
        _setFlag(&self._flags, f_is_detached_dangling, dangling)

    # Registration
    cpdef bint isRegistered(self):
        """
        Returns true if the current tree structure is registered in
        the module-level tree index and can be accessed through the
        `getTree()` function.
        """
        
        return _flagOn(&self._flags, f_is_registered)

    cdef void _setRegisteredFlag(self, bint registered):
        _setFlag(&self._flags, f_is_registered, registered)

    def _numDangling(self):
        return self._n_dangling

    # HasBeenCopied flag
    cdef bint hasBeenCopied(self):
        return _flagOn(&self._flags, f_is_already_copied)

    cdef void _setHasBeenCopiedFlag(self, bint copied):
        _setFlag(&self._flags, f_is_already_copied, copied)

    # Iterator control
    cdef bint isIterReferenced(self):
        return _flagOn(&self._flags, f_one_iterators_referencing)

    cdef void iteratorIncRef(self):

        if not _flagOn(&self._flags, f_one_iterators_referencing):
            _setFlag(&self._flags, f_one_iterators_referencing, True)
            
            if RUN_ASSERTS:
                assert not _flagOn(&self._flags, f_many_iterators_referencing)

        elif not _flagOn(&self._flags, f_many_iterators_referencing):

            if RUN_ASSERTS:
                assert not s_IterReferenceCount in self._aux_dict
            
            self._aux_dict[s_IterReferenceCount] = 2
            _setFlag(&self._flags, f_many_iterators_referencing, True)
        else:
            if RUN_ASSERTS:
                assert s_IterReferenceCount in self._aux_dict
                assert self._aux_dict[s_IterReferenceCount] >= 1

            self._aux_dict[s_IterReferenceCount] += 1
            
    cdef void iteratorDecRef(self):

        if _flagOn(&self._flags, f_many_iterators_referencing):

            if RUN_ASSERTS:
                assert s_IterReferenceCount in self._aux_dict

            n = self._aux_dict[s_IterReferenceCount]

            if n > 2:
                self._aux_dict[s_IterReferenceCount] = n - 1
            else:
                
                if RUN_ASSERTS:
                    assert self._aux_dict[s_IterReferenceCount] == 2
                    
                del self._aux_dict[s_IterReferenceCount]
                
                _setFlag(&self._flags, f_many_iterators_referencing, False)
        else:

            if RUN_ASSERTS:
                assert _flagOn(&self._flags, f_one_iterators_referencing)
                assert s_IterReferenceCount not in self._aux_dict
                
            _setFlag(&self._flags, f_one_iterators_referencing, False)

    def _iteratorRefCount(self):
        if _flagOn(&self._flags, f_many_iterators_referencing):
            return self._aux_dict[s_IterReferenceCount]
        elif _flagOn(&self._flags, f_one_iterators_referencing):
            return 1
        else:
            return 0
            
    ################################################################################
    # Methods that return information about the tree

    cpdef TreeDict parentNode(self):
        """
        Returns the parant node of the current node.
        """
        return self._parent
    
    cpdef TreeDict rootNode(self):
        """
        Returns the root node of current tree.
        """

        if self._parent is None:
            return self
        else:
            return self._parent.rootNode()

    cpdef bint isRoot(self):
        """
        Returns True if the current node is the root of the tree, and
        False otherwise.
        """
        return self._parent is None

    cpdef bint isEmpty(self):
        """
        Returns True if the current branch has no branches or leaves.
        (Note that dangling branches don't count, but empty branches do.)
        """
        
        if len(self._param_dict) == 0:
            return True

        for b in self._branches:
            if not (<TreeDict>b).isDangling():
                return False
        
        return len(self._branches) == len(self._param_dict)


    cpdef bint nodeInSameTree(self, TreeDict node):
        """
        Tests whether `node` is a node in the current tree.  This is
        equal to testing whether they have the same root node.  Note
        that TreeDict instances stored in the tree but not attached
        are not considered nodes of the current tree.
        """

        return (self.rootNode() is node.rootNode())


    cpdef interactiveTree(self):
        """
        Returns an interactive version of the TreeDict for use in an
        interpreted shell.  While the branch, node, and leaf values in
        a TreeDict instance are stored in an internal dictionary, they
        are the attributes in an interactive TreeDict.  This allows
        one to use tab completion in Ipython to interact with the tree
        more easily.

        The `treeDict()` method of the interactive tree returns the
        original TreeDict instance.

        Example::

            In [3]: from treedict import TreeDict

            In [4]: t = TreeDict()

            In [5]: t.set('alpha.beta', 1, beta = 1, gamma = 2)

            In [6]: ti = t.interactiveTree()

            In [7]: ti.alpha.

            ti.alpha.__class__             ti.alpha.__eq__                ti.alpha.__init__              ti.alpha.__reduce_ex__         ti.alpha.__str__               ti.alpha._setAttrDirect
            ti.alpha.__delattr__           ti.alpha.__format__            ti.alpha.__module__            ti.alpha.__repr__              ti.alpha.__subclasshook__      ti.alpha.beta
            ti.alpha.__dict__              ti.alpha.__getattribute__      ti.alpha.__new__               ti.alpha.__setattr__           ti.alpha.__weakref__           ti.alpha.treeDict
            ti.alpha.__doc__               ti.alpha.__hash__              ti.alpha.__reduce__            ti.alpha.__sizeof__            ti.alpha._original_param_tree  

            In [7]: ti.alpha.treeDict() is t
            Out[7]: False

            In [8]: ti.alpha.treeDict() is t.alpha
            Out[8]: True

            In [9]: t.
            t.__call__                  t.__getattr__               t.__pyx_vtable__            t._getSettingOrderPosition  t.fromkeys                  t.isRoot                    t.pop
            t.__class__                 t.__getattribute__          t.__reduce__                t._isDetachedDangling       t.get                       t.items                     t.popitem
            t.__contains__              t.__getitem__               t.__reduce_ex__             t._iteratorRefCount         t.getClosestKey             t.iterbranches              t.rootNode
            t.__copy__                  t.__gt__                    t.__repr__                  t._numDangling              t.has_key                   t.iteritems                 t.set
            t.__deepcopy__              t.__hash__                  t.__setattr__               t.attach                    t.hash                      t.iterkeys                  t.setFromString
            t.__delattr__               t.__init__                  t.__setitem__               t.branchName                t.interactiveTree           t.itervalues                t.setdefault
            t.__delitem__               t.__le__                    t.__sizeof__                t.branches                  t.isDangling                t.keys                      t.size
            t.__doc__                   t.__len__                   t.__str__                   t.clear                     t.isEmpty                   t.makeBranch                t.treeName
            t.__eq__                    t.__lt__                    t.__subclasshook__          t.copy                      t.isFrozen                  t.makeReport                t.update
            t.__format__                t.__ne__                    t._branchNameOf             t.dryset                    t.isMutable                 t.nodeInSameTree            t.values
            t.__ge__                    t.__new__                   t._fullNameOf               t.freeze                    t.isRegistered              t.parentNode                

            In [9]: t.
            """

        return InteractiveTreeDict(self)

    def __call__(self, *args, **kwargs):
        if self.isDangling():
            raise TypeError('<%s> not a TreeDict method or branch, illegally called.'
                            % self._branchName(False, True))
        else:
            self._setAll(args, kwargs, False)
            return self
        
    def __repr__(self):
        if self.isDangling():
            return "Dangling TreeDict <%s>" % self._branchName(False, True)
        else:
            return "TreeDict <%s>" % self._branchName(False, True)

    cpdef str _fullNameOf(self, str key):
        """
        Returns the full name of `key`, including the root name of the tree.
        """

        checkKeyNotNone(key)
        return self._branchName(False, True) + "." + key

    cpdef str _branchNameOf(self, str key):
        """
        Returns the full name of `key`, not including the root name of the tree.
        """

        return catNames(self._branchName(False, False), key)

    cpdef str treeName(self):
        """
        Returns the name of the tree (defined as the name of the root
        node).

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict('mytree')
            >>> t.treeName()
            'mytree'
            >>> t.makeBranch('a.b.c')
            TreeDict <mytree.a.b.c>
            >>> t.a.b.treeName()
            'mytree'
        """
        
        return self.rootNode()._branchName(True, True)

    cpdef str branchName(self, bint add_path = False, bint add_tree_name = False):
        """
        Returns the name of the branch.

        If `add_path` is False, returns only the local branch name;
        otherwise, it returns the full name of the branch to the root.
        If `add_tree_name` is True, the tree name is included in the
        path; if `add_path` is False, `add_tree_name` is ignored.

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict('root')
            >>> t.makeBranch("a.b.c")
            TreeDict <root.a.b.c>
            >>> t.a.b.c.branchName()
            'c'
            >>> t.a.b.c.branchName(add_path = True)
            'a.b.c'
            >>> t.a.b.c.branchName(add_path = True, add_tree_name = True)
            'root.a.b.c'
        """

        return self._branchName(not add_path, add_tree_name)

    cdef str _branchName(self, bint local_only, bint include_tree_name):
        # Now a little trickier since we have to handle empty tree
        # names properly, so we can't special case ''

        cdef TreeDict p = self.parentNode()
        cdef str base

        if p is None:
            if include_tree_name:
                return self._name
            else:
                return ''
        else:
            if local_only:
                return self._name

            if p.isRoot():
                if include_tree_name:
                    return p._name + '.' + self._name
                else:
                    return self._name
            else:
                return p._branchName(False, include_tree_name) + '.' + self._name

    def makeReport(self, bint recursive = True, bint add_path = False, bint add_tree_name = True):
        """
        Creates a report listing all values present in this node,
        formatted as ``[branch].name = value``.  Parameters are
        reported in the exact order they were first set.

        If `add_path` is True, then the full path of each value is
        given instead of just the path from the current node.  If, in
        addition, `add_tree_name` is True, the name of the tree is
        prepended to the path.  (Note: if self.treeName() is not a
        valid python variable name, then it is enclosed in single
        quotes, and if it is '', it is omitted.) `add_tree_name` is
        ignored if `add_path` is False.

        If recursive is True, then all values in this node and in all
        subnodes are listed; otherwise, only local values are
        returned.

        Example::

            >>> from treedict import TreeDict
            >>> 
            >>> t = TreeDict("mytree")
            >>> t.x = 1
            >>> t.y = 2
            >>> t.a.z = [1,2,3]
            >>> t.a.y = {1 : 2}
            >>> t.b.x = "hello"
            >>> t.a.x = None
            >>> t.b.z = 2
            >>> 
            >>> print t.makeReport()
            x   = 1
            y   = 2
            a.z = [1, 2, 3]
            a.y = {1: 2}
            a.x = None
            b.x = 'hello'
            b.z = 2
            >>> print t.a.makeReport()
            z = [1, 2, 3]
            y = {1: 2}
            x = None
            >>> print t.a.makeReport(add_path = True)
            mytree.a.z = [1, 2, 3]
            mytree.a.y = {1: 2}
            mytree.a.x = None
            >>> print t.a.makeReport(add_path = True, add_tree_name = False)
            a.z = [1, 2, 3]
            a.y = {1: 2}
            a.x = None
        """


        if add_path and add_tree_name:
            tn = self.treeName()

        prepend_list = [((tn if isValidName(tn) else '%s' % tn)
                         if add_path and add_tree_name and len(tn) != 0 else ""),
                        self.branchName(False, False) if add_path else ""]

        cdef str prepend_string = ".".join([k for k in prepend_list if len(<str>k) != 0])

        if len(prepend_string) != 0:
            prepend_string += '.'

        value_list = [(self._getSettingOrderPosition(k), prepend_string + k, v)
                      for k, v in self.iteritems(recursive, 'none')]

        if len(value_list) == 0:
            return ""

        variable_space = max([len(k) for o,k,v in value_list])

        return "\n".join([ (k + " "*(variable_space - len(k)) + " = " + repr(v))
                           for (o, k, v) in sorted(value_list)])


    cpdef tuple _getSettingOrderPosition(self, str name):

        # make sure it's present
        self._get(name, False)

        cdef list key_list = name.split('.')
        cdef TreeDict t = self
        cdef list order = [None]*len(key_list)
        cdef size_t idx
        cdef _PTreeNode pn

        for idx, k in enumerate(key_list):
            pn = t._getLocalPTNode(k)

            order[idx] = pn.orderPosition()

            if idx < len(key_list) - 1:
                t = pn.tree()
        
        return tuple(order)

    ################################################################################
    # Methods relating to retrieving values and existance testing


    ##############################
    # First the methods that interface to the outside world

    def __getattr__(self, str k):

        # Different from get in that we handle non-existant branches
        # by creating a new node and flagging it as tentative
        
        # The _getattr__called is to detect programming errors

        if _flagOn(&self._flags, f_getattr_called):
            raise Exception("Programming Error: Multiple (recursive?) __getattr__ with '%s'" % k)


        cdef flagtype gsp = (f_dangling_okay 
                             | (f_create_if_needed if not self.isFrozen() else 0))

        cdef bint allow_dangling_nodes = False if self.isFrozen() else True

        try:
            _setFlagOn(&self._flags, f_getattr_called)

            if self._existsLocal(k, allow_dangling_nodes):
                return self._getLocal(k, allow_dangling_nodes)
            elif not self.isFrozen():
                return self._newLocalBranch(k, f_create_if_needed | f_create_dangling)
            else:
                self._raiseAttributeError(k)

            #except TypeError:
            #    raise AttributeError("branch/value/method '%s' does not exist in tree/branch '%s' (Frozen)." % (k, self.branchName()))

        finally:
            _setFlagOff(&self._flags, f_getattr_called)

    def __getitem__(self, key):
        if type(key) is not str:
            raise TypeError("Indexing keys must be strings, not %s" % repr(type(key)))
        
        return self.get(key)
    
    cpdef get(self, str key, default_value = _NoDefault):
        """
        Returns the value/branch associated with the key `key`.  If
        `default_value` is given, and the `key` is not present, then
        `default_value` is returned; otherwise, a KeyError is raised.

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict(x = 1)
            >>> t.get("x")
            1
            >>> t.get("y")
            Traceback (most recent call last):
             File "<stdin>", line 1, in <module>
             File "treedict.pyx", line 1995, in treedict.treedict.TreeDict.get (treedict/treedict.c:17360)
             File "treedict.pyx", line 2010, in treedict.treedict.TreeDict.get (treedict/treedict.c:17249)
            KeyError: 'root.y'
            >>> t.get("y", [])
            []

        """

        checkKeyNotNone(key)

        try:
            return self._get(key,False)
        except KeyError:
            if default_value is not _NoDefault:
                return default_value
            else:
                raise KeyError(self._fullNameOf(key))

    ################################################################################
    # existence checks

    def __contains__(self, k):
        return self.exists(k)

    def has_key(self, key):
        """
        Returns True if `key` is in the tree and False otherwise.

        This is analogous to the `has_key` dict method.
        """

        return self.exists(key)

    cdef bint exists(self, k):
        if type(k) is not str or k is None:
            return False
        else:
            return self._exists(<str>k, False)


    ##############################
    # Now the core methods for retrieving PTNodes; the others are
    # based on these

    cdef _PTreeNode _getPTNode(self, str k):
        cdef TreeDict p
        cdef _PTreeNode pn
        cdef int pos = strfind(k, ".")
        
        if pos == -1:
            return self._getLocalPTNode(k)
        else:
            pn = self._getLocalPTNode(k[:pos])

            if pn is None or not pn.isTree():
                return None
            
            return pn.tree()._getPTNode(k[pos+1:])

    cdef _PTreeNode _getLocalPTNode(self, str k):
    
        try:
            return (<_PTreeNode> self._param_dict[k])

        except KeyError:
            if len(k) == 0:
                return None

            elif k[0] in ['$', '@']:

                # See if there's a special method associated with this 
                try:
                    f = _special_functions[k]
                except KeyError:
                    return None

                try:
                    v = f(self)
                except _SpecialFunctionNotAvailable:
                    return None
                
                return newPTreeNode(self, v, 0)

            else:
                return None

    ##############################
    # General value retrieval / existance checking

    cdef _get(self, str k, bint dangling_okay):
        cdef _PTreeNode pn = self._getPTNode(k)

        if pn is None or (not dangling_okay and pn.isDanglingBranch()):
            raise KeyError
        else:
            return pn.value()

    cdef _getLocal(self, str k, bint dangling_okay):
        cdef _PTreeNode pn = self._getLocalPTNode(k)

        if pn is None or (not dangling_okay and pn.isDanglingBranch()):
            raise KeyError
        else:
            return pn.value()
        
    cdef bint _exists(self, str k, bint dangling_okay):

        cdef _PTreeNode pn = self._getPTNode(k)

        if pn is None:
            return False
        elif dangling_okay:
            return True
        else:
            return not pn.isDanglingTree()

    cdef bint _existsLocal(self, str k, bint dangling_okay):
        cdef _PTreeNode pn
    
        if dangling_okay:
            return (k in self._param_dict)
        else:
            pn = self._getLocalPTNode(k)

            if pn is None:
                return False
            else:
                return not pn.isDanglingTree()


    ########################################
    # Master Functions for getting branches

    cdef TreeDict _getLocalBranch(self, str k, flagtype gsp):
        cdef _PTreeNode pn

        if self._existsLocal(k, True):
            pn = self._getLocalPTNode(k)

            if not pn.isBranch():
                if (gsp & f_ignore_nonbranches):
                    if (gsp & f_create_if_needed):
                        return self._newLocalBranch(k, gsp)
                    else:
                        return None
                else:
                    raise TypeError("Node \"%s\" is not a branch as requested."
                                    % self._fullNameOf(k) )

            if pn.isDanglingBranch() and not (gsp & f_dangling_okay):
                return None
        
            return pn.tree()

        elif (gsp & f_create_if_needed):
            return self._newLocalBranch(k, gsp)

        else:
            return None
    

    cdef TreeDict _getBranch(self, str k, flagtype gsp):

        cdef int pos = strfind(k, '.')
        cdef str k1
        cdef TreeDict p

        if pos != -1:
            p = self._getLocalBranch(k[:pos], gsp)
            return p._getBranch(k[pos+1:], gsp)
        else:
            return self._getLocalBranch(k, gsp)


    ########################################
    # Convenience wrapper functions for above functions

    cdef TreeDict _getBaseOf(self, str key, flagtype gsp):
        cdef int pos = strrfind(key, '.')
        
        if pos == -1:
            return self
        else:
            return self._getBranch(key[:pos], gsp)

    cdef TreeDict _getBottomNode(self, str key):
        # When we start supporting relative links, this will become
        # more useful; for now we don't.

        return self


    ################################################################################
    # Methods relating to branch creation and manipulation

    def makeBranch(self, str name, bint only_new = False):
        """
        Explicitly creates a branch named `name` and returns it.

        If `only_new` is True, and `name` is already present, a
        ValueError is raised. Otherwise, a ValueError is raised only
        if `name` refers to a non-branch value, and an existing branch
        is returned if present.
        """
        
        checkKeyNotNone(name)

        if self._exists(name, False):
            if not only_new:
                v = self._get(name, False)

                if type(v) is TreeDict:
                    return v
                else:
                    raise ValueError("'%s' already exists as non-branch key; cannot create new branch."
                                     % name)
            else:
                raise ValueError("'%s' already exists; cannot create new branch."
                                 % name)

        cdef flagtype gsp = (f_dangling_okay | f_create_if_needed | f_atomic_set | f_create_dangling)

        cdef TreeDict b = self._getBranch(name, gsp)
        
        b._attachDanglingSelf()

        if RUN_ASSERTS:

            assert not b.isDangling()

            if '.' not in name:
                assert not (<_PTreeNode>self._param_dict[name]).isDanglingBranch()

        return b
            
    cdef TreeDict _newLocalBranch(self, str k, flagtype gsp):
        
        cdef TreeDict b

        b = newTreeDict(k, False)

        b._parent = self
        b._flags = self._flags & f_newbranch_propegating_flags

        if gsp & f_atomic_set:
            b._setDangling(True)
            b._setDetachedDangling(True)

            if RUN_ASSERTS:
                n_d = self._n_dangling

            self._setLocalBranch(b, f_dry_run)

            if RUN_ASSERTS:
                assert n_d == self._n_dangling

        else:
            b._setDangling(True if (gsp & f_create_dangling) else False)
            self._setLocalBranch(b, 0)
            
        return b


    cdef _setLocalBranch(self, TreeDict tree, flagtype gsp):

        self._setLocal(tree._name, tree, gsp)
        
        if not (gsp & f_dry_run):

            if RUN_ASSERTS:
                assert tree.parentNode() is self

            if RUN_ASSERTS:
                for t in self._branches:
                    assert tree is not t

            self._branches.append(tree)

    cdef _attachDanglingSelf(self):
        if not self.isDangling():
            return

        cdef TreeDict p = self.parentNode()

        if RUN_ASSERTS:
            assert p is not None

        # See if the base needs to be attached
        p._attachDanglingSelf()

        self._setDangling(False)
                
        if RUN_ASSERTS:
            assert not self.isDangling()
        
        if self._isDetachedDangling():
            self._setDetachedDangling(False)
            p._setLocalBranch(self, f_already_dryset)
        else:
            if RUN_ASSERTS:
                assert p._n_dangling != 0

            p._n_dangling -= 1

    ###############################################################################
    # Equality comparisons

    def __richcmp__(p1, p2, int t):

        cdef bint are_equal 

        if type(p1) is not TreeDict:
            if RUN_ASSERTS:
                assert type(p2) is TreeDict

            if isinstance(p1, dict):
                are_equal = (dict((<TreeDict>p2).iteritems()) == p1)
            else:
                are_equal = False

        elif type(p2) is not TreeDict:
            if RUN_ASSERTS:
                assert type(p1) is TreeDict

            if isinstance(p2, dict):
                are_equal = (dict((<TreeDict>p1).iteritems()) == p2)
            else:
                are_equal = False

        elif p1 is None or p2 is None:
            are_equal = False

        else:
            are_equal = (<TreeDict>p1)._isEqual(<TreeDict>p2)

        if t == 2:              # ==
            return are_equal
        elif t == 3:            # !=
            return not are_equal
        else:
            return False

    cdef bint _isEqual(self, TreeDict p):

        cdef size_t i

        if p is None:
            return False

        # The tricky thing is that equality testing needs to ignore
        # any dangling nodes, as they don't really exist...

        # Attempt reject based on other equality measures

        if self.isDangling() != p.isDangling():
            return False
        
        if (len(self._param_dict) - self._n_dangling
            != len(p._param_dict) - p._n_dangling):
            return False

        if self._n_mutable != p._n_mutable:
            return False

        if self._getImmutableItemsHash() != p._getImmutableItemsHash():
            return False

        cdef _PTreeNode pn1, pn2

        for k, pn1 in self._param_dict.iteritems():

            if pn1.isImmutable():
                continue

            if pn1.isDanglingBranch(): 
                continue

            try:
                pn2 = p._param_dict[k]
            except KeyError:
                return False

            if not pn1.isEqual(pn2):
                return False

        return True


    #################################################################################
    # hash stuff

    def __hash__(self):
        if not self.isFrozen():
            raise TypeError("Only frozen trees are python hashable.")

        if self.isMutable():
            s = self._firstMutableType()
            if s is not None:
                raise TypeError("Node '%s' (and possibly more) not hashable." % s)

        return hash(self._self_immutable_hash())

    cdef str _firstMutableType(self):
        cdef _PTreeNode pn
        cdef str s

        # Mutable tests; if there are no mutable items, then go with

        for k, pn in self._param_dict.iteritems():
            if pn.isMutable() or (pn.isTree() and pn.tree().isMutable()):
                return k
            
            if pn.isBranch():
                s = pn.tree()._firstMutableType()
                if s is not None:
                    return k + "." + s

        return None

    cpdef bint isMutable(self):
        """
        Returns true if the current tree is frozen and contains no
        mutable values, otherwise returns False.
        """

        # Just like the previous version, but doesn't take as long
        # cause it just does quick checks

        if not self.isFrozen():
            return True

        if self._n_mutable != 0:
            return True
        
        cdef _PTreeNode pn
        
        for k, pn in self._param_dict.iteritems():
            if pn.isTree() and pn.tree().isMutable():
                return True

        return False

    ########################################
    # Hashes that handle mutability, for things like database lookups, etc.
    
    cpdef hash(self, str key=None, bint add_name = False, keys=None):
        """
        Returns a hash of the current tree / branch and all
        sub-branches.  The hash is based on an md5 hash, and can be
        used as a unique identifier for the tree and its values.

        If `key` is given, the hash of the branch/value `key` is
        returned.

        If `add_name` is True, then the name of the local tree is
        included in the hash.  That is, two branches have the same
        hash only if they also have the same name, otherwise this is
        dropped.

        If `keys` is given, it must be an iterable returning keys, and
        the hash is taken only over these keys.

        One usecase for this method is for caching values; if the
        input parameters for a calculation are all contained in a
        TreeDict, then the results can be cached by the hash of that
        paramtree to avoid repeating calculations.
        
        Unrecognized value types are first pickled, and then the hash
        is taken over the pickled string.  If this value is immutable,
        this hash is cached for future reference.

        Hashes have the following properties:

        - Hashes of frozen trees and hashes of unfrozen trees are
          equal, i.e. the frozenness is not considered in the hash.
          
        - The hash of a tree with separate, non-branch TreeDict
          instances in the tree will be different from the hash of a
          similar tree with the TreeDicts set as branches.


        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.set('br.x', 1, 'br.c.y', 2, x = 1, y = 2)
            >>> t.hash()
            'ypXSDHXSEg'
            >>> t.hash('br')
            '8uMbRZ88dg'
            >>> t.br.hash()
            '8uMbRZ88dg'
            >>> t.br.hash(add_name = True)
            'br-8uMbRZ88dg'
            >>> t.hash('x')
            'xMpCOKC5I4'
            >>> t.hash(keys = ['x', 'y'])
            'wgrU12pd1m'
            >>> t.hash('nothere')
            Traceback (most recent call last):
             File "<stdin>", line 1, in <module>
             File "treedict.pyx", line 2522, in treedict.treedict.TreeDict.hash (treedict/treedict.c:21606)
             File "treedict.pyx", line 2573, in treedict.treedict.TreeDict.hash (treedict/treedict.c:21484)
            KeyError: 'root.nothere'
        """
        try:
            if add_name:
                if key is not None:
                    return self._reportable_hash(self._shortKeyName(key), self._item_hash(key))
                elif keys is not None:
                    raise TypeError("'add_name=True' not available for set of keys.")
                else:
                    return self._reportable_hash(self._name, self._self_hash())            
            else:
                if key is not None:
                    return self._item_hash(key)
                elif keys is not None:
                    key_set = keys if type(keys) is set else set(keys)

                    if len(<set>key_set) == self._size(True, i_BranchMode_None):
                        return self._self_hash()
                    else:
                        return self._item_set_hash(<set>key_set)
                else:
                    return self._self_hash()
        except Exception, e:
            raise e
            
    cdef str _reportable_hash(self, str key, str digest):
        return key + "-" + digest

    cdef str _encode_hash(self, str s):
        return (b64encode(s).replace('=', '').replace('+', '').replace('/',''))[:10]

    # Hash for a list of keys
    cdef str _item_set_hash(self, set keys):
        cdef str key
        cdef _PTreeNode pn

        h = md5()
        hf = getattr(h, 'update')
        
        for key in sorted(keys):
            
            pn = <_PTreeNode> self._getPTNode(key)
            if pn is None:
                raise KeyError(self._fullNameOf(key))
            
            pn.runFullHash(hf)

        return self._encode_hash(h.digest())

    # Hash for specific item
    cdef str _item_hash(self, str key):

        cdef _PTreeNode pn = <_PTreeNode> self._getPTNode(key)

        if pn is None:
            raise KeyError(self._fullNameOf(key))
        
        return self._encode_hash(pn.fullHash())

    # Hash for a whole tree
    cdef str _self_hash(self):
        h = md5()
        self._runFullHash(getattr(h, 'update'))
        return self._encode_hash(h.digest())

    # Hash for a whole tree
    cdef str _self_immutable_hash(self):
        h = md5()
        self._runImmutableHash(getattr(h, 'update'))
        return self._encode_hash(h.digest())

    ##################################################
    # Now methods for actually running the hashes

    # The sorting in the next two functions is awkward; because of how
    # python dicts implement the hash lookup, we have no gaurantees
    # that keys with the same hash will come out in the same way.
    # Thus we need to do this sort to ensure proper order.

    cdef _runFullHash(self, hf):
        
        if self.isDangling():
            raise TypeError("Dangling nodes not hashable.")

        hf(self._getImmutableItemsHash())

        # This takes care of all the mutable items
        cdef _PTreeNode pn

        for k, pn in sorted(self._param_dict.iteritems()):
            if not pn.isImmutable() and not pn.isDanglingTree():
                self._update_hash_with_key(hf, k)
                self._update_hash_with_context(hf, pn)
                pn.runFullHash(hf)

    cdef _runImmutableHash(self, hf):
        if self.isDangling():
            raise TypeError("Dangling nodes not hashable.")

        # This takes care of all the immutable local values
        hf(self._getImmutableItemsHash())

        cdef TreeDict b
        cdef _PTreeNode pn
        
        for k, pn in sorted(self._param_dict.iteritems()):
            if pn.isBranch() and not pn.isDanglingBranch():
                self._update_hash_with_key(hf, k)
                self._update_hash_with_context(hf, pn)
                pn.runImmutableHash(hf)

        
    # Now going back on the immutable hash cases
    cdef str _getImmutableItemsHash(self):
        cdef _PTreeNode pn
        cdef str hs
        
        if self.isDangling():
            raise TypeError("Dangling nodes not hashable.")

        if s_immutable_items_hash not in self._aux_dict:
            h = md5()
            hf = getattr(h, 'update')

            for k, pn in sorted(self._param_dict.iteritems()):
                if pn.isImmutable():
                    self._update_hash_with_key(hf, k)
                    self._update_hash_with_context(hf, pn)
                    pn.runImmutableHash(hf)

            hs = h.hexdigest()
            self._aux_dict[s_immutable_items_hash] = hs
            return hs

        return <str>self._aux_dict[s_immutable_items_hash]

    cdef _update_hash_with_key(self, hf, str key):
        hf("$S$")
        hf(key)
        hf("$E$")

    cdef _update_hash_with_context(self, hf, _PTreeNode pn):
        # Any context-based information
        if pn.isBranch():
            hf("$BRANCH$")


    ################################################################################
    # All functions dealing with caching, tracking, etc.

    cdef void _keyDeleted(self, str key, _PTreeNode pn):
        cdef size_t i
        
        if pn.isMutable():
            self._n_mutable -= 1

            if RUN_ASSERTS:
                assert self._n_mutable >= 0

        elif pn.isImmutable():
            self._resetImmutableHashes()

        elif pn.isBranch():
            v = pn.value()
            for i, b in enumerate(self._branches):
                if b is v:
                    del self._branches[i]
                    break
            
        if pn.isDanglingBranch():
            self._n_dangling -= 1
            
    cdef _keyInserted(self, str key, _PTreeNode pn):
        cdef TreeDict p

        if pn.isMutable():
            self._n_mutable += 1
        elif pn.isImmutable():
            self._resetImmutableHashes()
            
        # Now if we are a dangling node, inserting a key turns us into
        # a non-dangling node...
        if pn.isDanglingBranch():
            
            # Only count if we need to; this would be an issue with links
            p = pn.tree()
            
            self._n_dangling += 1
            
        else:
            self._attachDanglingSelf()

    cdef void _resetImmutableHashes(self):
        if s_immutable_items_hash in self._aux_dict:
            del self._aux_dict[s_immutable_items_hash]

    ################################################################################
    # Methods for copying the tree
    def __copy__(self):
        return self._copy(False, False)

    def __deepcopy__(self, m={}):
        return self._copy(True, False)

    def copy(self, bint deep=False, bint freeze=False):
        """
        Returns a copy of the current tree.  If `deep` is true, then
        all the values in the leaves are also copied, otherwise the
        entire tree structure is copied but not the values.  If
        `freeze` is true, then the returned tree is frozen.
        """

        return self._copy(deep, freeze)

    def importFrom(self, TreeDict source_tree, bint copy_deep=False, overwrite_existing = True):
        """
        Copies all the branches and values from a source branch/tree
        `source_tree` into the current branch.

        If `copy_deep` is True, then copies are made of all the values
        held in the source tree, otherwise, only the tree structure
        and references to the values are copied (default).

        If `overwrite_existing` is True (default), then conflicting
        values in the local tree are overwritten by the corresponding
        values in the source tree.  If `overwrite_existing` is False,
        all local values already present are preserved.
        """

        cdef dict d = dict(source_tree._getIter(True, i_BranchMode_All, i_Items))
        cdef set existing_items
        

        if overwrite_existing:
            
            if copy_deep:
                for k, v in d.iteritems():
                    d[k] = deepcopy_f(v)

            self._setAll(None, d, False)
            
        else:

            # First see if there will be any problems, so do a dryset
            for k, v in d.items():
                if not self._exists(<str>k, False):
                    self._dryset(<str>k, v)
                else:
                    del d[k]
                    
            # don't make unneccesary copies 
            if copy_deep:
                for k, v in d.iteritems():
                    d[k] = deepcopy_f(v)

            # Then go ahead and set them
            for k, v in d.iteritems():
                self._set(<str>k, v, True)

                    
    cdef TreeDict _copy(self, bint deep, bint frozen):
        # Wraps the recursive function _recursiveCopy() that 
    
        if self.isDangling():
            self._raiseErrorAtFirstNonDanglingBranch(True)

        cdef TreeDict p
        cdef str tn, bn, newbn

        p = self._recursiveCopy(deep)

        if frozen:
            p.freeze()

        self._clearHasBeenCopiedFlags()
        
        return p

    cdef _clearHasBeenCopiedFlags(self):
        if self.hasBeenCopied():
            del self._aux_dict["copied_node"]

        self._setHasBeenCopiedFlag(False)

        cdef _PTreeNode pn

        for pnv in self._param_dict.itervalues():
            pn = <_PTreeNode>pnv

            if pn.isTree():
                pn.tree()._clearHasBeenCopiedFlags()

    cdef TreeDict _recursiveCopy(self, bint deep):
        # The recursive version of the above;
    
        if self.hasBeenCopied():
            return self._aux_dict["copied_node"]

        cdef TreeDict p = newTreeDict(self._name, False)
        cdef _PTreeNode pn, new_pn

        assert p._name == self._name
        
        # In copying, the tree doesn't preserve parental relation.
        
        p._parent = None
        p._param_dict = {}
        p._setFrozen(False)
        
        p._flags = self._flags & f_copybranch_propegating_flags

        p._n_dangling = 0
        p._n_mutable = self._n_mutable
        p._next_item_order_position = self._next_item_order_position

        for k, pn in self._param_dict.iteritems():

            if pn.isDanglingBranch():
                continue

            new_pn = self._copyValue(p, pn, deep)

            p._param_dict[k] = new_pn
            p._keyInserted(k, new_pn)

        p._reset_branches()

        self._aux_dict["copied_node"] = p
        self._setHasBeenCopiedFlag(True)

        return p
     

    cdef _copyValue(self, TreeDict parent, _PTreeNode pn, bint deep):
        cdef TreeDict p

        if pn.isTree():
            p = pn.tree()._recursiveCopy(deep)

            if pn.isBranch():
                p._parent = parent

            return newPTreeNodeExact(p, pn.type(), pn.orderPosition())
        else:
            if deep:
                return newPTreeNodeExact(
                    deepcopy_f(pn.value()),
                    pn.type(), pn.orderPosition())
            else:
                return newPTreeNodeExact(pn.value(),
                    pn.type(), pn.orderPosition())
          

    cdef _reset_branches(self):
        self._branches = [(<_PTreeNode> pn).value() for pn in self._param_dict.itervalues()
                          if (<_PTreeNode> pn).isBranch()]

    ################################################################################
    # Methods relating to pickling / unpickling 

    def __reduce__(self):
        return (_TreeDict_unpickler,
                (self._name, self._param_dict, self._flags,
                 self._n_mutable, self._next_item_order_position, self._n_dangling) )
    

    ################################################################################
    # Methods relating to size and the like

    def __len__(self):
        return self._size(True, i_BranchMode_None)

    def size(self, bint recursive = True, str branch_mode = 'none'):
        """
        Returns a count of values in the tree.  If recursive is True,
        then it counts all nodes in this branch and in all subtrees,
        according to the branch_mode policy.

        If branch_mode is 'none' (default), only the values are counted.

        If branch_mode is 'all', all nodes and all values in the current
        tree are counted.

        If branch_mode is 'only', only the branches are counted.

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
            >>> print t.makeReport()
            b.x   = 1
            b.c.y = 2
            x     = 1
            >>> t.size()
            3
            >>> t.size(recursive=False)
            1
            >>> t.size(recursive=False, branch_mode='none')
            1
            >>> t.size(recursive=False, branch_mode='only')
            1
            >>> t.size(recursive=False, branch_mode='all')
            2
            >>> t.size(recursive=True, branch_mode='only')
            2
            >>> t.size(recursive=True, branch_mode='all')
            5
            
        """

        return self._size(recursive, self._getBranchMode(branch_mode))

    cdef size_t _local_size(self, int branch_mode):
        if branch_mode == i_BranchMode_Only:
            return len(self._branches) - self._n_dangling
        elif branch_mode == i_BranchMode_All:
            return len(self._param_dict) - self._n_dangling
        elif branch_mode == i_BranchMode_None:
            return len(self._param_dict) - len(self._branches)
    
    cdef size_t _size(self, bint recursive, int branch_mode):
        
        cdef size_t n
        cdef TreeDict b

        if recursive:
            n = self._local_size(branch_mode)

            for b in self._branches:
                if not b.isDangling():
                    n += b._size(recursive, branch_mode)

            return n
        else:
            return self._local_size(branch_mode)


    ################################################################################
    # Methods relating to iterating over values 

    cdef _getBranchMode(self, branch_mode):
        # This function returns an object so it can raise exceptions;
        # it gets converted later anyway.

        if branch_mode is None:
            return i_BranchMode_None

        if type(branch_mode) is not str:
            raise TypeError(_branch_mode_error_msg)

        try:
            return _branch_mode_lookup[strlower(branch_mode)]
        except KeyError:
            raise TypeError(_branch_mode_error_msg)

    cdef TreeDictIterator _getIter(self, bint recursive, int branch_mode, int valuetype):
        return newTreeDictIterator(self, recursive, branch_mode, valuetype)

    cpdef TreeDictIterator iteritems(self, bint recursive = True, branch_mode = 'none'):
        """
        Returns an iterator that returns (key, value) pairs.  If
        recursive is True, then it iterates through all nodes in this
        branch and in all subtrees.  Keys are returned with their full
        path names, e.g. 'foo.bar'.

        If branch_mode is 'none' (default), the branches are ignored
        and all the items associated with values are returned.

        If branch_mode is 'all', all items in the current tree
        are returned.

        If branch_mode is 'only', then only the branches are returned.

        Example::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
            >>> print t.makeReport()
            b.x   = 1
            b.c.y = 2
            x     = 1
            >>> list(t.iteritems())
            [('x', 1), ('b.x', 1), ('b.c.y', 2)]
            >>> list(t.iteritems(recursive=False))
            [('x', 1)]
            >>> list(t.iteritems(recursive=False, branch_mode='none'))
            [('x', 1)]
            >>> list(t.iteritems(recursive=False, branch_mode='only'))
            [('b', TreeDict <root.b>)]
            >>> list(t.iteritems(recursive=False, branch_mode='all'))
            [('x', 1), ('b', TreeDict <root.b>)]
            >>> list(t.iteritems(recursive=True, branch_mode='only'))
            [('b', TreeDict <root.b>), ('b.c', TreeDict <root.b.c>)]
            >>> list(t.iteritems(recursive=True, branch_mode='all'))
            [('x', 1), ('b', TreeDict <root.b>), ('b.x', 1), ('b.c', TreeDict <root.b.c>), ('b.c.y', 2)]
        """

        return self._getIter(recursive, self._getBranchMode(branch_mode), i_Items)

    cpdef TreeDictIterator itervalues(self, bint recursive = True, branch_mode = 'none'):
        """
        Returns an iterator that returns values in the tree.  If
        recursive is True, then it iterates through all nodes in this
        branch and in all subtrees.

        If branch_mode is 'none' (default), the branches are ignored
        and all the items associated with values are returned.

        If branch_mode is 'all', all items in the current tree
        are returned.

        If branch_mode is 'only', then only the branches are returned.

        Example::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
            >>> print t.makeReport()
            b.x   = 1
            b.c.y = 2
            x     = 1
            >>> list(t.itervalues())
            [1, 1, 2]
            >>> list(t.itervalues(recursive=False))
            [1]
            >>> list(t.itervalues(recursive=False, branch_mode='none'))
            [1]
            >>> list(t.itervalues(recursive=False, branch_mode='only'))
            [TreeDict <root.b>]
            >>> list(t.itervalues(recursive=False, branch_mode='all'))
            [1, TreeDict <root.b>]
            >>> list(t.itervalues(recursive=True, branch_mode='only'))
            [TreeDict <root.b>, TreeDict <root.b.c>]
            >>> list(t.itervalues(recursive=True, branch_mode='all'))
            [1, TreeDict <root.b>, 1, TreeDict <root.b.c>, 2]
            
        """

        return self._getIter(recursive, self._getBranchMode(branch_mode), i_Values)

    def __iter__(self):
        return self.iterkeys()

    cpdef TreeDictIterator iterkeys(self, bint recursive = True, branch_mode = 'none'):
        """
        Returns an iterator that returns keys for nodes in the tree.
        If recursive is True, then it iterates through all nodes in
        this branch and in all subtrees.  Keys are returned with their
        full path names, e.g. 'foo.bar'.

        If branch_mode is 'none' (default), the branches are ignored
        and all the items associated with values are returned.

        If branch_mode is 'all', all items in the current tree
        are returned.

        If branch_mode is 'only', then only the branches are returned.

        Example::

            >>> from treedict import TreeDict
            >>> t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
            >>> print t.makeReport()
            b.x   = 1
            b.c.y = 2
            x     = 1
            >>> list(t.iterkeys())
            ['x', 'b.x', 'b.c.y']
            >>> list(t.iterkeys(recursive=False))
            ['x']
            >>> list(t.iterkeys(recursive=False, branch_mode='none'))
            ['x']
            >>> list(t.iterkeys(recursive=False, branch_mode='only'))
            ['b']
            >>> list(t.iterkeys(recursive=False, branch_mode='all'))
            ['x', 'b']
            >>> list(t.iterkeys(recursive=True, branch_mode='only'))
            ['b', 'b.c']
            >>> list(t.iterkeys(recursive=True, branch_mode='all'))
            ['x', 'b', 'b.x', 'b.c', 'b.c.y']
            
        """

        return self._getIter(recursive, self._getBranchMode(branch_mode), i_Keys)

    cpdef TreeDictIterator iterbranches(self):
        """
        A convenience function; iterates through all of the local
        branches.  Equivalent to itervalues(recursive=False,
        branch_mode='only').

        Example::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.set('a.b', 1, 'b.c', 2, x = 1, y = 2)
            >>> print t.makeReport()
            a.b = 1
            b.c = 2
            y   = 2
            x   = 1
            >>> list(t.iterbranches())
            [TreeDict <root.a>, TreeDict <root.b>]
       
        """

        return self._getIter(False, self._getBranchMode('only'), i_Values)

    cdef list _getListFromIter(self, TreeDictIterator pti):
        # Fast as possible
        cdef bint recursive = pti._recursive
        cdef int branch_mode = pti._branch_mode
        
        cdef size_t n = self._size(recursive, branch_mode)

        cdef list l = <list>PyList_New(n)
        cdef size_t i
        cdef bint r

        for 0 <= i < n:

            r = pti._loadNext()

            if RUN_ASSERTS:
                assert r

            v = pti._currentRetValue()

            # Because we're using a temporary, and PyList_SetItem
            # steals the reference, i.e. assumes it owns it now,
            # we have to incref

            Py_INCREF(<PyObject*>v) 
            PyList_SET_ITEM(l, i, <PyObject*>v)

        if RUN_ASSERTS:
            assert not pti._loadNext()

        return l

    def items(self, bint recursive = True, branch_mode = 'none'):
        """
        Identical to :meth:`iteritems()`, but returns a list instead
        of an iterator.
        """

        return self._getListFromIter(self.iteritems(recursive, branch_mode))

    def values(self, bint recursive = True, branch_mode = 'none'):
        """
        Identical to :meth:`itervalues()`, but returns a list instead
        of an iterator.
        """

        return self._getListFromIter(self.itervalues(recursive, branch_mode))

    def keys(self, bint recursive = True, branch_mode = 'none'):
        """
        Identical to :meth:`iterkeys()`, but returns a list instead of
        an iterator.
        """

        return self._getListFromIter(self.iterkeys(recursive, branch_mode))

    def branches(self):
        """
        Identical to :meth:`iterbranches()`, but returns a list
        instead of an iterator.

        Example::
        
            >>> from treedict import TreeDict
            >>> t = TreeDict()
            >>> t.set('a.b', 1, 'b.c', 2, x = 1, y = 2)
            >>> print t.makeReport()
            a.b = 1
            b.c = 2
            y   = 2
            x   = 1
            >>> t.branches()
            [TreeDict <root.a>, TreeDict <root.b>]
       
        """
        return self._getListFromIter(self.iterbranches())

    
    ################################################################################
    # Methods relating to testing on this class

    def getClosestKey(self, str key, int n = 0, bint recursive = True, branch_mode = 'none'):
        """
        Returns the closest match(s) in the tree to the key `key`.

        If ``n >= 1``, then a list of the `n` closest strings is
        returned.  If ``n <= 0``, then a single string, the closest
        match, is returned.  The search algorithm is faster for
        ``n=0`` or ``n=1``.

        The optional behavior is just like with the iterators, with
        the default being to examine, recursively, the keys of all
        leaves for close matches.

        The algorithm used is based on the closest edit distance to
        the query key `key`, with extra weighting given to branch
        boundaries.

        Example::

            >>> t = TreeDict()
            >>> t.alpha.x1 = 1
            >>> t.alpha.y1 = 1
            >>> t.alpha.zzz = 1
            >>> t.beta.x = 1
            >>> t.gamma.beta = 1
            >>> "alpah.x" in t
            False
            >>> t.getClosestKey("alpah.x")
            'alpha.x1'
            >>> t.getClosestKey("alpah.x", 1)
            ['alpha.x1']
            >>> t.getClosestKey("alpah.x", 3)
            ['alpha.x1', 'beta.x', 'alpha.y1']
           
        """

        checkKeyNotNone(key)

        cdef TreeDictIterator pti = self.iterkeys(recursive, branch_mode)

        cdef size_t_v buf = new_size_t_v(100)

        if buf.d == NULL:
            raise MemoryError

        try:
            if n <= 0:
                return self._getSingleClosest(key, pti, &buf)
            elif n == 1:
                v = self._getSingleClosest(key, pti, &buf)
                if v is None:
                    return []
                else:
                    return [v]
            else:
                return self._getListOfClosest(key, <size_t>n, pti, &buf)
        finally:
            free_size_t_v(&buf)


    cdef list _getListOfClosest(self, str key, size_t n, TreeDictIterator pti, size_t_v *bufp):

        cdef str k
        cdef long cost, highest_cost_cutoff = -(2**(sizeof(long) - 2) )
        cdef size_t n_els = 0
        cdef tuple t
        cdef list kl = []

        while True:
            if not pti._loadNext():
                break

            k = pti.currentKey()
            cost = name_match_distance(bufp, key, k)

            # put it on the heap; use -cost so pop gets rid of the
            # highest cost one.
            if n_els < n:
                heappush(kl, (-cost, k) )

                if cost > highest_cost_cutoff:
                    highest_cost_cutoff = cost

                n_els += 1
            else:
                if cost < highest_cost_cutoff:
                    t = <tuple>heapreplace(kl, (-cost, k) )

                    highest_cost_cutoff = min2_long(highest_cost_cutoff, 
                                                    max2_long(-(<long>(t[0])), cost))

        cdef size_t i

        return [k for v, k in 
                reversed([heappop(kl) for i in range(len(kl))])]


    cdef str _getSingleClosest(self, str key, TreeDictIterator pti, size_t_v *bufp):

        cdef str k, best_match = None
        cdef long cost = 0, best_cost = -(2**(sizeof(long) - 2) )
        cdef bint first = True

        while True:
            if not pti._loadNext():
                break

            k = pti.currentKey()
            cost = name_match_distance(bufp, key, k)
            
            if first or cost < best_cost:
                first      = False
                best_cost  = cost
                best_match = k

        return best_match


################################################################################
# Unpickling


def _TreeDict_unpickler(
    name, dict param_dict, flagtype _flags, 
    size_t _n_mutable, size_t _next_item_order_position, size_t _n_dangling):

    cdef TreeDict b, p = newTreeDict(name, False)

    p._param_dict = param_dict
    p._flags = _flags
    p._n_mutable = _n_mutable
    p._next_item_order_position = _next_item_order_position
    p._n_dangling = _n_dangling

    p._reset_branches()

    # Set up familial relations
    for b in p._branches:
        b._parent = p

    return p


######################################################################
# Now an interactive version that works well with ipython. 

class InteractiveTreeDict(object):
    """
    An interactive version of the TreeDict for use in an interpreted
    shell.  While the branch, node, and leaf values in a TreeDict
    instance are stored in an internal dictionary, they are the
    attributes in an InteractiveTreeDict.  This allows one to use tab
    completion in Ipython to interact with the tree more easily.

    The :meth:`treeDict()` method returns the original TreeDict
    instance.

    Example::

        In [3]: from treedict import TreeDict

        In [4]: t = TreeDict()

        In [5]: t.set('alpha.beta', 1, beta = 1, gamma = 2)

        In [6]: ti = t.interactiveTree()

        In [7]: ti.alpha.

        ti.alpha.__class__             ti.alpha.__eq__                ti.alpha.__init__              ti.alpha.__reduce_ex__         ti.alpha.__str__               ti.alpha._setAttrDirect
        ti.alpha.__delattr__           ti.alpha.__format__            ti.alpha.__module__            ti.alpha.__repr__              ti.alpha.__subclasshook__      ti.alpha.beta
        ti.alpha.__dict__              ti.alpha.__getattribute__      ti.alpha.__new__               ti.alpha.__setattr__           ti.alpha.__weakref__           ti.alpha.treeDict
        ti.alpha.__doc__               ti.alpha.__hash__              ti.alpha.__reduce__            ti.alpha.__sizeof__            ti.alpha._original_param_tree  

        In [7]: ti.alpha.treeDict() is t
        Out[7]: False

        In [8]: ti.alpha.treeDict() is t.alpha
        Out[8]: True

        In [9]: t.
        t.__call__                  t.__getattr__               t.__pyx_vtable__            t._getSettingOrderPosition  t.fromkeys                  t.isRoot                    t.pop
        t.__class__                 t.__getattribute__          t.__reduce__                t._isDetachedDangling       t.get                       t.items                     t.popitem
        t.__contains__              t.__getitem__               t.__reduce_ex__             t._iteratorRefCount         t.getClosestKey             t.iterbranches              t.rootNode
        t.__copy__                  t.__gt__                    t.__repr__                  t._numDangling              t.has_key                   t.iteritems                 t.set
        t.__deepcopy__              t.__hash__                  t.__setattr__               t.attach                    t.hash                      t.iterkeys                  t.setFromString
        t.__delattr__               t.__init__                  t.__setitem__               t.branchName                t.interactiveTree           t.itervalues                t.setdefault
        t.__delitem__               t.__le__                    t.__sizeof__                t.branches                  t.isDangling                t.keys                      t.size
        t.__doc__                   t.__len__                   t.__str__                   t.clear                     t.isEmpty                   t.makeBranch                t.treeName
        t.__eq__                    t.__lt__                    t.__subclasshook__          t.copy                      t.isFrozen                  t.makeReport                t.update
        t.__format__                t.__ne__                    t._branchNameOf             t.dryset                    t.isMutable                 t.nodeInSameTree            t.values
        t.__ge__                    t.__new__                   t._fullNameOf               t.freeze                    t.isRegistered              t.parentNode                

        In [9]: t.
    """

    def __init__(self, TreeDict ptree):

        # May be overridden
        self._setAttrDirect("_original_param_tree", ptree)

        cdef str k
        cdef _PTreeNode pn

        for k, pn in ptree._param_dict.iteritems():

            if pn.isBranch():
                if not pn.tree().isDangling():
                    self._setAttrDirect(k, pn.tree().interactiveTree())
            else:
                self._setAttrDirect(k, pn.value())

    def __eq__(ipt1, ipt2):

        if not (isinstance(ipt1, InteractiveTreeDict) and isinstance(ipt2, InteractiveTreeDict)):
            return False
        elif ipt1 is None or ipt2 is None:
            return False
        else:
            return (<TreeDict>ipt1._original_param_tree)._isEqual(<TreeDict>ipt2._original_param_tree)
    
    def treeDict(self):
        return self._original_param_tree

    def __reduce__(self):
        return (InteractiveTreeDict, (self._original_param_tree,))
            
    def __setattr__(self, str key, v):
        (<TreeDict> self._original_param_tree)._setLocal(key, v, 0)
        self._setAttrDirect(key, v)

    def _setAttrDirect(self, str key, v):
        object.__setattr__(self, key, v)

################################################################################
# A few small side functions mainly for testing

def _ldist(str s1, str s2):
    cdef size_t_v buf = new_size_t_v(0)
    
    cost = editDistance(&buf, s1, s2)

    free_size_t_v(&buf)

    return cost
