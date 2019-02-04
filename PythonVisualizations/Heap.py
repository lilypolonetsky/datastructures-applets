import tkinter as tk
import random
import time

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
        
    # Grow the array, if necessary    
    def __grow(self):
        oldSize = len(self.__arr)
        newSize = oldSize * 2    # how big should the new array be?
        
        # allocate the new array and copy the old array into it
        newA = [None] * newSize
        for i in range(oldSize): 
            newA[i] = self.__arr[i]
        self.__arr = newA           

    def insert(self, k, d):
        # grow array if the heap is full
        if self.__nElems == len(self.__arr): self.__grow()   
        
        # Place new node at end of heap & trickle it up
        self.__arr[self.__nElems] = Node(k, d)
        self.__trickleUp(self.__nElems)
        self.__nElems += 1
        return True
    
       
    def __trickleUp(self, cur):
        bottom = self.__arr[cur] # the recently inserted Node
        parent = (cur-1) // 2    # its parent's location
       
        # While cur hasn't reached the root, and cur's parent's
        # key is smaller than the new Node's key
        while cur > 0 and self.__arr[parent].key < bottom.key:
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
    
    # this heap is now a min-heap       
    def __trickleDown(self, cur = 0, size = -1):
        if size == -1: size = self.__nElems
        top = self.__arr[cur]   # save the Node at the root
        
        # while the current Node has at least one child...
        while cur < size // 2: 
            leftChild  = 2*cur + 1
            rightChild = leftChild + 1
            
            # find smaller child (right child might not exist)
            largerChild = leftChild
            if rightChild > size and \
               self.__arr[leftChild].key < self.__arr[rightChild].key:
                largerChild = rightChild
                
            # done trickling if top's key is >= the key of larger child
            if top.key >= self.__arr[largerChild].key:
                break
            
            # shift child up
            self.__arr[cur] = self.__arr[largerChild]
            cur = largerChild            # go down
            
        # when we make it to this point, either cur is a leaf, or
        # cur is at the highest point in the tree where the root's key
        # is larger than both children. So place the old root node there
        
        self.__arr[cur] = top  # move original root to its correct position 
    
    #test that this heap follows min-heap conditions
    def isHeap(self, cur = 0):
        # if the current Node has no children...
        if cur > self.__nElems // 2: return True
        
        parent = (cur-1) // 2
        leftChild  = 2*cur + 1
        rightChild = leftChild + 1 
        #If the current node has a left or right children then recurse further into list
        if self.__nElems >= leftChild:
            self.isHeap(leftChild)
        if self.__nElems >= rightChild:
            self.isHeap(rightChild)  
            
        #if a child node is greater than its parent, the heap is not a max-heap
        if self.__arr[parent] and self.__arr[cur].key > self.__arr[parent].key: return False
        
        #otherwise, it is a max-heap
        return True 
    
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
    def length(self):
        return self.__nElems
    def getElem(self, x):
        return self.__arr[x]
 
#### THIS IS WHERE I STARTED TO PLAY WITH TKinter #######   
#root = tk.Tk()

def drawMaxHeap(heap):
    
    for i in range(0, heap.length()):
        positionX = coordinates[0][i]
        positionY = coordinates[1][i]
        #else:
            #positionX = (i*100+150)
            #positionY = ((i-1)//2)*100+200
        w.create_oval(positionX, positionY, positionX+50, positionY+50, fill='yellow')
        w.create_text(positionX+25, positionY+25, font=('calibri', 12), text=str(heap.getElem(i).key))
# This function doesn't really mean much, im just displaying the values on the screen
# we need to find a way to make it look like a heap, like a pyramid
# maybe we can look at his __display() function for inspiration/guidance    
    
coordinates = [ [375, 175, 575, 75, 275, 475, 675, 25, 125, 225, 325, 425, 525, 625, 725],
                [100, 200, 200, 300, 300, 300, 300, 400, 400, 400, 400, 400, 400, 400, 400] ]
root = tk.Tk()
canvas_width = 800
canvas_height = 800

 # Make the canvas with title 'Heaps' 
root.title("Heaps Data Vis")
w = tk.Canvas(root, width = canvas_width, height=canvas_height, bg='lightblue')
w.pack()
w.create_text(canvas_width/2, 50, font=('calibri', 50), text='HEAPS')


def __main():
    
    
    h = Heap(3)  # make a new heap with maximum of 31 elements
    
    for i in range(10):  # insert 10 items
        h.insert(random.randint(0, 10000), chr(ord('A') + 1 + i))
    
    drawMaxHeap(h)
    #ans = input("Enter first letter of show, insert, remove, empty, test isHeap: ")
    #while ans:
        
        #if ans[:1] == 'e':  # empty the heap
            #h = Heap(3)    
        #elif ans[:1] == 'i':  # insert
            #key  = int(input("Enter integer key to insert: "))
            #data = input("Enter data to insert: ")
            #if not h.insert(key, data):
                #print("Can't insert; heap is full")
                
        #elif ans[:1] == 'r':  # remove
            #key, data = h.remove() 
            #if key == None:
                #print("Can't remove; heap empty")
            #else:
                #print("Removed this key/data pair from heap: " + \
                      #str(key) + ", " + repr(data))
                
        #elif ans[:1] == 't':  # Test the min-heap conditions
            #print("It is ", h.isHeap(), "that this heap is a min-heap" )

        #else:
            #print("Invalid command");
        #w.delete("all")
        #w.create_text(canvas_width/2, 50, font=('calibri', 50), text='HEAPS')
        #drawMaxHeap(h, w)
    
    
#if __name__ == '__main__':
    #__main()       
# create button for REMOVE and ADD which will trickle_up or trickle_down 

# Perhaps have option for a min-heap
__main()
root.mainloop()
