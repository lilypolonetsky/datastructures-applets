import time
from tkinter import *
import math
try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *



class Node(object):
    
    # create a linked list node
    #id is used to link the different parts of each node visualization
    def __init__(self, k, color, n=None, id=None):
        self.key = k
        self.id = id
        self.next = n  # reference to next item in list
        self.color = color
          
        
    def __str__(self):
        return "{" + str(self.key) + "}"

class LinkedList(VisualizationApp):
    nextColor = 0
    WIDTH = 800
    HEIGHT = 400
    CELL_SIZE = 50
    CELL_BORDER = 2 
    CELL_WIDTH = 120
    CELL_HEIGHT = 50
    CELL_GAP = 20
    DOT_SIZE = 10
    LL_X0 = 100
    LL_Y0 = 100
    MAX_SIZE=20
    LEN_ROW = 5
    ROW_GAP = 40   
    
    def __init__(self, size=13, title="Linked List", **kwargs):
        super().__init__(title=title, **kwargs)
        self.size = size
        self.title = title        
        self.first = None
        self.prev_id = -1
        self.buttons = self.makeButtons()
        for i in range(size-1, -1, -1):
            self.insert(i)
        self.display_neatly()

    def __len__(self):
        cur = self.first
        ans = 0
        while cur:
            ans += 1
            cur = cur.next
        return ans
    
    # inserts a key/data pair at the start of the list
    def insert(self, key):
        color = self.chooseColor()
        newNode = Node(key, color, self.first)
        self.first = newNode
        return newNode    

    def isEmpty(self):
        return not self.first
    
    def generateId(self):
        self.prev_id+=1
        return "item" + str(self.prev_id)
    
    #pointer arrow for find and delete
    def index(self, position):
        x = position % self.LEN_ROW * (self.CELL_WIDTH + self.CELL_GAP) + self.LL_X0 + self.CELL_WIDTH / 2
        y = position // self.LEN_ROW * (self.CELL_HEIGHT + self.ROW_GAP) + self.LL_Y0
        return x, y
    
    #accesses the next color in the pallete
    #used to assign a node's color
    def chooseColor(self):
        color = drawable.palette[self.nextColor]
        self.nextColor = (self.nextColor + 1) % len(drawable.palette)
        return color
    
    #used to calculate coordinates of cell parts
    def x_y_offset(self, pos):
        x_offset = pos%self.LEN_ROW * (self.CELL_WIDTH + self.CELL_GAP)
        y_offset = pos//self.LEN_ROW*(self.CELL_HEIGHT+self.ROW_GAP) 
        return x_offset, y_offset

    #assigns the coordinates of the cell
    #if the coords is not None- it is the node pre-insertion
    def cellCoords(self, pos, coords):
        x_offset, y_offset = self.x_y_offset(pos)
        if not coords:
            return (self.LL_X0 + x_offset, 
                self.LL_Y0 + y_offset, 
                self.LL_X0 + self.CELL_WIDTH + x_offset,
                self.LL_Y0 + self.CELL_HEIGHT + y_offset)
        return (self.LL_X0 + x_offset ,
                self.LL_Y0- (self.CELL_HEIGHT//2 + self.CELL_HEIGHT)+y_offset,
                self.LL_X0 + self.CELL_WIDTH + x_offset,
                self.LL_Y0 -(self.CELL_HEIGHT//2)+y_offset)
    
    #assigns coordinates for the node's text  
    def cell_text(self, pos, coords):
        x_offset, y_offset = self.x_y_offset(pos)
        if not coords:
            return self.LL_X0 + self.CELL_HEIGHT  + x_offset, self.LL_Y0 + self.CELL_HEIGHT // 2+y_offset
        return  self.LL_X0 + self.CELL_HEIGHT  + x_offset, (self.LL_Y0 -self.CELL_HEIGHT)+y_offset
    
    #assigns coordinates for the dot in the node
    def cell_dot(self, pos, coords):
        x_offset, y_offset = self.x_y_offset(pos)
        if not coords:
            return (self.LL_X0 + self.CELL_HEIGHT*2 - self.DOT_SIZE // 2 + x_offset,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 - self.DOT_SIZE // 2 + y_offset,
                               self.LL_X0 + self.CELL_HEIGHT*2 + self.DOT_SIZE // 2 + x_offset,
                               self.LL_Y0 + self.CELL_HEIGHT // 2 + self.DOT_SIZE // 2+ y_offset)
        return (self.LL_X0 + self.CELL_HEIGHT*2 - self.DOT_SIZE // 2 + x_offset,
                               (self.LL_Y0-self.CELL_HEIGHT )- self.DOT_SIZE // 2 + y_offset,
                               self.LL_X0 + self.CELL_HEIGHT*2 + self.DOT_SIZE // 2 + x_offset,
                               (self.LL_Y0-self.CELL_HEIGHT ) + self.DOT_SIZE // 2+ y_offset)

    #draws a cell based on applicable location, position, and text input
    #draws the arrows linking the nodes
    def createCell(self, pos = 1,  textSize = '12', val = None, cur = None, color= None, arrow = None, coords = None):
        if not cur: cur = self.first
        if not val: val = cur.key
        x_offset, y_offset = self.x_y_offset(pos)       
        if color == None:color = cur.color
        cell_coords= self.cellCoords(pos, coords)
        cell_text = self.cell_text(pos, coords)
        cell_circle = self.cell_dot(pos,coords)
        cell_rect = self.canvas.create_rectangle(cell_coords, fill= color, tag=id)
        cell_text = self.canvas.create_text(cell_text, text=val, font=('Helvetica', textSize),tag = id)
        cell_oval =self.canvas.create_oval(cell_circle, fill="RED", outline="RED", tag = id)
                  
            
        if not arrow:
            if pos%self.LEN_ROW == self.LEN_ROW-1 and pos!=-1 and cur.next:
                self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                   self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset,
                                   self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                  self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset+self.ROW_GAP/2 + self.CELL_HEIGHT/2,
                                    tag=id)
                self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                   self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset + self.ROW_GAP / 2 + self.CELL_HEIGHT / 2,
                                   self.LL_X0 + self.CELL_HEIGHT*2,
                                   self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset+self.ROW_GAP/2 + self.CELL_HEIGHT/2,
                                   tag=id)
                self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2,
                                   self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset + self.ROW_GAP / 2 + self.CELL_HEIGHT / 2,
                                   self.LL_X0 + self.CELL_HEIGHT*2,
                                   self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset + self.ROW_GAP + self.CELL_HEIGHT/2,
                                   arrow=LAST, tag=id)
            elif val == "FIRST" or (cur and cur.next):
                self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                        self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset,
                                        self.LL_X0 + x_offset + self.CELL_WIDTH + self.CELL_GAP,
                                        self.LL_Y0 + self.CELL_HEIGHT // 2 + y_offset,
                                         arrow = LAST,tag = id)
        else:
            self.canvas.create_line(self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                    (self.LL_Y0 - self.CELL_HEIGHT )+ y_offset,
                                    self.LL_X0 + self.CELL_HEIGHT*2 + x_offset,
                                    self.LL_Y0 + y_offset,
                                     arrow = LAST,tag = id)
        
        handler = lambda e: self.setArgument(str(val))
        for item in (cell_rect,cell_text, cell_oval):
            self.canvas.tag_bind(item, '<Button>', handler)
        
        return cur
            
    #creates the node pre-insertion
    def nodeToBeInserted(self, val):
        newNode = self.insert(val)
        return self.createCell(1, '12', val = val, color = newNode.color, arrow = "DOWN", coords = "OTHER")
        
    #creates the initial "node" that indicates the head of the linked list
    def firstPointer(self, next = None):
        self.createCell(0, '10', "FIRST", None, "GRAY" )          
    
        
    ### ANIMATION METHODS###
    
    #returns the first node in list
    def getFirst(self):
        return self.first
            
    #erases old linked list and draws empty list
    def newLinkedList(self):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        self.firstPointer()
        self.first = None
        self.size = 0
        self.cleanUp(callEnviron)
        return self.first
        
    
    # delete a node from the linked list, returning the key
    # pair of the deleted node. If key == None, then just delete
    # the first node. Otherwise, attempt to find and delete
    # the first node containing key
    def delete(self, key=None):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()

        pos = 1
        x, y = self.index(pos)
        arrow = self.canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
    
        callEnviron.add(arrow)
        self.window.update()

        # delete the first node?
        if (not key) or (self.first and key == self.first.key):
            ans = self.first
            if not ans: return None
            self.first = ans.next

            self.wait(1.0)
            callEnviron.add(ans.id)
           
            self.cleanUp(callEnviron)
            return ans.key

        # loop until we hit end, or find key,
        # keeping track of previously visited node
        cur = prev = self.first
        while cur and cur.key != key:
            self.wait(0.7)    
            arrow = (arrow, )
            if (pos-4)%self.LEN_ROW == 0:
                self.moveItemsBy(arrow, (-((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), self.CELL_HEIGHT + self.ROW_GAP))
                
            else:
                self.moveItemsBy(arrow, (self.CELL_WIDTH+ self.CELL_GAP, 0))
            
            pos += 1
            prev = cur
            cur = cur.next            

        # A node with this key isn't on list
        if not cur: 
            self.cleanUp(callEnviron)
            return

        # otherwise remove the node from the list and
        # return the key/data pair of the found node
        prev.next = cur.next
        
        self.wait(1)
      
        
        callEnviron.add(cur.id)
        self.cleanUp(callEnviron)
        return cur.key    
    
 
    #id is used to link the different parts of each node visualization
    def insertElem(self, val, pos=1, id=-1):
        callEnviron = self.createCallEnvironment()
        self.startAnimations()
        newNode = self.nodeToBeInserted(val)
        if id==-1:
            id = self.generateId()
            newNode.id = id           
        self.wait(0.5)
        self.cleanUp(callEnviron)
        return val        
        
    def find(self, key):
        self.startAnimations()
        callEnviron = self.createCallEnvironment()  
        cur = self.first
        pos = 1
        x, y = self.index(pos)
        arrow = self.canvas.create_line(x, y - 40, x, y, arrow="last", fill='red')
        callEnviron.add(arrow)
        
        # go through each Element in the linked list
        while cur:
            self.window.update()

            # if the value is found
            if cur.key == key:
                
                #highlight the box of the node that contains the search key
                x_offset, y_offset = self.x_y_offset(pos)
                cell_outline = self.canvas.create_rectangle(self.LL_X0 + x_offset-5,
                                           self.LL_Y0+y_offset-5,
                                           self.LL_X0 + self.CELL_WIDTH + x_offset+5,
                                           self.LL_Y0 + self.CELL_HEIGHT+y_offset+5, outline = "RED", tag=id)

                callEnviron.add(cell_outline)
                self.wait(1.0)

                # update the display
                self.cleanUp(callEnviron)
                return pos

            # if the value hasn't been found, wait and then move the arrow over one cell
            self.wait(0.7)
            cur = cur.next
            arrow = (arrow, )
            if (pos-4)%self.LEN_ROW == 0: 
                self.moveItemsBy(arrow, (-((self.CELL_WIDTH + self.CELL_GAP)*(self.LEN_ROW-1)), self.CELL_HEIGHT + self.ROW_GAP))
            else: 
                self.moveItemsBy(arrow, (self.CELL_WIDTH + self.CELL_GAP,0))
            pos +=1
            
        self.cleanUp(callEnviron)
        return None

    def display_neatly(self):
        self.canvas.delete("all")
        self.firstPointer()
        cur = self.first
        pos = 1
        while cur:
            val = cur.key
            self.createCell(pos, '12', val, cur)
            cur = cur.next
            pos += 1
        self.window.update()
              
    
    def cleanUp(self, *args, **kwargs): 
        super().cleanUp(*args, **kwargs)
        self.display_neatly()
    
    ### BUTTON FUNCTIONS##
    def clickFind(self):
        val = self.validateArgument()
        if val is None:
            self.setMessage("Input value must be less than 9 characters")
        else:
            result = self.find(val)
            if result != None:
                msg = "Found {}!".format(val)
            else:
                msg = "Value {} not found".format(val)
            self.setMessage(msg)
            
        self.clearArgument()
    
    def clickInsert(self):
        val = self.validateArgument()
        if val is None:
            self.setMessage("Input value must be less than 9 characters")
        elif len(self) >= self.MAX_SIZE:
            self.setMessage("Error! Linked List is already full.")
        else:  
            self.insertElem(val)



    def clickDelete(self):
        val = self.validateArgument()
        if not self.first:
            msg = "ERROR: Linked list is empty"
        elif not val:
            msg = "Input value must be less than 9 characters"
        else: 
            result = self.delete(val)
            if result != None:
                msg = "{} Deleted!".format(val)
            else:
                msg = "Value {} not found".format(val)
        self.setMessage(msg)
        self.clearArgument()
        
    def clickNewLinkedList(self):
        self.canvas.delete('all')
        self.newLinkedList()
    
    def clickGetFirst(self):
        cur = self.getFirst()
        if cur!= None: 
            val = cur.key
            msg = "The first node is {}".format(val)
        else: msg = "ERROR: Linked list is empty"
        self.setMessage(msg)
        self.clearArgument()
    

    def makeButtons(self):
        vcmd = (self.window.register(validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        findButton = self.addOperation(
            "Find", lambda: self.clickFind(), numArguments=1,
            validationCmd=vcmd)
        insertButton = self.addOperation(
            "Insert", lambda: self.clickInsert(), numArguments=1,
            validationCmd=vcmd)
        deleteButton = self.addOperation(
            "Delete", lambda: self.clickDelete(), numArguments=0,
            validationCmd=vcmd)
        newLinkedListButton = self.addOperation(
            "New", lambda: self.clickNewLinkedList(), 
            numArguments = 0, validationCmd =vcmd)
        getFirstButton = self.addOperation(
            "Get First", lambda: self.clickGetFirst(), numArguments = 0,
            validationCmd=vcmd)
        self.addAnimationButtons()
        return [findButton, insertButton, deleteButton, newLinkedListButton, getFirstButton]        

    
    # validate text entry
    def validateArgument(self):
        text = self.getArgument()
        if text:
            if text.isdigit():
                val = int(text)
                if val< 100000000: return val
            elif len(text)<9: return text
            
#allow letters or numbers to be typed in                  
def validate(action, index, value_if_allowed,
            prior_value, text, validation_type, trigger_type, widget_name):
    if not(value_if_allowed.isdigit()):
        for i in value_if_allowed:
            if not 65<=ord(i)<=122 and i not in "0123456789": return False
    return True
   
if __name__ == '__main__':
    ll = LinkedList()
    ll.runVisualization()

'''
Useful Links:
http://effbot.org/zone/tkinter-complex-canvas.htm
https://mail.python.org/pipermail/python-list/2000-December/022013.html
'''

# Just confirming this is working - Etti