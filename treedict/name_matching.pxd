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
#     - Neither the name of the copyright holder nor the
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


# We include several elements here in calculating the distances to
# provide the best match.

# We use a function that calculates the levenshtein distance between
# two strings.  This version is pretty vanilla, with a few
# optimization tricks thrown in (e.g. prune the ends).  However, we
# want to weight the results so that starting overlaps are weighted
# closer.


from minsmaxes cimport min3
from membuffers cimport size_t_v, resize_size_t_v
import warnings
from minsmaxes cimport min2_long


cdef inline long _combine_scores(long n_beginning, long n_groups, long n_end_groups, long n1, long n2, long ldist):
    # make sure that beginning matching is most important
    return (ldist - 50*n_groups - min2_long(n_beginning, 5)*n_beginning - 10*n_end_groups 
            + (n1 - n2  if n1 > n2 else 0) )


cdef inline long name_match_distance(size_t_v *calc_buffer, 
                                     str s1, str s2):

    # s1 is the query string, s2 is the one being compared against

    cdef long n1 = len(s1)
    cdef long n2 = len(s2)

    if n1 == 0: return n2
    if n2 == 0: return n1

    cdef char* s = <bytes>s1
    cdef char* t = <bytes>s2
    
    cdef size_t n_beginning = 0, n_groups = 0, n_end_groups = 0

    # Get the overlap at the beginning; this is important
    while s[0] == t[0]:

        n_beginning += 1
        if s[0] == 46:
            n_groups += 1
            n_beginning = 0

        s += 1
        t += 1
        n1 -= 1
        n2 -= 1

        if n1 == 0: return _combine_scores(n_beginning, n_groups, n_end_groups, n1, n2, n2)
        if n2 == 0: return _combine_scores(n_beginning, n_groups, n_end_groups, n1, n2,  n1)

    while s[n1-1] == t[n2-1]:
        if s[n1-1] == 46:
            n_end_groups += 1

        n1 -= 1
        n2 -= 1
        
        if n1 == 0: return _combine_scores(n_beginning, n_groups, n_end_groups, n1, n2,  n2)
        if n2 == 0: return _combine_scores(n_beginning, n_groups, n_end_groups, n1, n2,  n1)


    cdef long ldist = _editDistanceDirect(calc_buffer, s, n1, t, n2)
    return _combine_scores(n_beginning, n_groups, n_end_groups, n1, n2, ldist)



cdef inline long editDistance(size_t_v *calc_buffer, str s1, str s2):

    # This is for debugging purposes
    cdef long n1 = len(s1)
    cdef long n2 = len(s2)

    if s1 == s2: 
        return 0

    cdef char* s = <bytes>s1
    cdef char* t = <bytes>s2
    
    # Get the overlap at the beginning; this is important
    while s[0] == t[0]:
        s += 1
        t += 1
        n1 -= 1
        n2 -= 1

        if n1 == 0: return n2
        if n2 == 0: return n1

    while s[n1-1] == t[n2-1]:
        n1 -= 1
        n2 -= 1

        if n1 == 0: return n2
        if n2 == 0: return n1
    
    return _editDistanceDirect(calc_buffer, s, n1, t, n2)


cdef inline long _editDistanceDirect(size_t_v *calc_buffer, char *s, long n1, char *t, long n2):

    resize_size_t_v(calc_buffer, ((n1+2)*(n2+2) + 1))

    cdef size_t* d = calc_buffer.d

    if d == NULL:
        warnings.warn("Out-of-memory error allocating buffer array.")
        return 0

    cdef size_t i, j
    cdef size_t m = n2+1

    for i from 0 <= i <= n1: d[i*m] = i
    for j from 0 < j <= n2:  d[j] = j
 
    for i from 1 <= i <= n1:
        for j from 1 <= j <= n2:
            d[i*m + j] = min3( d[(i-1)*m + j] + 1, # Insertion
                               d[i*m + j-1] + 1,   # Deletion
                               d[(i-1)*m + j-1] + (0 if s[i-1] == t[j-1] else 1) ) # Change
    
    return d[n1*m + n2]
    
