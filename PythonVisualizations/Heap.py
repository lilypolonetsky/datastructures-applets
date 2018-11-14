#Heap Visualization 

# MIN HEAP:

import random

class Node(object):
    def __init__(self, k, d):
        self.key  = k
        self.data = d
        
    def __str__(self): 
        return "(" + str(self.key) + "," + repr(self.data) + ")"
        
class Heap(object):
    def __init__(self, size):
        self.__arr = [None] * size
        self.__nElems = 0        

    def insert(self, k, d):
        # if the heap is full, make the heap bigger so that insert cannot fail
        if self.__nElems == len(self.__arr):
            self.__arr = self.__arr * 2
        
        # Place new node at end of heap & trickle it up
        self.__arr[self.__nElems] = Node(k, d)
        self.__trickleUp(self.__nElems)
        self.__nElems += 1
        return True
          
    def __trickleUp(self, cur):
        bottom = self.__arr[cur] # the recently inserted Node
        parent = (cur-1) // 2    # its parent's location
       
        # While cur hasn't reached the root, and cur's parent's
        # key is bigger than the new Node's key
        while cur > 0 and self.__arr[parent].key > bottom.key:
            self.__arr[cur] = self.__arr[parent] # move parent down
            cur = parent                         # cur goes up one level
            parent = (cur-1) // 2
         
        # when we reach this point, either cur has reached the 
        # root, or cur's parent's key is >= the new node's key. 
        # so place the new node into the current spot on the tree.
        self.__arr[cur] = bottom
    
    # return the key/data pair with the highest priority   
    def remove(self): 
        if self.__nElems == 0: return None, None # empty heap

        # the answer will be the key/data from the root node
        root = self.__arr[0]
        self.__nElems -= 1
        
        # Now place the last Node in the heap into the 
        # root location, and trickle it down
        self.__arr[0] = self.__arr[self.__nElems]
        self.__trickleDown()
        
        return root.key, root.data
           
    def __trickleDown(self, cur = 0, size = -1):
        if size == -1: size = self.__nElems
        top = self.__arr[cur]   # save the Node at the root
        
        # while the current Node has at least one child...
        while cur < size // 2: 
            leftChild  = 2*cur + 1
            rightChild = leftChild + 1
            
            # find smaller child (right child might not exist)
            smallerChild = leftChild
            if rightChild < size and \
               self.__arr[leftChild].key > self.__arr[rightChild].key:
                smallerChild = rightChild
                
            # done trickling if top's key is <= the key of smaller child
            if top.key <= self.__arr[smallerChild].key:
                break
            
            # shift child up
            self.__arr[cur] = self.__arr[smallerChild]            
            cur = smallerChild            # go down
            
        # when we make it to this point, either cur is a leaf, or
        # cur is at the highest point in the tree where the root's key
        # is larger than both children. So place the old root node there
        
        self.__arr[cur] = top  # move original root to its correct position 
        
        
    def __isHeap(self, cur = 0, size = -1):
        if size == -1: size = self.__nElems
        
        top = self.__arr[cur]   # save the Node at the root
        
        # define left and right children in terms of cur
        leftChild  = 2*cur + 1
        rightChild = leftChild + 1        
           
        # if it only has a left child and not a right child
        if leftChild < size and not rightChild < size:
            # if the left child is less than its top
            if self.__arr[leftChild].key < top.key:
                return False
            # if left child is greater than top
            # recurse down to check it's child 
            return self.__isHeap(leftChild, size)
            
        # if it has right child and left child 
        elif rightChild < size and leftChild < size:
            # if either the left child or right child is less than top
            if self.__arr[leftChild].key < top.key or self.__arr[rightChild].key < top.key:
                return False
            # if neither left or right children are less than top
            # recurse down to each of the children to check their left and right children
            return self.__isHeap(leftChild, size) and self.__isHeap(rightChild, size)
     
        # if it has no children, just return True
        else:
            return True


    def isHeap(self):
        return self.__isHeap(cur = 0, size = -1)
                    
       
    def displayHeap(self):
        print("heapArray: ", end="")
        for m in range(self.__nElems):
            print(str(self.__arr[m]) + " ", end="")
        print()
        
    def __display(self, cur, indent):
        if cur < self.__nElems:
            leftChild  = 2*cur + 1      
            print((" " * indent) + str(self.__arr[cur]))
            if leftChild < self.__nElems:
                self.__display(leftChild,   indent+4)
                self.__display(leftChild+1, indent+4)
    
    def display(self): 
        self.__display(0, 0)
        
        
def __main():
   
   
    h = Heap(31)  # make a new heap with maximum of 31 elements
    
    for i in range(30):  # insert 30 items
        h.insert(random.randint(0, 100), chr(ord('A') + 1 + i))

    for i in range(1000):   #insert 1000 more items
        h.insert(random.randint(0, 100), chr(ord('A') + 1 + i))
    
    #confirm that it is still a heap    
    print("It is", h.isHeap(), "that the heap is a minHeap")

    while True:
        ans = input("Enter first letter of show, insert, remove, empty, heap: ")
        if ans[:1] == 's':    # show
            h.display()
            
        elif ans[:1] == 'e':  # empty the heap
            h = Heap(31)
            
        elif ans[:1] == 'i':  # insert
            key  = int(input("Enter integer key to insert: "))
            data = input("Enter data to insert: ")
            if not h.insert(key, data):
                print("Can't insert; heap is full")
                
        elif ans[:1] == 'r':  # remove
            key, data = h.remove() 
            if key == None:
                print("Can't remove; heap empty")
            else:
                print("Removed this key/data pair from heap: " + \
                      str(key) + ", " + repr(data))
        
        elif ans[:1] == 'h':
            print("It is", h.isHeap(), "that the heap is a minHeap")

        else:
            print("Invalid command");
    
if __name__ == '__main__':
    __main()       
        
