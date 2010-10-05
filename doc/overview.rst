.. _overview:

Overview
====================

TreeDict can be thought of as a hierarchical dictionary.  It is
limited in functionality compared to the python built-in dictionary
only in that the branch names and values must be strings that follow
standard python attribute naming rules.  This is to allow the user to
access and set values through attributes, allowing for easy-to-read,
concise parameter specification.

The syntax used to specify branches and leaves in the tree is the same
as that used for accessing attributes, i.e. python names seperated by
periods.  For example, `b1.b2.x` specifies a branch `b1`, sub-branch
`b2`, and value `x`.

Basic Operations
----------------------------------------

All the python operators supported by `dict` are also supported by
`TreeDict`.  These include assignment, membersnhip testing with `in`,
equality testing, iteration, and copying.  These are summarized in the
following table:

+-------------------------+---------------------------------------------+
|  ``k in t``             | True if  `k`  is in  `t`, False otherwise.  |
+-------------------------+---------------------------------------------+
|  ``t[k] = v``           | Sets key `k` to value `v`.                  |
+-------------------------+---------------------------------------------+
|  ``del t[k]``           | Removes key `key` from `t`.                 |
+-------------------------+---------------------------------------------+
| ``t['a.b.x'] = v``,     | Sets key `'x'` on branch `'a.b'` to `v`.    |
| ``t.a.b.x = v``         | `'a.b'` is implicitly created if not        |
|                         | present.                                    |
+-------------------------+---------------------------------------------+
| ``for k in t:``         | Like `dict`, iterates through the keys of   |
|                         | `t`.                                        |
+-------------------------+---------------------------------------------+
| ``t.copy()``,           | Creates a copy of the tree structure.       |
| ``copy(t)``             |                                             |
+-------------------------+---------------------------------------------+
| ``t.copy(deep=True)``,  | Creates a copy of both the tree structure   |
| ``deepcopy(t)``         | and the values.                             |
+-------------------------+---------------------------------------------+


In addition to the above, all the dictionary methods --
:meth:`~treedict.TreeDict.get`, :meth:`~treedict.TreeDict.setdefault`,
:meth:`~treedict.TreeDict.clear`, :meth:`~treedict.TreeDict.copy`,
:meth:`~treedict.TreeDict.pop`, :meth:`~treedict.TreeDict.popitem`,
:meth:`~treedict.TreeDict.update`, :meth:`~treedict.TreeDict.keys`,
:meth:`~treedict.TreeDict.iterkeys`,
:meth:`~treedict.TreeDict.values`,
:meth:`~treedict.TreeDict.itervalues`,
:meth:`~treedict.TreeDict.items` and
:meth:`~treedict.TreeDict.iteritems` -- are implemented.  Each of
these supports optional parameters beyond those of `dict` to work with
the tree-shaped structure, but the default operations are exactly
analagous a `dict` in which the keys are the full path names to the
values.  If these functions are called on a branch, they operate only
on that branch and the branches and values underneath it.  For
example::

    >>> from treedict import TreeDict
    >>> t = TreeDict()
    >>> t.a.b.x = 1
    >>> t.a.c.x = 2
    >>> t.d.y = 3
    >>> t.items()
    [('a.c.x', 2), ('a.b.x', 1), ('d.y', 3)]
    >>> t.a.items()
    [('c.x', 2), ('b.x', 1)]
    >>> t.a.b.items()
    [('x', 1)]

In addition, pickling is supported.  

Implicit Branch Creation 
----------------------------------------

Branches in the TreeDict are created implicitly as needed.  In the
following code::

    t = TreeDict()
    t.a.b.y = 1
    t.a.b.c.x = 2

the intermediate branches `a`, `b`, and `c` are implicitly created.
Thus, setting options through attributes minimizes unnecessary syntax,
e.g. quotes and brackets (``["..."]``) if one uses python
dictionaries.

