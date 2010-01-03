
# For the makeReport example
from treedict import TreeDict

t = TreeDict("mytree")
t.x = 1
t.y = 2
t.a.z = [1,2,3]
t.a.y = {1 : 2}
t.b.x = "hello"
t.a.x = None
t.b.z = 2

print t.makeReport()
print t.a.makeReport()
print t.a.makeReport(add_path = True)
print t.a.makeReport(add_path = True, add_tree_name = False)


# For set()
from treedict import TreeDict
t = TreeDict()
t.set("x", 1)
t.set(z = 3)
t.set("ya", 2, "yb", 2, yc = 3)
t.set("a.b.c.v", 1)
print t.makeReport()

# for set

from treedict import TreeDict
t = TreeDict()
t.set("x", 1)
print t.makeReport()
t.set("a", 3, "b", 4, "1badvalue", 5)
print t.makeReport()

# For attach

from treedict import TreeDict
t = TreeDict('root')
t1 = TreeDict('t1')
t.attach(t1, copy = True)
t1.rootNode()
t.t1 is t1
t.t1.rootNode()

from treedict import TreeDict
t = TreeDict('root')
t1 = TreeDict('t1')
t.attach(t1, name = "new_t1", copy = False)
t1.rootNode()
t.new_t1 is t1

from treedict import TreeDict
t = TreeDict('root')
t1 = TreeDict('t1', x1 = 1, y1 = 2)
t2 = TreeDict('t2', x2 = 10, y2 = 20)
    
t.a = 1
t.t1 = t1
t.attach(t2)
print t.makeReport()
t.attach(recursive = True)
print t.makeReport()

#########################################
# For branch name

from treedict import TreeDict
t = TreeDict('root')
t.makeBranch("a.b.c")
t.a.b.c.branchName()
t.a.b.c.branchName(add_path = True)
t.a.b.c.branchName(add_path = True, add_tree_name = True)

########################################
# Branches

from treedict import TreeDict
t = TreeDict()
t.set('a.b', 1, 'b.c', 2, x = 1, y = 2)
print t.makeReport()
list(t.iterbranches())

from treedict import TreeDict
t = TreeDict()
t.set('a.b', 1, 'b.c', 2, x = 1, y = 2)
print t.makeReport()
t.branches()

########################################
# Clear

from treedict import TreeDict
t = TreeDict() ; t.set('a.b', 1, 'b.c', 2, x = 1, y = 2)
print t.makeReport()
t1 = t.copy() ; t2 = t.copy()
t.clear()
t.isEmpty()

t1.clear(branch_mode = 'none')
print t1.makeReport()

t2.clear(branch_mode = 'only')
print t2.makeReport()

########################################
# fromkeys

from treedict import TreeDict
t = TreeDict.fromkeys(['a', 'b', 'c'])
print t.makeReport()

from treedict import TreeDict
t = TreeDict.fromkeys('abc', 'abc')
print t.makeReport()

########################################
# setdefault

from treedict import TreeDict
t = TreeDict(x = 1)
print t.makeReport()
t.setdefault("x", 2)
t.setdefault("y", 2)
print t.makeReport()

########################################
# get

from treedict import TreeDict
t = TreeDict(x = 1)
t.get("x")
t.get("y")
t.get("y", [])

########################################
# getClosestKey

t = TreeDict()
t.alpha.x1 = 1
t.alpha.y1 = 1
t.alpha.zzz = 1
t.beta.x = 1
t.gamma.beta = 1
"alpah.x" in t
t.getClosestKey("alpah.x")
t.getClosestKey("alpah.x", 1)
t.getClosestKey("alpah.x", 3)

########################################
# hash

from treedict import TreeDict
t = TreeDict()
t.set('br.x', 1, 'br.c.y', 2, x = 1, y = 2)
t.hash()
t.hash('br')
t.br.hash()
t.br.hash(add_name = True)
t.hash('x')
t.hash(keys = ['x', 'y'])
t.hash('nothere')

########################################
# treeName

from treedict import TreeDict
t = TreeDict('mytree')
t.treeName()
t.makeBranch('a.b.c')
t.a.b.treeName()

########################################
# iteritems

from treedict import TreeDict
t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
print t.makeReport()
list(t.iteritems())
list(t.iteritems(recursive=False))
list(t.iteritems(recursive=False, branch_mode='none'))
list(t.iteritems(recursive=False, branch_mode='only'))
list(t.iteritems(recursive=False, branch_mode='all'))
list(t.iteritems(recursive=True, branch_mode='only'))
list(t.iteritems(recursive=True, branch_mode='all'))


########################################
# iterkeys

