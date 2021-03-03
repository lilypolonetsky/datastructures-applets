from tkinter import *
import random
import sys

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
        super().__init__(RECT=(0, 0, canvasWidth, canvasHeight), title=title,
                         canvasWidth=canvasWidth, canvasHeight=canvasHeight, 
                         **kwargs)
        self.buttons = self.makeButtons()
        self.title = title

   def newTree(self):
      self.emptyTree()

   def randomFill(self, numNodes):
      callEnviron = self.createCallEnvironment()

      # empty the tree
      self.emptyTree()

      #randomly generate a tree
      nums = list(range(1, 99))
      random.shuffle(nums)
      while self.size < numNodes and nums:
         num = nums.pop()
         self.insert(nums.pop(), animation=False)

      self.cleanUp(callEnviron)

   def insert(self, key, animation=True):
      callEnviron = self.createCallEnvironment()
      self.startAnimations()

      # create arrow
      if animation:
         coords = self.calculateCoordinates(None,0,Child.RIGHT)
         arrow = self.createArrow(coords)
         callEnviron |= set(arrow)

      root, flag = self.__insert(self.getRoot(), key, animation=animation, arrow=arrow)
      self.setRoot(root)
      if animation:
         self.moveArrow(arrow, root)
      self.redrawNodes()
      self.drawAllLines()
      self.allDisplayHeight()

      self.cleanUp(callEnviron)
      return flag

   def __insert(self, node, key,animation=True, arrow=None):
      callEnviron = self.createCallEnvironment()
      self.startAnimations()

      # empty subtree
      if node is None:
         insertedNode = self.createNode(key, parent=None, addToArray=False)
         self.cleanUp(callEnviron)
         return insertedNode, True
      
      # key already exists in tree
      if key == node.getKey():
         self.setMessage(
               "Error! Key" + str(key) + " already exists in the tree")
         self.cleanUp(callEnviron)
         return node, False

      # don't insert past MAX_LEVEL
      if self.getLevel(node) == self.MAX_LEVEL-1:
         if animation:
            self.setMessage(
               "Error! Cannot insert at level " + str(self.MAX_LEVEL+1) + 
               " or below")
         self.cleanUp(callEnviron)
         return node, False
          
      # Does the key belong in left subtree?
      elif key < node.getKey():
         # insert on left and update the left link
         newLeft, flag = self.__insert(self.getLeftChild(node), key, animation=animation, arrow=arrow)
         self.setLeftChild(node, newLeft)

         if animation:
            self.restoreNodesPosition([newLeft], arrow=arrow, sleepTime=.01)
            self.redrawLines()
            self.wait(0.2)

          # If insert made node left heavy
         if self.heightDiff(node) > 1:
            leftChild = self.getLeftChild(node)
            if leftChild.getKey() < key:                             
               self.setLeftChild(node, self.rotateLeft(leftChild, animation=animation))  
                   
            node = self.rotateRight(node, animation=animation)                                           
          
      # Otherwise key belongs in right subtree
      else:
         # Insert it on right and update the right link 
         newRight, flag = self.__insert(self.getRightChild(node), key, animation=animation, arrow=arrow)
         self.setRightChild(node, newRight)
         
         if animation:
            self.restoreNodesPosition([newRight], arrow=arrow, sleepTime=.01)
            self.redrawLines()  
            self.wait(0.2)
         
         # If insert made node right heavy
         if self.heightDiff(node) < -1:                     
            rightChild = self.getRightChild(node)
            if key < rightChild.getKey():
               self.setRightChild(node, self.rotateRight(rightChild, animation= animation))
                   
            node = self.rotateLeft(node, animation=animation)
      self.cleanUp(callEnviron)
      return node, flag       # Return the updated node & insert flag

   def __drawHeight(self, node):
      height = self.getHeight(node)
      x, y = self.calculateCoordinates(self.getParent(node), self.getLevel(node), self.getChildDirection(node))

      return self.canvas.create_text(x, y- 1.5*self.CIRCLE_SIZE, text = str(height), tags = (node.tag, "height"))

   # override height from BinaryTreeBase.py
   def getHeight(self, node):
        if not node: return 0

        rightChild = self.getRightChild(node)
        leftChild = self.getLeftChild(node)

        return max(self.getHeight(rightChild), self.getHeight(leftChild)) + 1

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
      val = self.validArgument()
      if val:
         self.randomFill(val)
         self.window.update()
      self.clearArgument()

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
    for arg in sys.argv[1:]:
        tree.setArgument(arg)
        tree.clickInsert()
    tree.stopAnimations()
    tree.runVisualization()