Internally, this is done by allowing "dangling" branches -- branches
that are invisible (e.g. ``b in t`` is False if `b` is dangling) to
the API but are tracked internally until they are attached to the
tree.  A dangling branch is attached if a leaf value is assigned to it
or a dangling subbranch is attached.  In the example above, assigning
`1` to `y` attaches the dangling branches `a` and `b`.

Implicitly creating branches in this way allows more natural orderings
on assigning values than what python would normally allow.
Specifically, "forward" references can be made to dangling branches
that are attached much later.  For example::

    t = TreeDict()
    
    # Action specified at top for clarity
    t.action = t.action_definitions.make_apple_stroudel  # dangling branch
    
    # Now specify definitions
    t.action_definitions.make_apple_stroudel.action      = "puree"
    t.action_definitions.make_apple_stroudel.ingredients = ["apple", "stroudel"]

    t.action_definitions.make_peach_cobler.action      = "puree"
    t.action_definitions.make_peach_cobler.ingredients = ["peach", "cobler"]

    # Or specify it this way 
    pie = t.action_definitions.make_pie
    pie.action  = "puree"
    pie.ingredients = [3.14159265358979323846, 2.7182818284590451]

    # And so on ...

This allows the user to choose an order in defining parameters that
best presents the options.  Specifying more significant options first
(lower levels on the tree), with details coming later (branches and
leaves), allows for more readable and intuitive code.

Tree Structure
----------------------

The tree itself is such that each node has only one parent node, and
each tree has only one root.  Nodes can be detached from their parent
with the :meth:`~treedict.TreeDict.pop` method; these become a new
tree with the detached node becoming the root.  Likewise, trees can be
grafted in usign :meth:`~treedict.TreeDict.attach`.  In addition,
copies of the entire tree, or just a subtree, can be done with
:meth:`~treedict.TreeDict.copy`.

Unattached TreeDict instances within the tree structure are treated
just like any other values.  Thus links within the tree structure are
allowed as leaves can reference other parts of the tree.  To eliminate
these links, one can use :meth:`~treedict.TreeDict.attach` with
``recursive = True`` to turn any such links into branches, copying as
needed.

Examples
-------------------------

After the above introduction, the features of TreeDict are best
learned by browsing the TreeDict API or presenting a few examples

Converting to/from a Dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A dictionary of keys that follow the branch/leaf naming conventions
(e.g. ``value``, ``branch.value``, ``a12._dlkfjd123.v``) can be
converted to a TreeDict in a number of ways, but the easiest way is
using :meth:`~treedict.TreeDict.update`::

    >>> from treedict import TreeDict
    >>> d = {"x" : 1, "y" : 2, "a.b.x" : 3, "a.b.c.y" : 4}
    >>> t = TreeDict()
    >>> t.update(d)
    >>> print t.makeReport()
    y       = 2
    x       = 1
    a.b.c.y = 4
    a.b.x   = 3
    
To convert to a dictionary, use :meth:`~treedict.TreeDict.iteritems()`::

    >>> from treedict import TreeDict
    >>> t = TreeDict() ; t.set("x" , 1, "y" , 2, "a.b.x", 3, "a.b.c.y", 4)
    >>> dict(t.iteritems())
    {'y': 2, 'x': 1, 'a.b.c.y': 4, 'a.b.x': 3}

Using Default Program Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting the default options in a program can be done as follows.  In
``defaults.py``, we could have::

    import treedict

    t = treedict.getTree('default_parameters')
    t.verbose = False
    t.run_mode = t.chug
    t.run_object = "coffee"

    t.chug.action = "drink"
    t.chug.quantity = "lots"

    t.sip.action = "drink"
    t.sip.quantity = "a little"
    
And then, when we need to access these parameters in another file, we
can do::

    def run(run_parameters):

        t = getTree("default_parameters").copy()
        t.update(parameters)

        # The following will print "drink lots" unless overridden by run_parameters
        print t.run_mode.action, t.run_mode.quantity


