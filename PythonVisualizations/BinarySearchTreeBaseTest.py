
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

class BinarySearchTree(BinaryTreeBase):
   def __init__(self, x0=0, y0=0, x1=800, y1=400):
      super().__init__(x0, y0, x1, y1)
      self.buttons = self.makeButtons()
      
   def example(self):
      self.canvas.delete("all")
      callEnviron = self.createCallEnvironment()
      self.startAnimations()

      node1 = self.createNode(50, None)
      node2 = self.createNode(40, node1, Child.LEFT)
      node3 = self.createNode(60, node1, Child.RIGHT)
      node4 = self.createNode(70, node3, Child.RIGHT)
      node5 = self.createNode(80, node4, Child.RIGHT)

      self.setMessage('Create node 30')
      self.wait(0.5)
      node6 = self.createNode(30, node2, Child.LEFT)

      self.setMessage('Create node 35')
      self.wait(0.5)
      node7 = self.createNode(35, node6, Child.RIGHT)
      
      self.setMessage('Create node 37')
      self.wait(0.5)
      node8 = self.createNode(37, node7, Child.RIGHT)

      self.setMessage('Highlight left child link of root')
      self.wait(0.5)
      highlight2 = self.createHighlightedLine(node2)

      self.setMessage('Highlight right child link of root')
      self.wait(0.5)
      highlight3 = self.createHighlightedLine(node3)
      
      self.setMessage('Remove left highlight link')
      self.wait(0.5)
      self.canvas.delete(highlight2)
      
      self.setMessage('Remove right highlight link')
      self.wait(0.5)
      self.canvas.delete(highlight3)
      self.wait(0.5)

      self.setMessage('Highlight root node')
      self.wait(0.5)
      highlight1 = self.createHighlightedCircle(node1, color='red')
      self.setMessage('Highlight root value')
      self.wait(0.5)
      highlight2 = self.createHighlightedValue(node1, color='green')
      self.wait(0.5)
      self.cleanUp(callEnviron)
      
   def makeButtons(self):
      vcmd = (self.window.register(numericValidate),
               '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
      exampleButton = self.addOperation("Fill example", self.example)
      newButton = self.addOperation("New", self.emptyTree)
      self.addAnimationButtons()
      return [exampleButton, newButton]
   
if __name__ == '__main__':
    random.seed(3.14159)  # Use fixed seed for testing consistency
    tree = BinaryTree()

    tree.runVisualization()
