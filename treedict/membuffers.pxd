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
#     - Neither the name 'paramtree' nor the
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

# This pxd module just provides a centralized and fast way of handling
# size_t* buffers, which seems to happen a lot.

cdef extern from "Python.h":
    void* malloc "PyMem_Malloc" (size_t n)
    void* realloc "PyMem_Realloc" (void *p, size_t n)
    void free "PyMem_Free" (void *p)

cdef struct size_t_v:
    size_t *d
    size_t size

cdef inline size_t_v new_size_t_v(size_t size):
    cdef size_t_v v

    if size > 0:
        v.d = <size_t*>malloc(size*sizeof(size_t))
    else:
        v.d = NULL

    v.size = size
    
    return v

cdef inline void resize_size_t_v(size_t_v* v_ptr, size_t newsize):

    if newsize <= v_ptr.size:
        return
    elif v_ptr.d == NULL:
        v_ptr.d = <size_t*>malloc(newsize*sizeof(size_t))
    else:
        v_ptr.d = <size_t*>realloc(v_ptr.d, newsize*sizeof(size_t))
    
    v_ptr.size = newsize
        
cdef inline void free_size_t_v(size_t_v* v_ptr):
    if v_ptr.d != NULL:
        free(v_ptr.d)

    v_ptr.size = 0
    v_ptr.d = NULL
