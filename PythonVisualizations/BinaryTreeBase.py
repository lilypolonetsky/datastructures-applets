from tkinter import *
import time, random
from enum import Enum

try:
    from drawable import *
    from VisualizationApp import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *

class Child(Enum):
    LEFT = 0
    RIGHT = 1

class Node(object):
   def __init__(self, drawable, coords, tag):
      self.drawable = drawable
      self.coords = coords
      self.tag = tag

   def getKey(self):
      return self.drawable.val

   def setKey(self, k):
      self.drawable.val = k

   def __str__(self):
      return "{" + str(self.getKey()) + "}"

class BinaryTreeBase(VisualizationApp):
   # -------- CONSTANTS ------------------
   FONT_SIZE = '16'
   VALUE_FONT = ('Helvetica', FONT_SIZE)
   FOUND_FONT = ('Helvetica', FONT_SIZE)

   CIRCLE_SIZE = 15

   def __init__(self, title="Tree", CIRCLE_SIZE = 15, 
               ROOT_X0 = 500, ROOT_Y0 = CIRCLE_SIZE + 10, 
               NODE_X_GAP = 400, NODE_Y_GAP = 75,
               ARROW_HEIGHT = 30,MAX_LEVEL = 5, **kwargs):
      super().__init__(title=title, **kwargs)
      
      self.title = title

      self.CIRCLE_SIZE = CIRCLE_SIZE         # size of each node
      self.ROOT_X0 = ROOT_X0                 # root's x position
      self.ROOT_Y0 = ROOT_Y0                 # root's y position
      self.NODE_X_GAP = NODE_X_GAP           # the horizontal gap between each node (modified for each level)
      self.NODE_Y_GAP = NODE_Y_GAP           # the vertical gap between each node (modified for each level)
      self.ARROW_HEIGHT = ARROW_HEIGHT       # the arrow's height
      self.MAX_LEVEL = MAX_LEVEL             # the maximum level that the tree can reach

      # tree will be stored in array
      # root will be index 0
      # root's left child will be index 1, root's right child will be index 2 etc
      self.maxElems = 2 ** self.MAX_LEVEL     
      self.nodes = [None] * self.maxElems
      self.size = 0

      self.prevId = -1

   # --------- ACCESSOR METHODS ---------------------------

   # returns the index of the node
   def getIndex(self, node):
      for i in range(len(self.nodes)):
         if self.nodes[i] is node:
            return i
      
      return -1

   # return's the node's left child's index
   def getLeftChildIndex(self, node):
      nodeIndex = self.getIndex(node)
      childIndex = 2*nodeIndex + 1

      if childIndex >= self.maxElems: return -1
      else: return childIndex

   # return's the node's right child's index
   def getRightChildIndex(self, node):
      nodeIndex = self.getIndex(node)
      if nodeIndex == -1: return -1
      childIndex = 2*nodeIndex + 2

      if childIndex >= self.maxElems: return -1
      else: return childIndex

   # returns the node's left child
   def getLeftChild(self, node):
      childIndex = self.getLeftChildIndex(node)

      if childIndex != -1: return self.nodes[childIndex]
      else: return None

   # returns the node's right child
   def getRightChild(self, node):
      childIndex = self.getRightChildIndex(node)

      if childIndex != -1: return self.nodes[childIndex]
      else: return None

   # returns the root node
   def getRoot(self):
      return self.nodes[0]

   # returns True if node is the root
   def isRoot(self, node):
      return self.nodes[0] is node

   # returns True if the node has no children, false otherwise
   def isLeaf(self, node):
      # if neither a right or left child exists
      if not (self.getRightChild(node) or self.getLeftChild(node)):
         return True
      else: return False

   # returns True if node is a right child, false otherwise
   def isRightChild(self, node):
      # is it the root?
      if self.isRoot(node): return False

      # right child will always be an even index
      index = self.getIndex(node)
      return index % 2 == 0

   # returns True if node is a left child, false otherwise
   def isLeftChild(self, node):
      # left child will always be an odd index
      index = self.getIndex(node)
      return index % 2 == 1

   # returns enum if node is right or left child
   # returns None if node is the root
   def getChildDirection(self, node):
      if self.isRoot(node):
            direction = None
      elif self.isRightChild(node):
         direction = Child.RIGHT
      else:
         direction = Child.LEFT
      return direction

   # returns the node's parent
   def getParent(self, node):
      # is it the root?
      if self.isRoot(node): return None

      parentIndex = self.getParentIndex(node)
      return self.nodes[parentIndex]

   def getParentIndex(self, node):
      # get node's index
      index = self.getIndex(node)
      return (index - 1) // 2

   # returns the level of the node
   def getLevel(self, node):
      if self.isRoot(node): return 0
      else: return self.getLevel(self.getParent(node)) + 1

   def getHeight(self, node):
      if not node: return -1

      rightChild = self.getRightChild(node)
      leftChild = self.getLeftChild(node)

      return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

   # returns the line pointing to the node
   def getLine(self, node):
      # get all the items with the node's tag
      nodeFamily = set(self.canvas.find_withtag(node.tag))
      # get all the line
      lines = set(self.canvas.find_withtag("line"))

      return (lines & nodeFamily).pop()
      
   # returns a tuple of the left and right child of node
   def getChildren(self, node):
      return self.getLeftChild(node), self.getRightChild(node)

   # returns a list of all the nodes that descend from node
   def getAllDescendants(self, node):
      if not node: return []

      children = self.getChildren(node)
      returnList = []
      if children[0]: returnList.append(children[0])
      if children[1]: returnList.append(children[1])

      return returnList + self.getAllDescendants(children[0]) + self.getAllDescendants(children[1])
      

   # ----------- DRAWING METHODS -------------------
   
   # monkey patching to allow for circles to be drawn easier
   def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
   Canvas.create_circle = _create_circle

   # Create an arrow to point at a node
   def createArrow(self, node):
      arrow = self.canvas.create_line(node.coords[0], node.coords[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
                                   node.coords[0], node.coords[1] - self.CIRCLE_SIZE, arrow="last", fill='red')
      return (arrow, )

   # move the arrow to point above the node
   def moveArrow(self, arrow, node, numSteps= 5, sleepTime=0.1):
      # was a node passed in?
      if isinstance(node, Node):
            toPos = (node.coords[0], node.coords[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
            node.coords[0], node.coords[1] - self.CIRCLE_SIZE)
      # were the coords passed?
      elif isinstance(node, tuple):
            toPos = (node[0], node[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
            node[0], node[1] - self.CIRCLE_SIZE)

      self.moveItemsTo(arrow, (toPos,), steps = numSteps, sleepTime=sleepTime)

   # calculate the coordinates for the node shape
   def calculateCoordinates(self, parent, level, childDirection):
        if level == 0:
            return self.ROOT_X0, self.ROOT_Y0
        elif childDirection == Child.LEFT:
            return parent.coords[0] - 1/2**level* (self.NODE_X_GAP-self.CIRCLE_SIZE), self.ROOT_Y0+level* self.NODE_Y_GAP
        else:
            return parent.coords[0] + 1/2**level* (self.NODE_X_GAP-self.CIRCLE_SIZE), self.ROOT_Y0+level* self.NODE_Y_GAP

   # calculate the coordinates for the line attached to the node
   def calculateLineCoordinates(self, node):
      # get node's parent
      parent = self.getParent(node)

      x1 = parent.coords[0]
      y1 = parent.coords[1] +self.CIRCLE_SIZE

      return (x1, y1, node.coords[0], node.coords[1])

   # highlight the left line of the node
   def highlightLeftLine(self, node, color = "red"):
      # get all the items with the node's tag
      nodeFamily = set(self.canvas.find_withtag(node.tag))
      # get all the lines that are left
      lines = set(self.canvas.find_withtag("left line"))

      line = (lines & nodeFamily).pop()

      self.canvas.itemconfig(line, fill=color)

   # unhighlight the left line of the node
   def unHighlightLeftLine(self, node):
      # get all the items with the node's tag
      nodeFamily = set(self.canvas.find_withtag(node.tag))
      # get all the lines that are left
      lines = set(self.canvas.find_withtag("left line"))

      line = (lines & nodeFamily).pop()

      self.canvas.itemconfig(line, fill="black")

   # highlight the right line of the node
   def highlightRightLine(self, node, color="red"):
      # get all the items with the node's tag
      nodeFamily = set(self.canvas.find_withtag(node.tag))
      # get all the lines that are left
      lines = set(self.canvas.find_withtag("right line"))

      line = (lines & nodeFamily).pop()

      self.canvas.itemconfig(line, fill= color)

   # unhighlight the right line of the node
   def unHighlightRightLine(self, node):
      # get all the items with the node's tag
      nodeFamily = set(self.canvas.find_withtag(node.tag))
      # get all the lines that are left
      lines = set(self.canvas.find_withtag("right line"))

      line = (lines & nodeFamily).pop()

      self.canvas.itemconfig(line, fill="black")

   # highlight the circle associated with the node
   def highlightCircle(self, node, color="red"):
      self.canvas.itemconfig(node.drawable.display_shape, outline=color)

   # unhighlight the circle associated with the node
   def unHighlightCircle(self, node):
      self.canvas.itemconfig(node.drawable.display_shape, outline="black")

   # creates a highlighted value on top of the normal value associated with the node
   def createHighlightedValue(self, node, color="green"):
      return self.canvas.create_text(node.coords[0], node.coords[1], text=node.getKey(), font=self.VALUE_FONT,
                                               fill=color)

   # highlight the value associated with the node
   def highlightValue(self, node, color="red"):
      self.canvas.itemconfig(node.drawable.display_val, fill=color)

   # unhighlight the value associated with the node
   def unHighlightValue(self, node):
      self.canvas.itemconfig(node.drawable.display_val, fill="black")

   # draws the circle and the key value
   def createNodeShape(self, x, y, key, tag, color= drawable.palette[2]):
      circle = self.canvas.create_circle(x, y, self.CIRCLE_SIZE, tag = tag, fill=color, outline='')
      circle_text = self.canvas.create_text(x,y, text=key, font=self.VALUE_FONT, tag = tag)

      return circle, circle_text

   def restoreNodesPosition(self, moveItems, sleepTime=0.1):
      # get the coords for the node to move to
      moveCoords = []
      for node in moveItems:
         node.coords = self.calculateCoordinates(self.getParent(node),self.getLevel(node), self.getChildDirection(node))
         moveCoords.append(( node.coords[0]-self.CIRCLE_SIZE, node.coords[1]-self.CIRCLE_SIZE,
                              node.coords[0]+self.CIRCLE_SIZE, node.coords[1]+self.CIRCLE_SIZE))
      
      moveItemsTags = [node.tag for node in moveItems]
      self.moveItemsTo(moveItemsTags, moveCoords, sleepTime=sleepTime)

      # fix the lines
      for node in moveItems:
         # get the coordinates of where it should be
         lineCoords = self.calculateLineCoordinates(node)
         # get the line
         line = self.getLine(node)
         
         self.canvas.coords(line, lineCoords)

   # ----------- SETTER METHODS --------------------
   
   # create a Node object with key and parent specified
   # parent should be a Node object
   def createNode(self, key, parent = None, direction = None):
      # calculate the level
      if not parent: level = 0
      else: level = self.getLevel(parent) + 1                                                
      
      # calculate the coords
      coords = self.calculateCoordinates(parent, level, direction)
      x,y = coords

      # generate a tag
      tag = self.generateTag()

      # create the shape and text
      circle, circle_text = self.createNodeShape(x, y, key, tag)
      
      # create the drawable object
      drawableObj = drawable(key, self.canvas.itemconfigure(circle, 'fill')[-1], *(circle, circle_text))
      
      # create the Node object
      node = Node(drawableObj, coords, tag)

      # increment size
      self.size += 1

      # add the node object to the internal representation
      self.setChildNode(node, direction, parent)

      # draw the lines
      if parent:
         lineCoords = self.calculateLineCoordinates(node)
         line = self.canvas.create_line(*lineCoords, tags = (tag, "line"))
         # the line should be beneath the circle
         self.canvas.tag_lower(line)

      return node 

   def setRoot(self, node):
      self.nodes[0] = node

   # set the node's left child
   def setLeftChild(self, node, child):
      index = self.getLeftChildIndex(node)
      if index != -1:
         self.nodes[index] = child
         return index
      else:
         return -1

   # set the node's right child
   def setRightChild(self, node, child):
      index = self.getRightChildIndex(node)
      if index != -1:
         self.nodes[index] = child
         return index
      else:
         return -1

   # set the node's child
   # returns the index where the child is stored
   def setChildNode(self, child, direction = None, parent = None):
      if not parent:
         self.nodes[0] = child
         return 0

      if direction == Child.LEFT:
         return self.setLeftChild(parent, child)
      else:
         return self.setRightChild(parent, child)

   def generateTag(self):
        self.prevId+=1
        return "item" + str(self.prevId)

   # remove the tree's drawing
   # empty the tree's data
   def emptyTree(self):
      self.canvas.delete("all")
      self.size = 0
      self.nodes = [None] * (2**self.MAX_LEVEL)

   def removeNodeInternal(self, node):
      self.nodes[self.getIndex(node)] = None
      self.size -= 1

    # rotate the node left in the array representation and animate it
    # RETURN TO FIX
   def rotateLeft(self, node):
      pass

   # rotate the nodes right in the drawing and in the array representation
   # RETURN TO FIX
   def rotateRight(self, node):
      pass

   # ----------- TESTING METHODS --------------------
   
   def inOrderTraversal(self, cur):
      if cur:
         self.inOrderTraversal(self.getLeftChild(cur))
         print(" " + str(cur), end="")
         self.inOrderTraversal(self.getRightChild(cur))

   def printTree(self, indentBy=4):
      self.__pTree(self.nodes[0], "ROOT:  ", "", indentBy)

   def __pTree(self, node, nodeType, indent, indentBy=4):
      if node:
         self.__pTree(self.getRightChild(node), "RIGHT:  ", indent + " " * indentBy, indentBy)
         print(indent + nodeType, node)
         self.__pTree(self.getLeftChild(node), "LEFT:  ", indent + " " * indentBy, indentBy)