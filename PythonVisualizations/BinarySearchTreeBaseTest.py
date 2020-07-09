
from tkinter import *
import random

try:
    from drawable import *
    from VisualizationApp import *
    from BinaryTreeBase import *
except ModuleNotFoundError:
    from .drawable import *
    from .VisualizationApp import *
    from .BinaryTreeBase import *

class BinaryTree(BinaryTreeBase):
   def __init__(self):
      super().__init__()
      self.buttons = self.makeButtons()
      
   def insert(self):
      insertCallEnviron = self.createCallEnvironment()
      self.startAnimations()

      node1 = self.createNode(50, None)
      node2 = self.createNode(40, node1, Child.LEFT)
      node3 = self.createNode(60, node1, Child.RIGHT)
      node4 = self.createNode(70, node3, Child.RIGHT)
      node5 = self.createNode(80, node4, Child.RIGHT)

      self.wait(0.5)
      node6 = self.createNode(30, node2, Child.LEFT)
      self.wait(0.5)
      node7 = self.createNode(35, node6, Child.RIGHT)
      self.wait(0.5)
      node8 = self.createNode(37, node7, Child.RIGHT)

      self.highlightLeftLine(node1)
      self.wait(0.5)
      self.unHighlightLeftLine(node1)
      self.wait(0.5)
      self.highlightRightLine(node2)
      self.wait(0.5)
      self.unHighlightRightLine(node2)

      self.highlightCircle(node1)
      self.highlightValue(node1)
      self.wait(0.5)
      self.unHighlightCircle(node1)
      self.unHighlightValue(node1)
      
   def makeButtons(self):
      vcmd = (self.window.register(numericValidate),
               '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
      insertButton = self.addOperation(
         "Insert", lambda: self.insert(), numArguments=1,
         validationCmd= vcmd)
      self.addAnimationButtons()
      return [ 
               insertButton]
   
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = BinaryTree()

    tree.runVisualization()