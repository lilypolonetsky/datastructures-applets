# DONE:
## disable button-use while nodes are still moving
## add highlight for the node being inserted and node being removed/being trickledDown
## have removed node fade-out more gradually

# TO DO:
## combine min and max heap
## change increments


import tkinter as tk
import random
import time


#import pause


class Node(object):
    def __init__(self, k, d):
        self.key  = k
        self.data = d
        
    def __str__(self): 
        return "(" + str(self.key) + "," + repr(self.data) + ")"
        
class Heap(object):
    def __init__(self, size, state="max"):
        self.__size = size
        self.__arr = [None] * self.__size  #an array to store our values
        self.__state = state
        self.__nElems = 0 
        self.__ovals = []      # list of each oval to access later on for swapping
        self.__oElems = 0  
        self.__nums = []       # list of each number-text to access later on for swapping
        self.__arrows = []     # list of each arrow to access for deletion 
     
    def changeState(self, state):
        for i in range(len(self.__ovals)):
            w.delete(self.__ovals[i])
            w.delete(self.__nums[i])
        for i in self.__arrows:
            w.delete(i)
        
        self.__arr = [None] * self.__size  #an array to store our values
        self.__state = state
        self.__nElems = 0 
        self.__ovals = []      # list of each oval to access later on for swapping
        self.__oElems = 0  
        self.__nums = []       # list of each number-text to access later on for swapping
        self.__arrows = []     # list of each arrow to access for deletion 
        
    def buttonState(self, state):
        button1.config(state=state)
        button2.config(state=state) 
        
    #def drawHeap(self):
     #   w.create_window(300,600, window=button1)  
     #   w.create_window(500,600,window=button2)            
     #   #w.create_text(canvas_width/2, 50, font=('calibri', 50), text='MAX HEAP')
     #   button2.config(state="disabled")

              
        
    def swapNodes(self, cur, other, x, y):
        # change increment based on the size of changeX and changeY
        changeX = x
        changeY = y
        increment = 50
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
        
        self.buttonState('disabled')
        try: 
            #print("this is self.__arr before insert", self.__arr)
            self.__arr[self.__nElems] = Node(k, d)
            #print("this is self.__arr after inserting:", self.__arr)
            self.__nElems += 1
        
            positionX = coordinates[0][self.__nElems-1]
            positionY = coordinates[1][self.__nElems-1]
            
            # insert ovals as red
            oval = w.create_oval(positionX, positionY, positionX+50, positionY+50, fill='red')
            text = w.create_text(positionX+25, positionY+25, font=('calibri', 12), text=str(self.__arr[self.__nElems-1].key))
            
            parent = (self.__nElems-2)//2      
            if len(self.__ovals) != 0 and self.__ovals[self.__oElems-1]==None:
                self.__ovals[self.__nElems-1] = oval
                self.__nums[self.__nElems-1] = text
                # only add an arrow if there is already a root node
                if self.__nElems > 1:
                    arrow = w.create_line(coordinates[0][parent]+25, coordinates[1][parent]+50, positionX+20, positionY, arrow=tk.LAST) 
                    self.__arrows[self.__nElems-2] = arrow
            else:
                self.__ovals.append(oval)           # append new oval to end of ovals list
                self.__oElems+=1                    # increment oval amount by 1
                self.__nums.append(text)            # add number to end of num list
                # only add an arrow if there is already a root node
                if self.__nElems > 1:
                    arrow = w.create_line(coordinates[0][parent]+25, coordinates[1][parent]+50, positionX+20, positionY, arrow=tk.LAST) 
                    self.__arrows.append(arrow)
            
            root.update()
            time.sleep(.5)            
            
            self.trickleUp()
            
            # when the trickle up is complete, 
            # change the most recently inserted node to yellow
            w.itemconfig(oval, fill='yellow')
            
            # when the trickle up is complete,
            # re-enable the buttons
            self.buttonState('normal')
            
            # if the heap is full, disable the insert button
            if all(v is not None for v in self.__arr):
                button1.config(state="disabled")
            return True
        except:
            pass
  
    def trickleUp(self):
        cur = self.__nElems-1
        bottom = self.__arr[cur] # the recently inserted Node
        parent = (cur-1) // 2    # its parent's location
        
        # if max heap
        # While cur hasn't reached the root, and cur's parent's
        # key is smaller than the new Node's key
        if self.__state == "max":
            ## add an if for if max heap or min heap
            while cur > 0 and self.__arr[parent].key < bottom.key:
                curX, curY = coordinates[0][cur], coordinates[1][cur]
                parX, parY = coordinates[0][parent], coordinates[1][parent]
                changeX = curX-parX
                changeY = curY-parY
                
                self.swapNodes(cur, parent, changeX, changeY)                                    
                self.__arr[cur] = self.__arr[parent] # move parent down
                cur = parent                         # cur goes up one level
                parent = (cur-1) // 2
                
        # if state is 'min' then check if parent.key is bigger
        if self.__state == "min":
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
        positionX = coordinates[0][cur]
        positionY = coordinates[1][cur]
        return True
    
    # return the key/data pair with the highest priority   
    def remove(self): 
        # disable the buttons while the remove/trickle down is running
        self.buttonState('disabled')
        if self.__nElems == 0:                 
            return None, None # empty heap

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
        # re-enable the buttons when trickle up is complete
        self.buttonState('normal')
        # if there are no nodes left, disable the remove button
        if self.__nElems == 0:
            button2.config(state="disabled") 
        return root.key, root.data
      
    def swapRoot(self):
        # coordinates of the last node
        x, y = coordinates[0][self.__nElems], coordinates[1][self.__nElems]
        # change in coordinates of last node and root node
        changeX = coordinates[0][0]-x
        changeY = coordinates[1][0]-y
        
        
        if self.__nElems > 0:
            w.delete(self.__arrows[self.__nElems-1])
            self.__arrows[self.__nElems-1] = None
        
        # change the last node that is swapped to the root to red 
        w.itemconfig(self.__ovals[self.__nElems], fill='red')
         
        increment = 50
        w.itemconfig(self.__ovals[0], fill='red')
        # swap the root node with the last node
        for i in range(increment):
            
            w.move(self.__ovals[0], 0, -150/increment)
            w.move(self.__nums[0], 0, -150/increment)            
            w.move(self.__ovals[self.__nElems], changeX/increment, changeY/increment)
            w.move(self.__nums[self.__nElems], changeX/increment, changeY/increment)
            root.update()
        
        # put last element in root position
        self.__ovals[0] = self.__ovals[self.__nElems]
        self.__nums[0] = self.__nums[self.__nElems]
        # remove the last node from the oval list
        self.__ovals[self.__nElems] = None
        self.__nums[self.__nElems] = None 
        
        root.update()    
        
        return True
    
    
    def __trickleDown(self, cur = 0, size = -1):
        if size == -1: size = self.__nElems
        top = self.__arr[cur]   # save the Node at the root
        
        # while the current Node has at least one child...
        while cur < size // 2: 
            leftChild  = 2*cur + 1
            rightChild = leftChild + 1
            largerChild = leftChild
            
            #if this is a max heap
            if self.__state == "max":
                # find smaller child (right child might not exist)
                if rightChild < size and \
                   self.__arr[leftChild].key < self.__arr[rightChild].key:
                    largerChild = rightChild
                    
            if self.__state == "min":
                # find smaller child (right child might not exist)
                if rightChild < size and \
                   self.__arr[leftChild].key > self.__arr[rightChild].key:
                    largerChild = rightChild
                    
            # if this is a max heap
            # done trickling if top's key is >= the key of larger child
            if self.__state =="max" and top.key >= self.__arr[largerChild].key:
                break
            elif self.__state =="min" and top.key <= self.__arr[largerChild].key:
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
        
        # when cur makes it to its correct position in the trickle down,
        # change it back to yellow
        w.itemconfig(self.__ovals[cur], fill='yellow')                
        
        return True
    
        

    
