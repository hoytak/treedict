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


import unittest, sys

if __name__ == '__main__':
    dtl = unittest.defaultTestLoader

    import test_badvalues
    import test_branches
    import test_centralsystem
    #import test_constraints
    import test_copying
    import test_dictbehavior
    import test_deletion
    import test_equalities
    import test_hashes
    import test_interactivetree
    import test_iterators_lists
    import test_matching
    import test_names
    import test_pickling
    import test_properties
    import test_retrieval	
    import test_setting

    ts = unittest.TestSuite([
        dtl.loadTestsFromModule(test_badvalues),
        dtl.loadTestsFromModule(test_branches),
        dtl.loadTestsFromModule(test_centralsystem),
        #dtl.loadTestsFromModule(test_constraints),
        dtl.loadTestsFromModule(test_copying),
        dtl.loadTestsFromModule(test_deletion),
        dtl.loadTestsFromModule(test_dictbehavior),
        dtl.loadTestsFromModule(test_equalities),
        dtl.loadTestsFromModule(test_hashes),
        dtl.loadTestsFromModule(test_interactivetree),
        dtl.loadTestsFromModule(test_iterators_lists),
        dtl.loadTestsFromModule(test_matching),
        dtl.loadTestsFromModule(test_pickling),
        dtl.loadTestsFromModule(test_names),
        dtl.loadTestsFromModule(test_properties),
        dtl.loadTestsFromModule(test_retrieval),
        dtl.loadTestsFromModule(test_setting)])

    if '--verbose' in sys.argv:
        unittest.TextTestRunner(verbosity=2).run(ts)
    else:
        unittest.TextTestRunner().run(ts)
