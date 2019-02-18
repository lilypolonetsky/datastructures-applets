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
        
        
    def drawHeap(self):
        w.delete("all")
        #nodes = []        
        button1=tk.Button(root,text='Insert',bg='blue',fg='red',command=insert_node)
        w.create_window(300,600, window=button1)  
        button2 = tk.Button(root,text='Remove', command=remove_node)
        w.create_window(500,600,window=button2)            
        #w.delete(nodes)
        w.create_text(canvas_width/2, 50, font=('calibri', 50), text='HEAPS')  
        for i in range(self.__nElems):
            parent = (i-1)//2
            positionX = coordinates[0][i]
            positionY = coordinates[1][i]
            oval = w.create_oval(positionX, positionY, positionX+50, positionY+50, fill='yellow')
            text = w.create_text(positionX+25, positionY+25, font=('calibri', 12), text=str(self.__arr[i].key))
            if i != 0:
                w.create_line(coordinates[0][parent]+25, coordinates[1][parent]+50, positionX+20, positionY, arrow=tk.LAST)
            #nodes.append([oval,text])
            

    def insert(self, k, d):
        # grow array if the heap is full
        #if self.__nElems == len(self.__arr): self.__grow()   
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
            print("left child:", leftChild)
            print("right child:", rightChild)
            
            # find smaller child (right child might not exist)
            largerChild = leftChild
            if rightChild < size and \
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
 

         
    
coordinates = [ [375, 175, 575, 75, 275, 475, 675, 25, 125, 225, 325, 425, 525, 625, 725],
                [100, 200, 200, 300, 300, 300, 300, 400, 400, 400, 400, 400, 400, 400, 400] ]


h = Heap(15)

def insert_node():
    h.insert(random.randint(0, 10000), chr(ord('A') + 1))
    h.drawHeap()
def remove_node():
    h.remove()
    h.drawHeap()
    
root = tk.Tk()
canvas_width = 800
canvas_height = 800    
# Make the canvas with title 'Heaps' 
root.title("Heaps Data Vis")
w = tk.Canvas(root, width = canvas_width, height=canvas_height, bg='lightblue')
w.pack()   
w.create_text(canvas_width/2, 50, font=('calibri', 50), text='HEAPS')
h.drawHeap()


root.mainloop()
