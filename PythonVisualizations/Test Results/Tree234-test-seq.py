from Tree234 import *
from coordinates import *
import random
import sys

def invalidItem(tree):
    return _invalidItem(tree, tree.getRoot(), 0)

def _invalidItem(tree, subtree, level, lo=None, hi=None):
    if subtree is None:
        return
    if not isinstance(subtree, Node234):
        return ('Expected Node234 object at level', level, 'but found',
                type(subtree), 'instead', subtree)
    if subtree.nKeys < 1 or Tree234.maxKeys < subtree.nKeys:
        return ('Number of keys is invalid at', level, subtree.nKeys, subtree)
    keys = subtree.keys[:subtree.nKeys]
    if any(key is None for key in keys):
        return ('One or more keys is None at', level, keys, subtree)
    if keys != sorted(keys):
        return ('Keys not in sorted order at level', level, keys, subtree)
    if lo and keys[0] <= lo:
        return ('Lowest key,', keys[0], ', is below bound', lo,
                'set at level higher than', level, subtree)
    if hi and keys[-1] >= hi:
        return ('Highest key,', keys[-1], ', is above bound', hi,
                'set at level higher than', level, subtree)
    link = subtree.dValue.items[0]
    if tree.canvas.type(link) != 'line':
        return ('Link item', link, 'is not a line', subtree)
    linkCoords = tree.canvas.coords(link)
    if distance2(linkCoords[:2], linkCoords[2:]) <= 1 and level > 0:
        return ('Link item', link, 'line is near zero length', linkCoords, 
                subtree)
    for ki in range(Tree234.maxKeys):
        keyItem = subtree.keyItems()[ki]
        dataItem = subtree.dataItems()[ki]
        if tree.canvas.type(keyItem) != 'text':
            return ('Key item', keyItem, 'is not a text item', subtree)
        if ki < subtree.nKeys and tree.canvas.itemconfigure(
                keyItem, 'fill')[-1] != 'black':
            return ('Key item', keyItem, 'text font color is not black',
                    subtree)
        text = tree.canvas.itemconfigure(keyItem, 'text')[-1]
        if ki < subtree.nKeys and (
                len(text) == 0 or text != str(subtree.keys[ki])):
            return ('Key item', keyItem,
                    'should be an integer but does not match key', text,
                    subtree.keys[ki], ki, subtree)
        elif ki >= subtree.nKeys and text != '':
            return ('Key item', keyItem, 'should be an empty string', text,
                    subtree.keys[ki], ki, subtree)
        fill = tree.canvas.itemconfigure(dataItem, 'fill')[-1]
        if ki < subtree.nKeys and len(fill) == 0:
            return ('Data item', dataItem,
                    'should have a fill color but has none', fill, ki, subtree)
        elif ki >= subtree.nKeys and fill != '':
            return ('Data item', dataItem, 
                    'should be invisible but is filled with', fill, ki, subtree)
    
    for c in range(subtree.nChild):
        result = _invalidItem(
            tree, subtree.children[c], level+1,
            lo=None if c <= 0 else subtree.keys[c - 1],
            hi=None if c >= subtree.nKeys else subtree.keys[c])
                
def validNodes(tree):
    return len(tree.getAllDescendants(tree.getRoot()))

def validItems(tree):
    return _validItems(tree.getRoot())

def _validItems(subtree):
    if subtree is None:
        return 0
    return subtree.nKeys + sum(_validItems(subtree.children[j])
                               for j in range(subtree.nChild))
            
def extremesFirst(seq):
    N = len(seq)
    for i in range(N):
        yield seq[i // 2 if i % 2 == 0 else N - 1 - i // 2]

def middleFirst(seq):
    N = len(seq)
    N2 = N // 2
    for i in range(N):
        yield seq[N2 + i // 2 if i % 2 == 0 else N2 - 1 - i // 2]

def binarySearchOrder(seq):
    N = len(seq)
    lo, hi = 0, N - 1
    queue = [(lo, hi)]
    while len(queue) > 0:
        lo, hi = queue.pop(0)
        if lo <= hi:
            mid = (lo + hi) // 2
            yield seq[mid]
            queue.append((lo, mid - 1))
            queue.append((mid + 1, hi))

def printProblem(problem, tree, operation, seq):
    if problem is not None:
        print('=' * 70)
        print('!' * 70)
        print('=' * 70)
        op = operation.split()
        print('After', op[0], seq, op[1], 'the tree')
        node = problem[-1]
        print('Found problem in node', node, problem[:-1])
        
        tree.print()
    
if __name__ == '__main__':
    # random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = Tree234(title='2-3-4 Tree Tester')
    values = [int(arg) for arg in sys.argv[1:] if arg.isdigit()
    ] if len(sys.argv) > 1 else [i for i in range(1, 96, 3)]

    for name, iseq in [
            ('middle first', middleFirst(values)),
            ('extremes first', extremesFirst(values)),
            ('sorted', sorted(values)), 
            ('reverse sorted', sorted(values)),
            ('random shuffle 1', random.sample(values, k=len(values))),
            ('random shuffle 2', random.sample(values, k=len(values))),
            ('binary search order', binarySearchOrder(values))]:

        print('=' * 60)
        vals = tuple(i for i in iseq)
        print('Starting tests on', name, 'sequence:\n', ' '.join(
            str(v) for v in vals))
        tree.newTree()
        for i, value in enumerate(vals):
            tree.setArgument(str(value))
            tree.insertButton.invoke()
            printProblem(invalidItem(tree), tree, 'inserting into', vals[:i+1])
        print('Finsihed with', validNodes(tree), 'nodes and',
              validItems(tree), 'keys inserted')
        

        
