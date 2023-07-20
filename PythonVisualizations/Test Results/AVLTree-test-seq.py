from AVLTree import *
from coordinates import *
import random
import sys

def invalidIndex(tree):
    heightLabels = set(tree.canvas.find_withtag('height'))
    for i in range(len(tree.nodes)):
        node = tree.nodes[i]
        if node:
            j, parent = i, (i - 1) // 2
            outOfOrder = []
            while parent >= 0:
                p = tree.nodes[parent]
                if p and (p.getKey() <= node.getKey() and j % 2 == 1 or
                          p.getKey() >= node.getKey() and j % 2 == 0):
                    outOfOrder.append(parent)
                elif p is None:
                    outOfOrder = []
                    break
                j, parent = parent, (parent - 1) // 2
            if outOfOrder:
                return (i, 
                        'Node value out of order with respect to ancestors',
                        [(a, tree.nodes[a]) for a in outOfOrder])
            if parent >= 0:  # If parent chain ended before root
                continue     # Skip remaining tests on this node
            for name, item, itemType, coords, nonEmpty in zip(
                    ('link', 'circle', 'valueText', 'heightText'),
                    node.drawnValue.items, 
                    ('line', 'oval', 'text', 'text'),
                    tree.nodeItemCoords(i, parent=(i - 1) // 2),
                    (('fill',), ('fill',), ('fill', 'text'),  ('fill', 'text'))):
                problem = validateItem(name, item, itemType, coords,
                                       tree.canvas, i, nonEmpty)
                if problem:
                    return problem
                if name == 'heightText':
                    if item not in heightLabels:
                        return (i, 'Node height text not in text items tagged '
                                'with "height"')
                    heightLabels.discard(item)
            if abs(tree.heightDiff(node)) > 1:
                return (i, 'Height difference too large', tree.heightDiff(node))
            
    visible = [label for label in heightLabels 
               if tree.canvas.type(label) == 'text' and
               tree.canvas.itemconfigure(label, 'text')[-1]]
    if len(visible) > 0:
        return (-1, 'Found {} unrelated, visible height label{}: {}'
                .format(len(visible), '' if len(visible) == 1 else 's',
                        ['{} @ {}'.format(v, tree.canvas.coords(v))
                         for v in visible]))

def validateItem(
        name, itemID, itemType, coords, canvas, nodeIndex, nonEmpty=[]):
    problems = []
    if canvas.type(itemID) != itemType:
        problems.append('Node {} item, ID={}, type is {}, not {}'.format(
            name, itemID, canvas.type(itemID), itemType))
    if distance2(canvas.coords(itemID), coords) > 1:
        problems.append('Node {} item, ID={}, coords are {}, not {}'.format(
            name, itemID, canvas.coords(itemID), coords))
    for attrib in nonEmpty:
        val = canvas.itemconfigure(itemID, attrib)[-1]
        if not val:
            problems.append('Node {} item, ID={}, attribute {} is {}'.format(
                name, itemID, attrib, val))
    if problems:
        return (nodeIndex,) + tuple(problems)
                
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
        parent = tree.getParent(problem[0]) if problem[0] > 0 else (
            problem[0] == 0)
        print('Found problem at', problem,
              '' if parent else 'but missing expected parent')
        
        tree.printTree()
    
if __name__ == '__main__':
    # random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = AVLTree(title='AVL Tree Tester')
    values = [int(arg) for arg in sys.argv[1:] if arg.isdigit()
    ] if len(sys.argv) > 1 else [i for i in range(1, 96, 3)]

    for name, iseq, dseq in [
            ('middle first', middleFirst(values), middleFirst(values)),
            ('extremes first', extremesFirst(values), extremesFirst(values)),
            ('sorted', sorted(values), sorted(values)), 
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

        
