TreeDict
========

The python TreeDict is a dictionary-like, hierarcical container for
storing, organizing and manipulating values.  It is intended to be
fast and lightweight enough to be used, in most cases, as a
feature-rich replacement for a dictionary of alphanumeric keys while
implementing features that make sophisticated bookkeeping easy.

TreeDict has the following features:

- A design emphasis on concise, clear, intuitive syntax and
  functionality.

- All dictionary operations and methods are implemented, allowing
  TreeDict to be a drop-in replacement for a dictionary in many cases
  (The limitation is that branch and value names must be strings
  following python variable/attribute naming conventions).

- An optional, central lookup of "registered" trees (similar to
  loggers in the python logging module) to ease global parameter
  setting.

- Manipulations on the tree structure, including attaching, detaching,
  copying, updating (merging), hashing, freezing and equality testing
  are supported and optimized.

- A method that takes non-intersecting hashes over all or parts of the
  tree to facilitate testing, caching and indexing.

- Implicit creation of branches to allow for more natural and readable
  ordering when defining parameters (see example below).

- API is well documented and covered by unit tests.

- Written in `cython`_ for speed and stability.

- Close-matching key retrieval to aid in offering helpful error
  messages.

- Licensed under the liberal BSD open source license.


Short Example
------------------------------

A brief example to wet the appetite::

    from treedict import TreeDict
    t = TreeDict()

    # Attribute-style and dict-style assignments are interchangable.
    t["run.action"]             = True
    t.run.time_of_day           = "Morning"
    
    # Intermediate branches are implicitly created
    t.programmer.habits.morning = ["drink coffee", "Read xkcd"]
    
    # 'read_xkcd' is implicitly created here, but it is "dangling"
    # until another operation fixes it to the tree.  
    t.action = t.read_xkcd
    
    # This attaches the dangling branch read_xkcd above
    t.read_xkcd.description     = "Go to www.xkcd.com and read."
    t.read_xkcd.expected_time   = "5 minutes."
    
Contents
========================================

.. toctree::
    :maxdepth: 2
    
    overview
    api
    license

.. _cython: http://www.cython.org
