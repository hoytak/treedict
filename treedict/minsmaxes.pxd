
cdef inline size_t min3(size_t a, size_t b, size_t c):
    cdef size_t m = a
    if b < m: m = b
    if c < m: m = c
    return m

cdef inline size_t min2(size_t a, size_t b):
    return a if a < b else b

cdef inline size_t max2(size_t a, size_t b):
    return b if a < b else a

cdef inline int min2_int(int a, int b):
    return a if a < b else b

cdef inline int max2_int(int a, int b):
    return b if a < b else a

cdef inline long min2_long(long a, long b):
    return a if a < b else b

cdef inline long max2_long(long a, long b):
    return b if a < b else a
