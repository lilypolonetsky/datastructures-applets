from BinaryTree import *
import random, sys, collections
                
def validNodes(tree):
    return len(tree.getAllDescendants(0))

def maxHeightDiff(tree):
    maxDiff = 0
    for node in tree.getAllDescendants(0):
        maxDiff = max(maxDiff, abs(tree.heightDiff(node)))
    return maxDiff

def validTree(tree, node=0, parent=None):
    if tree.getNode(node) is None:
        return True
    if parent is not None:
        parentKey = tree.getNode(parent).getKey()
        nodeKey = tree.getNode(node).getKey()
        if (nodeKey >= parentKey) if node % 2 == 1 else (nodeKey <= parentKey):
            return False
    return all(validTree(tree, child, node) for child in
               (node * 2 + 1, node * 2 + 2))
            
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

def printProgress(trial, trials, satisfied):
    print(('{} of {} trial{} complete, {:3.1f}% with '
           '{} satisfying all rules, {:3.1f}%').format(
               trial, trials, '' if trials == 1 else 's', 100 * trial / trials,
               satisfied, 100 * satisfied / trial))
    
if __name__ == '__main__':
    # random.seed(3.14159)  # Use fixed seed for testing consistency
    values = [int(arg) for arg in sys.argv[1:] if arg.isdigit()
    ] if len(sys.argv) > 1 else [i for i in range(1, 96, 3)]
    tree = BinaryTree(title='Binary Tree Tester', values=values)

    trials, satisfied = min(len(values) ** 2, 10000), 0
    histByMaxDiff = collections.defaultdict(lambda: 0)
    animate = len(values) <= 10
    for trial in range(trials):
        tree.emptyTree()
        tree.display()
        for num in random.sample([v for v in values], len(values)):
            if animate:
                tree.setArgument(str(num))
                tree.buttons[0].invoke()
            else:
                tree.insert(num, animation=False)
        maxDiff = maxHeightDiff(tree)
        histByMaxDiff[maxDiff] += 1
        balanced = maxDiff <= 1
        height = tree.getHeight(0)
        size = validNodes(tree)
        tree.startAnimations()
        if not validTree(tree):
            print('Tree is not a binary search tree!')
            tree.print()
        if balanced:
            satisfied += 1
            print('Trial', trial, 'satisfied the balance conditions')
            tree.wait(0.1)
        else:
            tree.wait(0)
        expectedHeight = min(tree.MAX_LEVEL, len(values))
        if height != expectedHeight:
            print('Tree height {} not equal to {}'.format(
                height, expectedHeight))
            tree.wait(1)
        elif size == len(tree.nodes):
            print('Tree completely filled with {} nodes'.format(size))
            tree.wait(1)
        tree.stopAnimations()
                  
        if trial % 100 == 99 or trial == trials - 1:
            printProgress(trial + 1, trials, satisfied)

    print('Final tree:')
    tree.print()
    print('  size = {}, height = {}, max height diff = {}, balanced = {}'
          .format(size, height, maxDiff, balanced))
    
    print('\n', '=' * 77)
    print('Tree balance histogram')
    for diff in sorted(histByMaxDiff.keys()):
        print('{:2d}: {} {:3.1f}%'.format(
            diff, histByMaxDiff[diff], 100 * histByMaxDiff[diff] / trials))
    # tree.runVisualization()
