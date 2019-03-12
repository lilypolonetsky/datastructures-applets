## fix bug causing TRUE ERROR!
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
        self.__arr = [None] * size  #an array to store our values
        self.__nElems = 0 
        self.__ovals = []  # list of each oval to access later on for swapping
        self.__oElems = 0
        self.__nums = []    # list of each number-text to access later on for swapping
        self.__arrows = []  # list of each arrow to access for deletion 
        
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
        button1=tk.Button(root,text='Insert',bg='pink',command=insert_node)
        w.create_window(300,600, window=button1)  
        button2 = tk.Button(root,text='Remove', command=remove_node)
        w.create_window(500,600,window=button2)            
        w.create_text(canvas_width/2, 50, font=('calibri', 50), text='MIN HEAP')  

        
        
    def swapNodes(self, cur, other, x, y):
        changeX = x
        changeY = y
        increment = 100
        for i in range(increment):  
            w.move(self.__ovals[cur], -(changeX/increment), -(changeY/increment))
            w.move(self.__ovals[other], (changeX/increment), (changeY/increment))
            w.move(self.__nums[cur], -(changeX/increment), -(changeY/increment))
            w.move(self.__nums[other], (changeX/increment), (changeY/increment))
            root.update() 
        self.__ovals[cur], self.__ovals[other] = self.__ovals[other], self.__ovals[cur]
        self.__nums[cur], self.__nums[other] = self.__nums[other], self.__nums[cur]
        
        return True
     
     

    def insert(self, k, d):
   
        # Place new node at end of heap & trickle it up

        try: 
            #print("this is self.__arr before insert", self.__arr)
            self.__arr[self.__nElems] = Node(k, d)
            #print("this is self.__arr after inserting:", self.__arr)
            self.__nElems += 1
            print("this is self.__nElems after instering now", self.__nElems)
        
            positionX = coordinates[0][self.__nElems-1]
            positionY = coordinates[1][self.__nElems-1]
            oval = w.create_oval(positionX, positionY, positionX+50, positionY+50, fill='yellow')
            text = w.create_text(positionX+25, positionY+25, font=('calibri', 12), text=str(self.__arr[self.__nElems-1].key))
            # list of each oval to access later on for swapping
            
            ## Goal here is to insert new node into self.__ovals list, replace the 
            ## last node which should be a None.
            ## of course, if this list is empty, or doesn't have a None, then we just append a new oval
            ## to the end of the list.
            ## this is to take care of then case where you re-insert an element after removing an element
            
            ## same thing with __nums and __arrows
            parent = (self.__nElems-2)//2            
            
            
            if len(self.__ovals) != 0 and self.__ovals[self.__oElems-1]==None:
                self.__ovals[self.__nElems-1] = oval 
                self.__nums[self.__nElems-1] = text
                 
                print("we are about to replace the None in arrow, here is arrow ", self.__arrows)
                print("we are about to replace the None in arrow, here is arrow ", self.__arrows)
            
                if self.__nElems > 1:
                    arrow = w.create_line(coordinates[0][parent]+25, coordinates[1][parent]+50, positionX+20, positionY, arrow=tk.LAST) 
                    self.__arrows[self.__nElems-2] = arrow
                print("we replaced the None in arrow, here is arrow ", self.__arrows)                
                             
                    
            else:
                self.__ovals.append(oval)
                self.__oElems+=1
                self.__nums.append(text)
                if self.__nElems != 1:
                    arrow = w.create_line(coordinates[0][parent]+25, coordinates[1][parent]+50, positionX+20, positionY, arrow=tk.LAST) 
                    self.__arrows.append(arrow)
                
            

            return True
        except:
            pass
  
            
    def trickleUp(self):
        cur = self.__nElems-1
        bottom = self.__arr[cur] # the recently inserted Node
        parent = (cur-1) // 2    # its parent's location
        # While cur hasn't reached the root, and cur's parent's
        # key is bigger than the new Node's key
        while cur > 0 and self.__arr[parent].key > bottom.key:
            
            curX, curY = coordinates[0][cur], coordinates[1][cur]
            parX, parY = coordinates[0][parent], coordinates[1][parent]
            changeX = curX-parX
            changeY = curY-parY
            
            self.swapNodes(cur, parent, changeX, changeY)                                    
            self.__arr[cur] = self.__arr[parent] # move parent down
            cur = parent                         # cur goes up one level
            parent = (cur-1) // 2
         
        # when we reach this point, either cur has reached the 
        # root, or cur's parent's key is >= the new node's key. 
        # so place the new node into the current spot on the tree.
        self.__arr[cur] = bottom
        return True
    
    
    
    # return the key/data pair with the highest priority   
    def remove(self): 
        if self.__nElems == 0: return None, None # empty heap

        # save the root position
        root = self.__arr[0]
        # decrease number of elements in arr since we will be removing the root
        
        self.__nElems -= 1

        
        # Now place the last Node in the heap into the 
        # root location
        self.__arr[0] = self.__arr[self.__nElems]        
        self.__arr[self.__nElems] = None
        
        # first swap the root
        self.swapRoot()
        # then trickle down normally
        self.__trickleDown()
        
        return root.key, root.data
      
    
    def swapRoot(self):
        # coordinates of the last node
        x, y = coordinates[0][self.__nElems], coordinates[1][self.__nElems]
        # change in coordinates of last node and root node
        changeX = coordinates[0][0]-x
        changeY = coordinates[1][0]-y
        
        # remove the node at the root
        w.delete(self.__ovals[0])
        w.delete(self.__nums[0])        
        # remove the last arrow
        
        print("this is nElems before we delete an arrow", self.__nElems)
        print("this is arrow list before delete ", self.__arrows)
        
        ### this line isnt working ###
        w.delete(self.__arrows[self.__nElems-1])
        self.__arrows[self.__nElems-1] = None
        print("this is arrow list after delete ", self.__arrows)
        
        
        
        increment = 100
        # swap the root node with the last node
        for i in range(increment):
            w.move(self.__ovals[self.__nElems], changeX/increment, changeY/increment)
            w.move(self.__nums[self.__nElems], changeX/increment, changeY/increment)
            root.update()
        
        #print("this is oval after delete root", self.__ovals)
        
        # put last element in root position
        self.__ovals[0] = self.__ovals[self.__nElems]
        self.__nums[0] = self.__nums[self.__nElems]
        # remove the last node from the oval list
        self.__ovals[self.__nElems] = None
        self.__nums[self.__nElems] = None 
        
        #self.__oElems-=1
        #print("this is oval after swapping last node with root and removing root:", self.__ovals)
        #print("this is length of oval after removing root and swap:", self.__oElems)
        root.update()    
        
        return True
    
    
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
            if rightChild < size and \
               self.__arr[leftChild].key > self.__arr[rightChild].key:
                largerChild = rightChild

                
            # done trickling if top's key is <= the key of larger child
            if top.key <= self.__arr[largerChild].key:
                break
            
            curX = coordinates[0][cur]
            curY = coordinates[1][cur]
            largX = coordinates[0][largerChild]
            largY = coordinates[1][largerChild]
            changeX = curX-largX
            changeY = curY-largY 

            
            # shift child up
            self.__arr[cur] = self.__arr[largerChild]
            
            self.swapNodes(cur, largerChild, changeX, changeY)
            
            cur = largerChild            # go down
            
        # when we make it to this point, either cur is a leaf, or
        # cur is at the highest point in the tree where the root's key
        # is larger than both children. So place the old root node there
        
        self.__arr[cur] = top  # move original root to its correct position 
        
        return True
    
