/* This macro calls Python's new-style class creation system. */ 

#define PY_NEW(T)						\
    (((PyTypeObject*)(T))->tp_new(				\
	(PyTypeObject*)(T), __pyx_empty_tuple, NULL))

