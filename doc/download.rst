Download
========

The easiest way to install treedict is through the python setuptools
``easy_install`` utility by typing::

    easy_install treedict

You can also install treedict by directly downloading a source tarball
from the python cheeseshop at http://pypi.python.org/pypi/treedict. 

For developers, a `git`_ source repository is available on `github`_.
You can clone that repository with the following command::

    git clone git://github.com/hoytak/treedict.git

Bug reports, questions, or comments are very welcome and can be
submitted at http://github.com/hoytak/treedict/issues.

Note on Binary/Source Distribution Packages
-------------------------------------------

TreeDict currently has only a source distribution in the cheeseshop.
Thus it requires a C compiler to be present in order to install it,
which should not be a problem on \*nix systems.  However, I don't have
the capability currently to create binary distribution packages for
windows.  This should be a painless affair -- the C code is generated
by cython_, which should compile fine using Microsoft compilers (at
least cython_ is well tested for use on windows) -- but I just don't
have the facilities currently to get binary packages together for
non-linux systems.  If someone is willing to do this for me, or donate
a few cycles on a buildbot, I would be most grateful; please email me
at hoytak@stat.washington.edu.

.. _git: http://git-scm.com/
.. _github: http://github.com
.. _cython: http://www.cython.org/