coordinates = [ [375, 175, 575, 75, 275, 475, 675, 25, 125, 225, 325, 425, 525, 625, 725],
                [100, 200, 200, 300, 300, 300, 300, 400, 400, 400, 400, 400, 400, 400, 400] ]


h = Heap(15)


root = tk.Tk()
canvas_width = 800
canvas_height = 800    
root.title("Heaps")
w = tk.Canvas(root, width = canvas_width, height=canvas_height, bg='lightblue')
w.pack()   

# this is the command called by the button to insert a node
def insert_node():  
    h.insert(random.randint(0, 100), chr(ord('A') + 1))
  
def remove_node():
    h.remove()

# create insert/remove buttons
# and initialize remove button to disabled
def runMaxHeap():
    # delete everything from screen except buttons
    
    minHeap.config(height=2, width=10)
    maxHeap.config(height=3, width=15)
    h.changeState("max")
# when min heap button in clicked, enlarge it to show current heap is min heap
def runMinHeap():
    
    minHeap.config(height=3, width=15)
    maxHeap.config(height=2, width=10)    
    h.changeState("min")  


### all of our buttons ####
button1=tk.Button(root,text='Insert', command=insert_node)
button2 = tk.Button(root,text='Remove', command=remove_node)
w.create_window(300,600, window=button1)  
w.create_window(500,600,window=button2)    
button2.config(state="disabled")

# buttons for changing between min heap and max heap    
maxHeap=tk.Button(root, command=runMaxHeap, relief = 'groove', highlightbackground = "pink", text='Max Heap', height=3, width=15)
w.create_window(325,50, window=maxHeap) 
minHeap=tk.Button(root, text='Min Heap', height=2, width=10,highlightbackground = "pink", command=runMinHeap)
w.create_window(475,50,window=minHeap)  
# when max heap button in clicked, enlarge it to show current heap is max heap
      


## TO DO:
## when min or max heap button is clicked,
## clear everything that is already on the screen (in case of changing in the middle of a heap)
## make runMaxHeap and runMinHeap run their respective heaps

#h.drawHeap()
root.mainloop()
