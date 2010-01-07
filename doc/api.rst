.. _API:

TreeDict API
==================

The treedict module provides the TreeDict class along with two
functions, `getTree` and `treeExists`. 

.. automodule:: treedict

    .. autofunction:: getTree(name)

    .. autofunction:: treeExists(name)

    .. autoclass:: treedict.TreeDict

        .. method:: __init__(self, name = 'root', **kwargs)
    
            Create a new TreeDict instance with name `name`.  

	    Initial values can be supplied as keyword arguments;
	    e.g. ``TreeDict(a = 5)`` will create a TreeDict instance with
	    one value, `a`, equal to 5.  

	    Example::

	        >>> from treedict import TreeDict
		>>> t = TreeDict('mytree', x = 5, y = 6)
		>>> print t.make_report(add_path = True)
		mytree.x = 5
		mytree.y = 6

	.. method:: __getattr__(self, key)

	    Returns the branch/value `key`.  If not present, a branch
	    `key` is implicitly created as a dangling node.

	.. method:: __setitem__(self, key, value)
	
	    Sets `key` to `value`.  `key` can be the name of a new or
	    existing key in the current node or any sub-node.  Any
	    intermediate nodes are created.

	    Equivalent to :meth:`set(key, value)<set>` 

	    A TypeError is raised if `key` is not a string, and a
	    ValueError is raised if `key` is not a valid name.

	.. method:: __setattr__(self, key, value)
	   
	   Like :meth:`__setitem__`, set `key` to `value`.

	.. method:: __delattr__(self, key):
	
	    Removes `key` from the current node.

	.. method:: __delitem__(self, key):
	
	    Removes `key` from the current node.

	.. method:: __call__(self, *args, **kwargs)
	
	    A convenience method that wraps :meth:`set` and returns
	    `self`.

	    Example::

	        >>> from treedict import TreeDict
		>>> t = TreeDict()
		>>> t('a.b.x', 1, x = 2)
		TreeDict <root>
		>>> print t.make_report()
		a.b.x = 1
		x     = 2
		>>> t(y = 3)(z = 4)
		TreeDict <root>
		>>> print t.make_report()
		a.b.x = 1
		x     = 2
		y     = 3
		z     = 4

	.. method:: __contains__(self, key)

	   Returns True if `key` is a valid value or non-dangling
	   branch. Equivalent to :meth:`has_key`.

	.. method:: __len__(self)

           Returns the number of values in this node and all subnodes.
           Equivalent to :meth:`size` with default arguments.

        .. automethod:: attach(self, tree_or_node = None, name = None, copy = True, recursive = False)

        .. automethod:: branch_name(self, local_only = True, include_tree_name=False)

        .. automethod:: branches(self)

        .. automethod:: clear(self, branch_mode = 'all')

        .. automethod:: copy(self, deep=False, freeze=False)

        .. automethod:: dryset(self, *args, **kwargs)

        .. automethod:: freeze(self, branch=None)

        .. automethod:: fromkeys(key_iterable, value = None)

        .. automethod:: get(self, key, default_value = NoDefault)

        .. automethod:: get_closest_key(self, key, n = 0, recursive = True, branch_mode = 'none')

        .. automethod:: has_key(self, key)

        .. automethod:: hash(self, key=None, add_name = False, keys=None)

        .. automethod:: interactive_tree(self)

        .. automethod:: is_dangling(self)

        .. automethod:: is_empty(self)

        .. automethod:: is_frozen(self)

        .. automethod:: is_mutable(self)

        .. automethod:: is_registered(self)
									    
        .. automethod:: is_root(self)

        .. automethod:: items(self, recursive = True, branch_mode = 'none')

        .. automethod:: iterbranches(self)

        .. automethod:: iteritems(self, recursive = True, branch_mode = 'none')
											    
        .. automethod:: iterkeys(self, recursive = True, branch_mode = 'none')

        .. automethod:: itervalues(self, recursive = True, branch_mode = 'none')

        .. automethod:: keys(self, recursive = True, branch_mode = 'none')

        .. automethod:: make_branch(self, name, only_new = False)

        .. automethod:: make_report(self)

        .. automethod:: node_in_same_tree(self, node)

        .. automethod:: parent_node(self)

        .. automethod:: pop(self, key = None, prune_empty = False, silent = False)

        .. automethod:: popitem(self, key = None, prune_empty = False, silent = False)

        .. automethod:: root_node(self)

        .. automethod:: set(self, *args, **kwargs)

        .. automethod:: set_from_string(self, key, value, extra_parameters = {})

        .. automethod:: setdefault(self, key, value = None)

        .. automethod:: size(self, recursive = True, branch_mode = 'none')

        .. automethod:: tree_name(self)

        .. automethod:: update(self, d)

        .. automethod:: values(self, recursive = True, branch_mode = 'none')

