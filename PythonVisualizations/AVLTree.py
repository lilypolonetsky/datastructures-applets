from tkinter import *
import time, random

try:
    from drawable import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class AVLTree(BinaryTreeBase):
   def __init__(self, canvasWidth=800, canvasHeight=400, title="AVL Tree", **kwargs):
        super().__init__(0, 0, canvasWidth, canvasHeight, title=title,
                         canvasWidth=canvasWidth, canvasHeight=canvasHeight, 
                         **kwargs)
        self.buttons = self.makeButtons()
        self.title = title

   def newTree(self):
      self.emptyTree()

   def randomFill(self, numNodes):
      pass

   def insert(self, key):
      callEnviron = self.createCallEnvironment()
      self.startAnimations()

      root, flag = self.__insert(self.getRoot(), key)
      self.setRoot(root)
      self.redrawNodes()
      self.drawAllLines()
      self.allDisplayHeight()

      self.cleanUp(callEnviron)
      return flag

   def __insert(self, node, key):
      callEnviron = self.createCallEnvironment()
      self.startAnimations()

      # empty subtree
      if node is None:
         insertedNode = self.createNode(key, parent=None, addToArray=False)
         self.cleanUp(callEnviron)
         return insertedNode, True
      
      # key already exists in tree
      if key == node.getKey():
         self.cleanUp(callEnviron)
         return node, False
          
      # Does the key belong in left subtree?
      elif key < node.getKey():
         # insert on left and update the left link
         newLeft, flag = self.__insert(self.getLeftChild(node), key)
         self.setLeftChild(node, newLeft)
         self.restoreNodesPosition([newLeft], sleepTime=.01)
         self.redrawLines()
         print(node,"left is", newLeft)  

          # If insert made node left heavy
         if self.heightDiff(node) > 1:
            leftChild = self.getLeftChild(node)
            if leftChild.getKey() < key:                             # If inside grandchild inserted,
               self.setLeftChild(node, self.rotateLeft(leftChild))   # then raise grandchild   
                   
            node = self.rotateRight(                           # Correct left heavy tree by
               node)                                           # rotating right around this node
          
      # Otherwise key belongs in right subtree
      else:
         # Insert it on right and update the right link 
         newRight, flag = self.__insert(self.getRightChild(node), key)
         self.setRightChild(node, newRight)
         self.restoreNodesPosition([newRight], sleepTime=.01)
         self.redrawLines()
         print(node,"right is", newRight)     
         
         # If insert made node right heavy
         if self.heightDiff(node) < -1:                     
            rightChild = self.getRightChild(node)
            if key < rightChild.getKey():                               # If inside grandchild inserted,
               self.setRightChild(node, self.rotateRight(rightChild))   # then raise grandchild
                   
            node = self.rotateLeft( # Correct right heavy tree by
               node)          # rotating left around this node
       
      return node, flag       # Return the updated node & insert flag

   def __drawHeight(self, node):
      height = self.getHeight(node)
      x, y = self.calculateCoordinates(self.getParent(node), self.getLevel(node), self.getChildDirection(node))

      return self.canvas.create_text(x, y- 1.5*self.CIRCLE_SIZE, text = str(height), tags = (node.tag, "height"))

   # display the height of the given node
   def __displayHeight(self, left, right):
      if left: 
         self.__drawHeight(left)
         self.__displayHeight(self.getLeftChild(left), self.getRightChild(left))
      if right: 
         self.__drawHeight(right)
         self.__displayHeight(self.getLeftChild(right), self.getRightChild(right))

   def allDisplayHeight(self):
      cur = self.getRoot()
      if cur:
         self.__drawHeight(cur)
         left = self.getLeftChild(cur)
         right = self.getRightChild(cur)
         self.__displayHeight(left, right)

   def redrawNodes(self):
      for node in self.nodes:
         if node:
            self.removeNodeDrawing(node)
            node.coords = self.calculateCoordinates(self.getParent(node), self.getLevel(node), self.getChildDirection(node))
            self.createNodeShape(node.coords[0], node.coords[1], node.getKey(), node.tag)
            self.redrawLines()
         
   def validArgument(self):
        entered_text = self.getArgument()
        if entered_text and entered_text.isdigit():
            val = int(entered_text)
            if val < 100:
                return val
            else:
                self.setMessage("Input value must be an integer from 0 to 99.")

   def clickInsert(self):
        val = self.validArgument()
        if val:
            self.insert(val)
            self.window.update()
        self.clearArgument()

   def clickRandomFill(self):
      pass

   def makeButtons(self):
      vcmd = (self.window.register(numericValidate),
               '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
      newTreeButton = self.addOperation("New Tree", lambda: self.newTree())
      randomFillButton = self.addOperation(
         "Random Fill", lambda: self.clickRandomFill(), numArguments=1,
         validationCmd= vcmd)
      insertButton = self.addOperation(
         "Insert", lambda: self.clickInsert(), numArguments=1,
         validationCmd= vcmd)
      #this makes the pause, play and stop buttons 
      self.addAnimationButtons()
      return [insertButton,]

if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = AVLTree()

    tree.runVisualization()