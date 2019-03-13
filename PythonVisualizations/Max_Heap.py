# DONE:
## disable button-use while nodes are still moving
## add highlight for the node being inserted and node being removed/being trickledDown
# TO DO:
## let the highlight sit for a second even when there is no trickle up
## combine min and max heap
## have insert/removed node fade-out more gradually
## change increments


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
        self.__ovals = []      # list of each oval to access later on for swapping
        self.__oElems = 0  
        self.__nums = []       # list of each number-text to access later on for swapping
        self.__arrows = []     # list of each arrow to access for deletion 
        
    
    def drawHeap(self):
        w.create_window(300,600, window=button1)  
        w.create_window(500,600,window=button2)            
        w.create_text(canvas_width/2, 50, font=('calibri', 50), text='MAX HEAP')
        button2.config(state="disabled")

    def buttonState(self, state):
        button1.config(state=state)
        button2.config(state=state)           
        
    def swapNodes(self, cur, other, x, y):
        # change increment based on the size of changeX and changeY
        changeX = x
        changeY = y
        increment = 10
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
            print("this is self.__nElems after instering now", self.__nElems)
        
            positionX = coordinates[0][self.__nElems-1]
            positionY = coordinates[1][self.__nElems-1]
            
            # insert ovals as red
            oval = w.create_oval(positionX, positionY, positionX+50, positionY+50, fill='red')
            text = w.create_text(positionX+25, positionY+25, font=('calibri', 12), text=str(self.__arr[self.__nElems-1].key))
            
            # THIS IS NOT WORKING
            # WANT IT TO PAUSE FOR A FEW SECONDS AFTER OVAL IS INSERTED
            # SO THAT EVEN WHEN THERE IS NO TRICKLE UP,
            # IT STILL APPEARS AS RED FOR A FEW SECONDS
            
            #time.sleep(1)
            
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

        # While cur hasn't reached the root, and cur's parent's
        # key is smaller than the new Node's key
        while cur > 0 and self.__arr[parent].key < bottom.key:
            
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
        
        # remove the node at the root
        w.delete(self.__ovals[0])
        w.delete(self.__nums[0])        
        # remove the last arrow
        
        if self.__nElems > 0:
            w.delete(self.__arrows[self.__nElems-1])
            self.__arrows[self.__nElems-1] = None
        
        # change the last node that is swapped to the root to red 
        w.itemconfig(self.__ovals[self.__nElems], fill='red')
         
        increment = 10
        # swap the root node with the last node
        for i in range(increment):
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
            
            # find smaller child (right child might not exist)
            largerChild = leftChild
            if rightChild < size and \
               self.__arr[leftChild].key < self.__arr[rightChild].key:
                largerChild = rightChild

            # done trickling if top's key is >= the key of larger child
            if top.key >= self.__arr[largerChild].key:
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

# this is the command called by the button to insert a node
def insert_node():  
    h.insert(random.randint(0, 100), chr(ord('A') + 1))
  
def remove_node():
    h.remove()
    
root = tk.Tk()
canvas_width = 800
canvas_height = 800    
# Make the canvas with title 'Heaps' 
root.title("Max Heap Data Vis")
w = tk.Canvas(root, width = canvas_width, height=canvas_height, bg='lightblue')
w.pack()   
#w.create_text(canvas_width/2, 50, font=('calibri', 50), text='HEAPS')

button1=tk.Button(root,text='Insert',bg='blue',command=insert_node)
button2 = tk.Button(root,text='Remove', command=remove_node)
h.drawHeap()
root.mainloop()

