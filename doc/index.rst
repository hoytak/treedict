TreeDict Introduction
=====================

TreeDict is a dictionary-like, hierarcical python container to
simplify the bookkeeping surrounding parameters, variables and
data. It aims to be fast, lightweight, intuitive, feature-rich and
stable.

While intended for general python development, it includes a number of
features particularly useful for scientific programming.  It is
similar in basic functionality to MATLAB structures in terms of
concise syntax and implicit branch creation.  In addition, though,
TreeDict implements all the methods of regular dictionaries, pickling,
fast non-intersecting hashing for efficient caching, manipulations on
the tree structure, and a system for forward referencing branches to
make lists of parameters more readable.

TreeDict Distinctives
------------------------------

- A design emphasis on concise, immediately readable and intuitive
  syntax and functionality.

- All dictionary operations and methods are implemented, allowing
  TreeDict to be a drop-in replacement for a dictionary in many cases
  (The limitation is that branch and value names must be strings
  following python variable/attribute naming conventions).

- An optional, central lookup of "registered" trees (similar to
  loggers in the python logging module) to ease global parameter
  setting and bookkeeping.

- Manipulations on the tree structure, including attaching, detaching,
  copying, updating (merging), hashing, freezing and equality testing
  are supported and optimized.

- A method that takes non-intersecting hashes over all or parts of the
  tree to facilitate testing, caching and indexing.

- Implicit creation of branches to allow for more natural and readable
  ordering when defining parameters (see example below).

- :ref:`API` is well documented and covered by unit tests.

- Written in `cython`_ for speed and stability.

- Close-matching key retrieval to aid in offering helpful error
  messages.

- Licensed under the liberal BSD open source license.

Short Example
------------------------------

A brief example to wet the appetite::

    t = TreeDict()
    
    # Action specified at top for clarity
    t.action = t.action_definitions.make_apple_stroudel  # dangling branch
    
    # Now specify definitions
    t.action_definitions.make_apple_stroudel.action      = "puree"
    t.action_definitions.make_apple_stroudel.ingredients = ["apple", "stroudel"]

    # And so on...

The rest of this example, and explanations, can be found in the
:ref:`overview`.

.. toctree::
    :maxdepth: 2
    :hidden:
    
    self    
    overview
    api
    download
    license

.. _cython: http://www.cython.org
