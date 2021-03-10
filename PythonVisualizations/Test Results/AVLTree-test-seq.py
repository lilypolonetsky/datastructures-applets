from AVLTree import *
from coordinates import *
import random
import sys

def invalidIndex(tree):
    heightLabels = set(tree.canvas.find_withtag('height'))
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
            valueText, heightText = node.drawnValue.items[2:4]
            if tree.canvas.type(valueText):
                if (tree.canvas.type(valueText) != 'text' or
                    distance2(node.center, tree.canvas.coords(valueText)) > 1):
                    return (i, 'Node visible but mispositioned',
                            node.center, tree.canvas.coords(valueText),
                            valueText)
            if tree.canvas.type(heightText) != 'text':
                return (i, 'Node height text type is "{}", not "text"'.format(
                    tree.canvas.type(heightText)))
            if distance2(tree.nodeHeightCoords(*node.center), 
                         tree.canvas.coords(heightText)) > 1:
                return (i,
                        'Node height text position is {} instead of {}'.format(
                    tree.canvas.coords(heightText), 
                    tree.nodeHeightCoords(*node.center)))
            if heightText not in heightLabels:
                return (i, 'Node height text not in text items tagged with '
                        '"height"')
            heightLabels.discard(heightText)
            if abs(tree.heightDiff(node)) > 1:
                return (i, 'Height difference too large', tree.heightDiff(node))
    visible = [label for label in heightLabels 
               if tree.canvas.type(label) == 'text']
    if len(visible) > 0:
        return (-1, 'Found {} unrelated height labels: {} at {}'.format(
            len(visible), visible, [tree.canvas.coords(v) for v in visible]))
                
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

def printProblem(problem, tree, operation, seq):
    if problem is not None:
        print('=' * 70)
        print('!' * 70)
        print('=' * 70)
        op = operation.split()
        print('After', op[0], seq, op[1], 'the tree')
        print('Found problem at', problem)
        for node in tree.getAllDescendants(0):
            print('index {:2d} {} height={}'.format(tree.getIndex(node), node,
                                                    tree.getHeight(node)))
    
if __name__ == '__main__':
    # random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = AVLTree(title='AVL Tree Tester')
    values = [int(arg) for arg in sys.argv[1:] if arg.isdigit()
    ] if len(sys.argv) > 1 else [i for i in range(1, 96, 3)]

    for name, iseq, dseq in [
            ('middle first', middleFirst(values), middleFirst(values)),
            ('extremes first', extremesFirst(values), middleFirst(values)),
            ('sorted', sorted(values), sorted(values, reverse=True)), 
            ('reverse sorted', sorted(values, reverse=True), sorted(values)),
            ('random shuffle 1', random.sample(values, k=len(values)),
             random.sample(values, k=len(values))),
            ('random shuffle 2', random.sample(values, k=len(values)),
             random.sample(values, k=len(values))),
            ('binary search order', binarySearchOrder(values), sorted(values))]:

        print('=' * 60)
        vals = tuple(i for i in iseq)
        print('Starting tests on', name, 'sequence:\n', ' '.join(
            str(v) for v in vals))
        tree.newTree()
        for i, value in enumerate(vals):
            tree.setArgument(str(value))
            tree.insertButton.invoke()
            printProblem(invalidIndex(tree), tree, 'inserting into', vals[:i+1])
        print('Finsihed with', validNodes(tree), 'nodes inserted')
        
        dvals = tuple(d for d in dseq)
        print('Deleting nodes in this order:\n', ' '.join(
            str(v) for v in dvals))
        for i, value in enumerate(dvals):
            tree.setArgument(str(value))
            tree.deleteButton.invoke()
            printProblem(invalidIndex(tree), tree, 'deleting from', dvals[:i+1])

        
