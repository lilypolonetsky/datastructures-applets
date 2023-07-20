from RedBlackTree import *
import random
import sys
                
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

def printProgress(trial, trials, satisfied):
    print(('{} of {} trial{} complete, {:3.1f}% with '
           '{} satisfying all rules, {:3.1f}%').format(
               trial, trials, '' if trials == 1 else 's', 100 * trial / trials,
               satisfied, 100 * satisfied / trial))
    
if __name__ == '__main__':
    # random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = RedBlackTree(title='Red-Black Tree Tester')
    values = [int(arg) for arg in sys.argv[1:] if arg.isdigit()
    ] if len(sys.argv) > 1 else [i for i in range(1, 96, 3)]

    rulesSatisfied = 0
    nNodes = 2 ** tree.MAX_LEVEL - 1
    trials = 1000
    for trial in range(trials):
        tree.emptyAndFill(nNodes)
        satisfied = len(tree.canvas.itemconfigure(tree.measures[3],
                                                  'text')[-1]) > 0
        height = tree.getHeight(0)
        tree.startAnimations()
        if satisfied:
            rulesSatisfied += 1
            print('Trial', trial, 'satisfied the rules')
            tree.wait(0.1)
        else:
            tree.wait(0)
        if height != tree.MAX_LEVEL:
            print('Tree height {} not equal to {}'.format(
                height, tree.MAX_LEVEL))
            tree.wait(1)
                  
        if trial % 100 == 99 or trial == trials - 1:
            printProgress(trial + 1, trials, rulesSatisfied)
            
    tree.runVisualization()
    

        