Function Caching / Memoization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TreeDict can be used to build a simple but effective caching system
for time-consuming functions.  This example reworks the `memoized`
decorator from the python `decorator wiki
<http://wiki.python.org/moin/PythonDecoratorLibrary>`_.  It uses the
:meth:`~treedict.TreeDict.hash` method of TreeDict to accomidate
mutable parameters and TreeDict instances in the arguments::

    from treedict import TreeDict

    class memoized_with_treedict(object):
        """
        Based on 'memoized' python decorator from
        http://wiki.python.org/moin/PythonDecoratorLibrary.
        Decorator that caches a function's return value each time it is
        called.  If called later with the same arguments, the cached value
        is returned, and not re-evaluated.  In this case, TreeDicts are
        both allowed as arguments and used to allow mutable arguments as
        types.
        """

        def __init__(self, func):
            self.func = func
            self.cache = {}

        def __call__(self, *args, **kwargs):

            # Use TreeDict to allow for mutable parameters / kwargs
            kw_t = TreeDict(**kwargs)
            arg_t = TreeDict(args = args)
            cache_key = (self.func.__name__, self.func.__module__, kw_t.hash(), arg_t.hash())

            try:
                return self.cache[cache_key]
            except KeyError:
	        # All exceptions from calling the function are passed on.
                self.cache[cache_key] = value = self.func(*args, **kwargs)
                return value

The fact that :meth:`~treedict.TreeDict.hash` returns a string permits
the use of `shelve <http://docs.python.org/library/shelve.html>`_ to
provide disk-level persistent caching, a possibly useful feature for
time consuming scientific calculations::

    from treedict import TreeDict
    import atexit, shelve

    # Put this somewhere so it is set before any memoized functions
    # are called
    from treedict import getTree
    getTree("global_options").cache_file = "cache.tmp"
    
    class persistent_memoized(object):
        """
        Based on 'memoized' python decorator from
        http://wiki.python.org/moin/PythonDecoratorLibrary.  Decorator
        that caches a function's return value each time it is called.
        If called later with the same arguments, the cached value is
        returned, and not re-evaluated.  In this case, TreeDicts are
        both allowed as arguments and used to allow mutable arguments
        as types.
        """

        def __init__(self, func):
            self.func = func
            self.cache = None

        def __call__(self, *args, **kwargs):

            # Set here so the cache file doesn't need to be set before
            # this module is imported
            if self.cache is None:
                self.cache = shelve.open(getTree("global_options").cache_file)
                atexit.register(lambda: self.cache.close())

            # Use TreeDict to allow for mutable parameters / kwargs
            kw_t = TreeDict(**kwargs)
            arg_t = TreeDict(args = args)

            # A string-based cache_key allows for use in shelves.
            cache_key = self.func.__name__ + str(self.func.__module__) + kw_t.hash() + arg_t.hash()

            try:
                return self.cache[cache_key]
            except KeyError:
                self.cache[cache_key] = value = self.func(*args, **kwargs)
                return value

Here is an example of how either of these decorates could be used::

    @memoized_with_treedict
    def weird_fibonacci(n, t):
        """
        Fibonacci numbers modified so all results are shifted by t.shift,
        and numbers less than t.start are returned as themselves plus the
        shift.  Demonstrates the use of TreeDict to control options in a
        memoized function.  t.start defaults to 1 and t.shift defaults to 0.
        """

        start = max(1, t.get("start", 1))
        shift = t.get("shift", 0)

        if n <= start:
            return n + shift
        else:
            return weird_fibonacci(n-1, t) + weird_fibonacci(n-2, t) + shift

-----------------------------------

    >>> weird_fibonacci(10, TreeDict(start = 5, shift = 2))
    110 
    >>> [weird_fibonacci(i, TreeDict(start = 5, shift = 2)) for i in xrange(10)]
    [2, 3, 4, 5, 6, 7, 15, 24, 41, 67]