from treedict import TreeDict
t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
print t.makeReport()
list(t.iterkeys())
list(t.iterkeys(recursive=False))
list(t.iterkeys(recursive=False, branch_mode='none'))
list(t.iterkeys(recursive=False, branch_mode='only'))
list(t.iterkeys(recursive=False, branch_mode='all'))
list(t.iterkeys(recursive=True, branch_mode='only'))
list(t.iterkeys(recursive=True, branch_mode='all'))


########################################
# itervalues

from treedict import TreeDict
t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
print t.makeReport()
list(t.itervalues())
list(t.itervalues(recursive=False))
list(t.itervalues(recursive=False, branch_mode='none'))
list(t.itervalues(recursive=False, branch_mode='only'))
list(t.itervalues(recursive=False, branch_mode='all'))
list(t.itervalues(recursive=True, branch_mode='only'))
list(t.itervalues(recursive=True, branch_mode='all'))

########################################
# pop

from treedict import TreeDict
t = TreeDict()
t.b.c.d.e.y = 2
t.b.c.d.e.pop('y')
"b.c.d.e.y" in t
"b.c.d.e" in t
t.b.c.d.e.pop()
"b.c.d.e" in t
"b.c.d" in t
t.b.c.d.pop(prune_empty = True)
"b.c.d" in t
"b.c" in t
t.isEmpty()
t.pop('nothere')
t.pop('nothere', silent=True)

########################################
# size

from treedict import TreeDict
t = TreeDict() ; t.set('b.x', 1, 'b.c.y', 2, x = 1)
print t.makeReport()
t.size()
t.size(recursive=False)
t.size(recursive=False, branch_mode='none')
t.size(recursive=False, branch_mode='only')
t.size(recursive=False, branch_mode='all')
t.size(recursive=True, branch_mode='only')
t.size(recursive=True, branch_mode='all')

########################################
# setFromString

from treedict import TreeDict
t = TreeDict()
t.setFromString('x', '1')
t.setFromString('y', '(1,2,["abc",None])') 
t.setFromString('z', '{"abc" : 1}')
print t.makeReport()

########################################
# __call__

from treedict import TreeDict
t = TreeDict()
t('a.b.x', 1, x = 2)
print t.makeReport()
t(y = 3)(z = 4)
print t.makeReport()

########################################
# The globals

t = getTree("default_parameters")
t.verbose = False
t.run_mode = t.chug

t.chug.action = "drink"
t.chug.quantity = "lots"

t.sip.action = "drink"
t.sip.quantity = "a little"

if True:
    def run(run_parameters):

        t = getTree("default_parameters")
        t.update(parameters)

        # The following will print "drink lots" unless overridden by run_parameters
        print t.run_mode.action, t.run_mode.quantity
    

########################################
#

from treedict import TreeDict
t = TreeDict()

# Attribute-style and dict-style setting are interchangable.
t["run.action"]             = True
t.run.time_of_day           = "Morning"

# Intermediate branches are implicitly created
t.programmer.habits.morning = ["drink coffee", "Read xkcd"]

# read_xkcd is implicitly created here, but isn't really part of the
# tree until later
t.action = t.read_xkcd

# This attaches the dangling branch read_xkcd above
t.read_xkcd.description     = "Go to www.xkcd.com and read."
t.read_xkcd.expected_time   = "5 minutes."

########################################
# Dict example

from treedict import TreeDict
d = {"x" : 1, "y" : 2, "a.b.x" : 3, "a.b.c.y" : 4}
t = TreeDict()
t.update(d)
print t.makeReport()

from treedict import TreeDict
t = TreeDict() ; t.set("x" , 1, "y" , 2, "a.b.x", 3, "a.b.c.y", 4)
dict(t.iteritems())

from treedict import TreeDict
t = TreeDict()
t.a.b.x = 1
t.a.c.x = 2
t.d.y = 3
t.items()
t.a.items()
t.a.b.items()
    
########################################
# Memoize decorator

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
        # replace "self.cache = {}" with something like:
        #
        # self.cache = shelve.open(getTree("global_options").cache_file)
        # atexit.register(lambda: self.cache.close())
        #
        # to get long-term persistence
        self.cache = {}
    def __call__(self, *args, **kwargs):
        # Use TreeDict to allow for mutable parameters / kwargs
        kw_t = TreeDict(**kwargs)
        arg_t = TreeDict(args = args)
        cache_key = ( kw_t.hash(), arg_t.hash())
        try:
            return self.cache[cache_key]
        except KeyError:
            self.cache[cache_key] = value = self.func(*args, **kwargs)
            return value

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
        return fibonacci(n-1, t) + fibonacci(n-2, t) + shift
    
