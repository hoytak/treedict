.. _API:

API
==================

.. currentmodule:: treedict

Creation
--------

.. method:: TreeDict.__init__(self, name = 'root', **kwargs)

    Create a new TreeDict instance with name `name`.  

    Initial values can be supplied as keyword arguments;
    e.g. ``TreeDict(a = 5)`` will create a TreeDict instance with
    one value, `a`, equal to 5.  

    Example::

	>>> from treedict import TreeDict
	>>> t = TreeDict('mytree', x = 5, y = 6)
	>>> print t.makeReport(add_path = True)
	mytree.x = 5
	mytree.y = 6

Value/Branch Retrieval
----------------------

Retrieving values can be done using methods similar to dictionaries or
other python objects.  

.. method:: TreeDict.__getattr__(self, key)

    Returns the branch/value `key`.  If not present, a branch
    `key` is implicitly created as a dangling node.

    Example::

	>>> from treedict import TreeDict
	>>> t = TreeDict(k = 5)
	>>> t.k
	5
	>>> t.b
	Dangling TreeDict <root.b>
	>>> 

.. method:: TreeDict.__getitem__(self, key)

    In similar fashion to a dictionary, returns the
    branch/value `key`.  If not present, a KeyError is raised.

    Example::

	>>> from treedict import TreeDict
	>>> t = TreeDict(k = 5)
	>>> t["k"]
	5
	>>> 

.. automethod:: TreeDict.get(self, key, default_value = NoDefault)


Storing Values
--------------

Storing values is supported using both dictionary style setting
(``t["key"] = value``) and attribute style setting (``t.key =
value``).  In addition, more powerful methods such as :meth:`set`, and
:meth:`update` support setting groups of keys at once; these methods
are all "atomic" in the sense that all of the values are set or none
at all are set (A set operation may fail with a bad key name or,
e.g. attempting to overwrite/modify a frozen branch).

Setting Single Values
~~~~~~~~~~~~~~~~~~~~~

.. method:: TreeDict.__setitem__(self, key, value)

    Sets `key` to `value`.  `key` can be the name of a new or
    existing key in the current node or any sub-node.  Any
    intermediate nodes are created.

    Equivalent to :meth:`set(key, value)<set>` 

    A TypeError is raised if `key` is not a string, and a ValueError
    is raised if `key` is not a valid name.

.. method:: TreeDict.__setattr__(self, key, value)

   Like :meth:`__setitem__`, set `key` to `value`.

.. automethod:: TreeDict.makeBranch(self, name, only_new = False)

Setting Groups of Values
~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: TreeDict.set(self, *args, **kwargs)

.. automethod:: TreeDict.update(self, source, overwrite=True, protect_structure=False)

Convenience Setting Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: TreeDict.checkset(self, *args, **kwargs)

.. automethod:: TreeDict.setdefault(self, key, value = None)

.. automethod:: TreeDict.setFromString(self, key, value, extra_parameters = {})

.. automethod:: TreeDict.fromkeys(key_iterable, value = None)

.. automethod:: TreeDict.fromdict(source)

Existence Querying
------------------

.. method:: TreeDict.__contains__(self, key)

   Returns True if `key` is a valid value or non-dangling
   branch. Equivalent to :meth:`has_key`.

.. automethod:: TreeDict.has_key(self, key)

Clearing Items
--------------

.. method:: TreeDict.__delattr__(self, key):

    Removes `key` from the current node.  `key` can reference either a
    value or a branch.  If `key` does not exist, an AttributeError is
    raised.

    Example::

	>>> from treedict import TreeDict
	>>> t = TreeDict(k = 5)
	>>> 'k' in t
	True
	>>> del t.k
	>>> 'k' in t
	False
	>>> 
    
.. method:: TreeDict.__delitem__(self, key):

    Removes `key` from the current node.  This method is analagous to
    the ``__delitem__`` of a dictionary.  If `key` does not exist, a
    KeyError is raised.

    Example::

	>>> from treedict import TreeDict
	>>> t = TreeDict(k = 5)
	>>> 'k' in t
	True
	>>> del t['k']
	>>> 'k' in t
	False
	>>> 


.. automethod:: TreeDict.clear(self, branch_mode = 'all')

.. automethod:: TreeDict.pop(self, key = None, prune_empty = False, silent = False)

Structural Operations
---------------------

The following methods permit manipulations of the tree structure in
several ways.  :meth:`attach` grafts in a TreeDict node as a branch;
:meth:`freeze` freezes the tree structure so no further manipulations
are possible (useful for ensuring that parameters do not change once
set), and copy

Additional methods that may be
when include

.. automethod:: TreeDict.attach(self, tree_or_node = None, name = None, copy = True, recursive = False, protect_structure=True)

.. automethod:: TreeDict.freeze(self, branch=None, quiet = True)

.. automethod:: TreeDict.copy(self, deep=False, freeze=False)


Iteration / Lists
-----------------

In similar fashion to dictionaries, TreeDict supports retrieving
elements as lists or through iteration.  In addition to the
corresponding dictionary methods, the TreeDict methods support
additional arguments concerning handling of branches and values.  All
default to returning all the values stored in the local tree and its
branches.  Furthermore, two convenience methods, :meth:`iterbranches` and
:meth:`branches`, also provide iteration over the local branches.

.. automethod:: TreeDict.iterkeys(self, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.keys(self, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.itervalues(self, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.values(self, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.iteritems(self, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.items(self, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.iterbranches(self)

.. automethod:: TreeDict.branches(self)

Traversing
----------

Traversing down the tree (using the computer science understanding of
a tree being upside-down) is simply done through retrieving the
desired branch.  Traversing back up the tree from a specific node is
done through the following methods.

.. automethod:: TreeDict.rootNode(self)

.. automethod:: TreeDict.parentNode(self)


Tree Properties
---------------

Names
~~~~~

.. automethod:: TreeDict.branchName(self, add_path = False, add_tree_name = False)

.. automethod:: TreeDict.treeName(self)

Size
~~~~

.. method:: TreeDict.__len__(self)

   Returns the number of values in this node and all subnodes.
   Equivalent to :meth:`size` with default arguments.

.. automethod:: TreeDict.size(self, recursive = True, branch_mode = 'none')

Branch Properties
~~~~~~~~~~~~~~~~~

.. automethod:: TreeDict.isDangling(self)

.. automethod:: TreeDict.isEmpty(self)

.. automethod:: TreeDict.isFrozen(self)

.. automethod:: TreeDict.isMutable(self)

.. automethod:: TreeDict.isRegistered(self)

.. automethod:: TreeDict.isRoot(self)

.. automethod:: TreeDict.nodeInSameTree(self, node)

Node Traversal
~~~~~~~~~~~~~~

.. automethod:: TreeDict.rootNode(self)

.. automethod:: TreeDict.parentNode(self)

Hash Operations
---------------

.. automethod:: TreeDict.hash(self, key=None, add_name = False, keys=None)

Convenience Methods
-------------------

.. automethod:: TreeDict.getClosestKey(self, key, n = 0, recursive = True, branch_mode = 'none')

.. automethod:: TreeDict.makeReport(self)

.. automethod:: TreeDict.interactiveTree(self)

Global Tree Management
----------------------

.. autofunction:: treedict.getTree(name)

.. autofunction:: treedict.treeExists(name)

