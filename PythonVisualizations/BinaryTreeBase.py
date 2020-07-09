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

   WIDTH = 1000
   HEIGHT = 400

   CIRCLE_SIZE = 15
   NODE_X_GAP = 400
   NODE_Y_GAP = 75
   ROOT_X0 = WIDTH/2
   ROOT_Y0 = CIRCLE_SIZE + 5
   MAX_LEVEL = 5

   ARROW_HEIGHT = 30

   def __init__(self, title="Tree", width = WIDTH, height = HEIGHT, **kwargs):
      super().__init__(title=title, canvasWidth= width, canvasHeight= height, **kwargs)
      
      self.title = title
      self.width = width
      self.height = height

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
      root = self.nodes[0]
      index = -1

      count = 0                           # track how many items we encountered
      i = 0                               # track what index we are at
      while count < self.size:
         if self.nodes[i]:                # does a node exist in this position?
            if self.nodes[i] is node:     # did we find the node?
               index = i
               break
            count += 1                    # encountered a node
         i += 1                           # move to the next index

      return index

   # return's the node's left child's index
   def getLeftChildIndex(self, node):
      nodeIndex = self.getIndex(node)
      childIndex = 2*nodeIndex + 1

      if childIndex >= self.maxElems: return -1
      else: return childIndex

   # return's the node's right child's index
   def getRightChildIndex(self, node):
      nodeIndex = self.getIndex(node)
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
   def getRoot(self, node):
      return self.nodes[0]

   # returns True if node is the root
   def isRoot(self, node):
      return self.nodes[0] is node

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

   # returns the node's parent
   def getParent(self, node):
      # is it the root?
      if self.isRoot(node): return None

      # get node's index
      index = self.getIndex(node)

      parentIndex = (index - 1) // 2
      return self.nodes[parentIndex]

   # returns the level of the node
   def getLevel(self, node):
      if self.isRoot(node): return 0
      else: return self.getLevel(self.getParent(node)) + 1

   def getHeight(self, node):
      if not node: return -1

      rightChild = self.getRightChild(node)
      leftChild = self.getLeftChild(node)

      return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

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
   def moveArrow(self, arrow, node, numSteps= 5):
      # was a node passed in?
      if isinstance(node, Node):
            toPos = (node.coords[0], node.coords[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
            node.coords[0], node.coords[1] - self.CIRCLE_SIZE)
      # were the coords passed?
      elif isinstance(node, tuple):
            toPos = (node[0], node[1] - self.CIRCLE_SIZE - self.ARROW_HEIGHT,
            node[0], node[1] - self.CIRCLE_SIZE)

      self.moveItemsTo(arrow, (toPos,), steps = numSteps)

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
      x1 = node.coords[0]
      y1 = node.coords[1] +self.CIRCLE_SIZE

      # where would the child be drawn?
      level = self.getLevel(node)+1
      x2, y2 = self.calculateCoordinates(node, level, Child.LEFT)
      x3, y3 = self.calculateCoordinates(node, level, Child.RIGHT)
      y2 -= self.CIRCLE_SIZE
      y3 -= self.CIRCLE_SIZE

      return [(x1, y1, x2, y2), (x1, y1, x3, y3)]

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

   # highlight the value associated with the node
   def highlightValue(self, node, color="red"):
      self.canvas.itemconfig(node.drawable.display_val, fill=color)

   # unhighlight the value associated with the node
   def unHighlightValue(self, node):
      self.canvas.itemconfig(node.drawable.display_val, fill="black")

   # draws the circle and the key value
   def createNodeShape(self, x, y, key, tag):
      circle = self.canvas.create_circle(x, y, self.CIRCLE_SIZE, tag = tag)
      circle_text = self.canvas.create_text(x,y, text=key, font=self.VALUE_FONT, tag = tag)

      # get rid of the none shape that was in its spot
      items = self.canvas.find_overlapping(*(self.canvas.coords(circle)))
      if len(items) >= 5:
         self.canvas.delete(items[-3])
         self.canvas.delete(items[-4])
         self.canvas.delete(items[-5])
         self.canvas.update()

      return circle, circle_text

   # creates the none shape that nodes will point to
   # line coords should be the coords of the line that points to none
   def createNoneShape(self, node, level, lineCoords, direction, tag):
      y = lineCoords[3] + (self.CIRCLE_SIZE // 2)
      xCoord = self.calculateCoordinates(node, level+1, direction)[0]

      shrinkFactor = self.CIRCLE_SIZE // 3

      coords1 = ( xCoord-self.CIRCLE_SIZE, y, 
                  xCoord+self.CIRCLE_SIZE, y)
      coords2 = (  shrinkFactor + coords1[0], coords1[1] + shrinkFactor,
                  -shrinkFactor + coords1[2], coords1[3] + shrinkFactor)
      coords3 = (  shrinkFactor + coords2[0], coords2[1] + shrinkFactor, 
                  -shrinkFactor + coords2[2], coords2[3] + shrinkFactor)

      self.canvas.create_line(coords1, tag = tag)
      self.canvas.create_line(coords2, tag = tag)
      self.canvas.create_line(coords3, tag = tag)

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
      drawableObj = drawable(key, self.canvas.itemconfigure(circle, 'fill'), *(circle, circle_text))
      
      # create the Node object
      node = Node(drawableObj, coords, tag)

      # increment size
      self.size += 1

      # add the node object to the internal representation
      self.setNode(node, direction, parent)

      # draw the lines
      leftLine, rightLine = self.calculateLineCoordinates(node)
      self.canvas.create_line(*leftLine, tags = (tag, "left line"))
      self.canvas.create_line(*rightLine, tags = (tag, "right line"))

      # draw the none symbols
      self.createNoneShape(node, level, leftLine, Child.LEFT, tag)
      self.createNoneShape(node, level, rightLine, Child.RIGHT, tag)

      return node 

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
   def setNode(self, child, direction = None, parent = None):
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

   # delete the node's drawing and remove it from the array represenation
   def removeNode(self, node):
      self.canvas.delete(node.tag)
      self.nodes[self.getIndex(node)] = None
      self.nElems -= 1

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