coordinates = [ [375, 175, 575, 75, 275, 475, 675, 25, 125, 225, 325, 425, 525, 625, 725],
                [100, 200, 200, 300, 300, 300, 300, 400, 400, 400, 400, 400, 400, 400, 400] ]


h = Heap(15)

# this is the command called by the button to insert a node
def insert_node():
    
    h.insert(random.randint(0, 100), chr(ord('A') + 1))
    h.trickleUp()


def remove_node():
    h.remove()
    
root = tk.Tk()
canvas_width = 800
canvas_height = 800    
# Make the canvas with title 'Heaps' 
root.title("Min Heap Data Vis")
w = tk.Canvas(root, width = canvas_width, height=canvas_height, bg='pink')
w.pack()   
#w.create_text(canvas_width/2, 50, font=('calibri', 50), text='')

h.drawHeap()
root.mainloop()


 
 
 
 
 
 
 
 

##test that this heap follows min-heap conditions
#def isHeap(self, cur = 0):
    ## if the current Node has no children...
    #if cur > self.__nElems // 2: return True
    
    #parent = (cur-1) // 2
    #leftChild  = 2*cur + 1
    #rightChild = leftChild + 1 
    ##If the current node has a left or right children then recurse further into list
    #if self.__nElems >= leftChild:
        #self.isHeap(leftChild)
    #if self.__nElems >= rightChild:
        #self.isHeap(rightChild)  
        
    ##if a child node is greater than its parent, the heap is not a max-heap
    #if self.__arr[parent] and self.__arr[cur].key > self.__arr[parent].key: return False
    
    ##otherwise, it is a max-heap
    #return True 

     

#def displayHeap(self):
    #print("heapArray: ", end="")
    #for m in range(self.__nElems):
        #print(str(self.__arr[m]) + " ", end="")
    #print()

  
#def __display(self, cur, indent):
    #if cur < self.__nElems:
        #leftChild  = 2*cur + 1      
        #print((" " * indent) + str(self.__arr[cur]))
        #if leftChild < self.__nElems:
            #self.__display(leftChild,   indent+4)
            #self.__display(leftChild+1, indent+4)

#def display(self): 
    #self.__display(0, 0)
#def length(self):
    #return self.__nElems
#def getElem(self, x):
    #return self.__arr[x]
