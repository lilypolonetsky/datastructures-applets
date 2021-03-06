from AVLTree import *
from coordinates import *
import random
import sys

V = vector

def invalidIndex(tree):
    for i in range(len(tree.nodes)):
        node = tree.nodes[i]
        parent = (i - 1) // 2
        if node:
            if parent >= 0:
                p = tree.nodes[parent]
                if p and (p.getKey() <= node.getKey() and i % 2 == 1 or
                          p.getKey() >= node.getKey() and i % 2 == 0):
                    return (i, 'Node value out of order with respect to parent',
                            parent)
            valueText = node.drawnValue.items[2]
            if tree.canvas.type(valueText):
                if (tree.canvas.type(valueText) != 'text' or
                    V(V(node.center) - 
                      V(tree.canvas.coords(valueText))).len2() > 1):
                    return (i, 'Node visible but mispositioned',
                            node.center, tree.canvas.coords(valueText),
                            valueText)
            if abs(tree.heightDiff(node)) > 1:
                return (i, 'Height difference too large', tree.heightDiff(node))
            
def validNodes(tree):
    return len(tree.getAllDescendants(0))
            
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
        
if __name__ == '__main__':
    # random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = AVLTree()
    values = [int(arg) for arg in sys.argv[1:] if arg.isdigit()
    ] if len(sys.argv) > 1 else [i for i in range(1, 96, 3)]

    for name, seq in [
            ('middle first', middleFirst(values)),
            ('extremes first', extremesFirst(values)),
            ('sorted', sorted(values)), 
            ('reverse sorted', sorted(values, reverse=True)),
            ('random shuffle 1', random.sample(values, k=len(values))),
            ('random shuffle 2', random.sample(values, k=len(values))),
            ('binary search order', binarySearchOrder(values))]:

        print('=' * 60)
        vals = tuple(i for i in seq)
        print('Starting tests on', name, 'sequence:\n', vals)
        tree.newTree()
        for i, value in enumerate(vals):
            tree.setArgument(str(value))
            tree.insertButton.invoke()
            index = invalidIndex(tree)
            if index is not None:
                print('=' * 70)
                print('!' * 70)
                print('=' * 70)
                print('After inserting', vals[:i+1], 'into the empty tree')
                print('Found problem at index', index)
                for node in self.getAllDescendants(0):
                    print('index {:2d} {}'.format(
                        tree.getIndex(node), node.drawnValue))
        print('Finsihed with', validNodes(tree), 'nodes inserted')
        
